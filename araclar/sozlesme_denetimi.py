# -*- coding: utf-8 -*-
"""AI modül sözleşmesi denetleyicisi (docs/ai-modul-sozlesmesi.md).

Kullanım:  python araclar/sozlesme_denetimi.py moduller/<modul_adi> [moduller/<baska> ...]
Çıkış kodu: 0 = hepsi geçti · 1 = en az bir HATA var. UYARI'lar çıkış kodunu etkilemez.

İki aşama:
  1) Durağan: klasör düzeni, MODUL_BILGISI, dosya boyutları ve SHA-256, yasaklı içe aktarma ve çağrılar (AST ile;
     `import numpy as n`, `from os import system` gibi takma adlar çözülür).
  2) Çalıştırma: modül ağ / alt süreç kafesi içinde içe aktarılır, sentetik girdiyle predict() İKİ kez çağrılır;
     Predictor() ve predict() sırasında dosyaya yazma da engellenir. Dönüş biçimi, katı JSON, belirlenimcilik ve süre
     denetlenir. Modülün fırlattığı her hata denetleyiciyi çökertmez, HATA olarak raporlanır.

Bu bir kural kapısıdır, güvenlik kafesi değildir: kasıtlı atlatma ekip incelemesinde yakalanır (docs/entegrasyon.md).
"""
from __future__ import annotations

import ast
import builtins
import hashlib
import importlib.util
import io
import json
import math
import os
import shutil
import socket
import subprocess
import sys
import tempfile
import time
from pathlib import Path

ZORUNLU_BILGI = ("ad", "baslik", "surum", "girdi_turu", "etiketler", "yazarlar", "model_dosyalari")
GIRDI_TURLERI = ("goruntu", "ses", "tablo")
AZAMI_AGIRLIK_MB = 95
AZAMI_SURE_SN = 10.0
AZAMI_YUKLEME_SN = 30.0

YASAK_ICE_AKTARMA = {
    "requests": "ağ erişimi", "urllib": "ağ erişimi", "http": "ağ erişimi", "httpx": "ağ erişimi", "aiohttp": "ağ erişimi",
    "socket": "ağ erişimi", "paho": "MQTT / ağ", "ftplib": "ağ erişimi", "smtplib": "ağ erişimi",
    "subprocess": "başka program çalıştırma", "tkinter": "pencere", "serial": "seri port", "sounddevice": "mikrofon",
    "pyaudio": "mikrofon", "uvicorn": "sunucu açma", "flask": "sunucu açma", "fastapi": "sunucu açma",
}
# Tam adlarla: takma adlar (`import numpy as np`, `from os import system`) denetimden önce bu adlara çözülür.
YASAK_CAGRI = {
    "sys.exit": "uygulamayı kapatır", "os._exit": "uygulamayı kapatır", "exit": "uygulamayı kapatır", "quit": "uygulamayı kapatır",
    "os.system": "başka program çalıştırma", "os.popen": "başka program çalıştırma", "os.startfile": "başka program çalıştırma",
    "os.execv": "başka program çalıştırma", "os.execve": "başka program çalıştırma", "os.execl": "başka program çalıştırma",
    "os.execvp": "başka program çalıştırma", "os.spawnv": "başka program çalıştırma", "os.spawnl": "başka program çalıştırma",
    "os.posix_spawn": "başka program çalıştırma",
    "eval": "kod çalıştırma", "exec": "kod çalıştırma", "compile": "kod çalıştırma",
    "__import__": "adı gizlenmiş içe aktarma", "importlib.import_module": "adı gizlenmiş içe aktarma",
    "cv2.VideoCapture": "kamera", "cv2.imshow": "pencere", "cv2.namedWindow": "pencere", "cv2.waitKey": "pencere",
    "cv2.imwrite": "dosyaya yazma", "numpy.save": "dosyaya yazma", "numpy.savez": "dosyaya yazma",
    "numpy.savez_compressed": "dosyaya yazma", "numpy.savetxt": "dosyaya yazma",
    "torch.hub.load": "internetten model indirme", "torch.hub.download_url_to_file": "internetten model indirme",
    "uvicorn.run": "sunucu açma",
}
# Sözleşme bunlara yalnız modülün KENDİ ağırlık dosyası için izin verir; denetleyici dosyayı ayırt edemez → UYARI.
UYARI_CAGRI = {
    "pickle.load": "pickle", "pickle.loads": "pickle", "joblib.load": "joblib", "dill.load": "dill", "dill.loads": "dill",
}
_OPEN_ADLARI = ("open", "io.open", "builtins.open")


def _ad(dugum: ast.AST) -> str:
    """`a.b.c` biçimli çağrı adını çıkarır; çözülemezse boş dize."""
    if isinstance(dugum, ast.Name):
        return dugum.id
    if isinstance(dugum, ast.Attribute):
        ust = _ad(dugum.value)
        return f"{ust}.{dugum.attr}" if ust else ""
    return ""


def _takma_adlar(agac: ast.AST) -> dict[str, str]:
    """`import numpy as n` → {"n": "numpy"}; `from os import system as s` → {"s": "os.system"}."""
    adlar: dict[str, str] = {}
    for d in ast.walk(agac):
        if isinstance(d, ast.Import):
            for a in d.names:
                if a.asname:
                    adlar[a.asname] = a.name
        elif isinstance(d, ast.ImportFrom) and d.module and d.level == 0:
            for a in d.names:
                adlar[a.asname or a.name] = f"{d.module}.{a.name}"
    return adlar


def _tam_ad(ad: str, takma: dict[str, str]) -> str:
    bas, nokta, kalan = ad.partition(".")
    return takma[bas] + nokta + kalan if bas in takma else ad


def _yazma_kipi(kip: object) -> bool:
    return isinstance(kip, str) and any(k in kip for k in "wax+")


def duragan_denetim(dosya: Path) -> tuple[list[str], list[str]]:
    hatalar: list[str] = []
    uyarilar: list[str] = []
    try:
        agac = ast.parse(dosya.read_text(encoding="utf-8"), filename=str(dosya))
    except SyntaxError as e:
        return [f"{dosya.name}:{e.lineno}: Python 3.10'da sözdizimi hatası — {e.msg}"], uyarilar
    takma = _takma_adlar(agac)
    for d in ast.walk(agac):
        if isinstance(d, (ast.Import, ast.ImportFrom)):
            adlar = [a.name for a in d.names] if isinstance(d, ast.Import) else [d.module or ""]
            for ad in adlar:
                kok = ad.split(".")[0]
                if kok in YASAK_ICE_AKTARMA:
                    hatalar.append(f"{dosya.name}:{d.lineno}: yasaklı içe aktarma `{ad}` ({YASAK_ICE_AKTARMA[kok]})")
        elif isinstance(d, ast.Call):
            yazilan = _ad(d.func)
            ad = _tam_ad(yazilan, takma)
            goster = f"`{yazilan}`" if yazilan == ad else f"`{yazilan}` (= `{ad}`)"
            if ad in YASAK_CAGRI:
                hatalar.append(f"{dosya.name}:{d.lineno}: yasaklı çağrı {goster} ({YASAK_CAGRI[ad]})")
            if ad in UYARI_CAGRI:
                uyarilar.append(f"{dosya.name}:{d.lineno}: {goster} — {UYARI_CAGRI[ad]} yalnız kendi ağırlık dosyanız için; ONNX yeğleyin")
            if ad == "torch.load":
                ok = any(k.arg == "weights_only" and isinstance(k.value, ast.Constant) and k.value.value is True for k in d.keywords)
                if not ok:
                    hatalar.append(f"{dosya.name}:{d.lineno}: `torch.load` `weights_only=True` olmadan (güvensiz çözme)")
            if ad in _OPEN_ADLARI:
                kip = d.args[1] if len(d.args) >= 2 else next((k.value for k in d.keywords if k.arg == "mode"), None)
                if isinstance(kip, ast.Constant) and _yazma_kipi(kip.value):
                    hatalar.append(f"{dosya.name}:{d.lineno}: dosyaya yazma `{yazilan}(..., {kip.value!r})` — sonuç bellekte dönmeli")
            if isinstance(d.func, ast.Attribute) and d.func.attr in ("write_text", "write_bytes"):
                hatalar.append(f"{dosya.name}:{d.lineno}: dosyaya yazma `.{d.func.attr}()` — sonuç bellekte dönmeli")
    return hatalar, uyarilar


def _sha256(yol: Path) -> str:
    h = hashlib.sha256()
    with open(yol, "rb") as f:
        for parca in iter(lambda: f.read(1 << 20), b""):
            h.update(parca)
    return h.hexdigest()


def _sentetik_girdi(tur: str, klasor: Path, bilgi: dict) -> Path:
    if tur == "goruntu":
        import numpy as np
        from PIL import Image

        rng = np.random.default_rng(1234)
        yol = klasor / "sentetik.png"
        Image.fromarray(rng.integers(0, 256, (96, 96, 3), dtype=np.uint8)).save(yol)
        return yol
    if tur == "ses":
        import wave

        import numpy as np

        yol = klasor / "sentetik.wav"
        t = np.arange(16000) / 16000.0
        veri = (0.3 * np.sin(2 * math.pi * 440 * t) * 32767).astype("<i2")
        with wave.open(str(yol), "wb") as w:
            w.setnchannels(1)
            w.setsampwidth(2)
            w.setframerate(16000)
            w.writeframes(veri.tobytes())
        return yol
    sutunlar = bilgi.get("tablo_sutunlari")
    if not sutunlar:
        raise LookupError("tablo modülünde MODUL_BILGISI['tablo_sutunlari'] yok — sentetik girdi üretilemedi")
    yol = klasor / "sentetik.csv"
    yol.write_text(",".join(sutunlar) + "\n" + ",".join("1" for _ in sutunlar) + "\n", encoding="utf-8")
    return yol


class KafesIhlali(PermissionError):
    """Kafesin engellediği erişim (modülün kendi PermissionError'ından ayırt etmek için)."""


_YAZMA_BAYRAKLARI = os.O_WRONLY | os.O_RDWR | os.O_APPEND | os.O_CREAT | os.O_TRUNC
_SUREC_CAGRILARI = ("system", "startfile", "execv", "execve", "execl", "execvp", "spawnv", "spawnl", "posix_spawn")


class _Kafes:
    """Çalıştırma aşamasında ağ ve alt süreç erişimini, `yazma_yasak` ise dosyaya yazmayı da keser (ihlal → KafesIhlali)."""

    def __init__(self, yazma_yasak: bool = False):
        self.yazma_yasak = yazma_yasak

    def _yama(self, nesne, ad: str, yeni) -> None:
        self._eski.append((nesne, ad, getattr(nesne, ad)))
        setattr(nesne, ad, yeni)

    def __enter__(self):
        self._eski: list[tuple[object, str, object]] = []

        def yasak(*_a, **_k):
            raise KafesIhlali("sözleşme kafesi: ağ / alt süreç erişimi yasak")

        for ad in ("connect", "connect_ex"):
            self._yama(socket.socket, ad, yasak)
        for ad in ("getaddrinfo", "create_connection"):
            self._yama(socket, ad, yasak)
        self._yama(subprocess, "Popen", yasak)
        for ad in _SUREC_CAGRILARI:
            if hasattr(os, ad):
                self._yama(os, ad, yasak)

        if self.yazma_yasak:
            eski_open, eski_os_open = builtins.open, os.open

            def korumali_open(file, mode="r", *a, **k):
                if _yazma_kipi(mode) and not isinstance(file, int):
                    raise KafesIhlali(f"sözleşme kafesi: dosyaya yazma yasak ({file})")
                return eski_open(file, mode, *a, **k)

            def korumali_os_open(path, flags, *a, **k):
                if flags & _YAZMA_BAYRAKLARI:
                    raise KafesIhlali(f"sözleşme kafesi: dosyaya yazma yasak ({path})")
                return eski_os_open(path, flags, *a, **k)

            self._yama(builtins, "open", korumali_open)
            self._yama(io, "open", korumali_open)
            self._yama(os, "open", korumali_os_open)
        return self

    def __exit__(self, *_):
        for nesne, ad, eski in reversed(self._eski):
            setattr(nesne, ad, eski)
        return False


def _hata_metni(e: BaseException) -> str:
    return f"{type(e).__name__}: {e}"


def _dosya_listesi(kok: Path) -> set[str]:
    return {str(p.relative_to(kok)) for p in kok.rglob("*") if "__pycache__" not in p.parts}


def denetle(modul: Path) -> tuple[list[str], list[str]]:
    hatalar: list[str] = []
    uyarilar: list[str] = []
    for gerekli in ("__init__.py", "predictor.py", "MODEL_KARTI.md"):
        if not (modul / gerekli).is_file():
            hatalar.append(f"eksik dosya: {gerekli}")
    testler = list((modul / "tests").glob("test_*.py")) if (modul / "tests").is_dir() else []
    if not testler:
        hatalar.append("eksik: tests/test_*.py (en az bir test dosyası)")
    for py in sorted(modul.rglob("*.py")):
        if "tests" in py.relative_to(modul).parts:
            continue
        h, u = duragan_denetim(py)
        hatalar.extend(h)
        uyarilar.extend(u)
    # Boyut sınırı listelenmiş olsun olmasın her dosyaya uygulanır (GitHub 100 MB'tan büyük dosyayı reddeder).
    for yol in sorted(p for p in modul.rglob("*") if p.is_file() and "__pycache__" not in p.parts):
        mb = yol.stat().st_size / 1e6
        if mb > AZAMI_AGIRLIK_MB:
            hatalar.append(f"{yol.relative_to(modul).as_posix()} {mb:.0f} MB > {AZAMI_AGIRLIK_MB} MB (konu açın, dağıtım ekiple planlanır)")
    if hatalar:
        return hatalar, uyarilar

    spec = importlib.util.spec_from_file_location(f"_denetim_{modul.name}", modul / "predictor.py")
    mod = importlib.util.module_from_spec(spec)
    calisma = Path(tempfile.mkdtemp(prefix="sozlesme_"))
    once_modul = _dosya_listesi(modul)
    eski_cwd = os.getcwd()
    sonuclar = []
    try:
        os.chdir(calisma)
        # İçe aktarma: ağ / alt süreç kafesli; dosya yazmaya izin var (bazı kütüphaneler içe aktarılırken önbellek yazar).
        with _Kafes():
            try:
                spec.loader.exec_module(mod)
            except SystemExit:
                return ["içe aktarma `sys.exit` çağırdı"], uyarilar
            except KafesIhlali as e:
                return [f"içe aktarma yasak erişim denedi: {e}"], uyarilar
            except Exception as e:
                return [f"içe aktarma hata verdi — {_hata_metni(e)}"], uyarilar
        bilgi = getattr(mod, "MODUL_BILGISI", None)
        if not isinstance(bilgi, dict):
            return ["predictor.py'de MODUL_BILGISI sözlüğü yok"], uyarilar
        eksik = [k for k in ZORUNLU_BILGI if k not in bilgi]
        if eksik:
            return [f"MODUL_BILGISI eksik alan: {', '.join(eksik)}"], uyarilar
        if bilgi["ad"] != modul.name:
            hatalar.append(f"MODUL_BILGISI['ad'] ({bilgi['ad']!r}) klasör adıyla ({modul.name!r}) aynı değil")
        if bilgi["girdi_turu"] not in GIRDI_TURLERI:
            return hatalar + [f"girdi_turu {bilgi['girdi_turu']!r} geçersiz ({', '.join(GIRDI_TURLERI)})"], uyarilar
        listelenen = set()
        for goreli, beklenen in (bilgi.get("model_dosyalari") or {}).items():
            yol = modul / goreli
            listelenen.add(yol.resolve())
            if not yol.is_file():
                hatalar.append(f"model dosyası yok: {goreli}")
                continue
            if _sha256(yol) != beklenen:
                hatalar.append(f"{goreli} SHA-256 MODUL_BILGISI'ndekiyle uyuşmuyor")
        if (modul / "agirliklar").is_dir():
            for yol in sorted(p for p in (modul / "agirliklar").rglob("*") if p.is_file()):
                if yol.resolve() not in listelenen:
                    uyarilar.append(f"{yol.relative_to(modul).as_posix()} MODUL_BILGISI['model_dosyalari']'nda yok (SHA-256 denetlenmedi)")
        Predictor = getattr(mod, "Predictor", None)
        if Predictor is None:
            return hatalar + ["predictor.py'de Predictor sınıfı yok"], uyarilar
        try:
            girdi = _sentetik_girdi(bilgi["girdi_turu"], calisma, bilgi)
        except LookupError as e:
            uyarilar.append(f"çalıştırma aşaması atlandı: {e}")
            return hatalar, uyarilar
        once_calisma = _dosya_listesi(calisma)
        with _Kafes(yazma_yasak=True):
            t0 = time.perf_counter()
            try:
                p = Predictor()
            except SystemExit:
                return hatalar + ["Predictor() `sys.exit` çağırdı"], uyarilar
            except KafesIhlali as e:
                return hatalar + [f"Predictor() yasak erişim denedi: {e}"], uyarilar
            except Exception as e:
                return hatalar + [f"Predictor() hata verdi — {_hata_metni(e)}"], uyarilar
            yukleme = time.perf_counter() - t0
            if yukleme > AZAMI_YUKLEME_SN:
                hatalar.append(f"ilk yükleme {yukleme:.1f} sn > {AZAMI_YUKLEME_SN:.0f} sn")
            for _ in range(2):
                t0 = time.perf_counter()
                try:
                    r = p.predict(str(girdi))
                except SystemExit:
                    return hatalar + ["predict() `sys.exit` çağırdı"], uyarilar
                except KafesIhlali as e:
                    return hatalar + [f"predict() yasak erişim denedi: {e}"], uyarilar
                except Exception as e:
                    return hatalar + [f"predict() sentetik girdide hata verdi — {_hata_metni(e)}"], uyarilar
                sure = time.perf_counter() - t0
                if sure > AZAMI_SURE_SN:
                    hatalar.append(f"predict() {sure:.1f} sn > {AZAMI_SURE_SN:.0f} sn")
                sonuclar.append(r)
        # Kafesin göremediği yollar için (ör. alt düzey os çağrıları) son bir dosya farkı denetimi.
        yeni = (_dosya_listesi(calisma) - once_calisma) | (_dosya_listesi(modul) - once_modul)
        if yeni:
            hatalar.append(f"predict() dosya yazdı: {sorted(yeni)[:5]}")
    finally:
        os.chdir(eski_cwd)
        shutil.rmtree(calisma, ignore_errors=True)

    r = sonuclar[0]
    if not isinstance(r, dict):
        return hatalar + [f"predict() sözlük döndürmeli, {type(r).__name__} döndürdü"], uyarilar
    try:
        json.dumps(r, allow_nan=False)
    except (TypeError, ValueError) as e:
        hatalar.append(f"dönüş katı JSON değil (NaN / inf / numpy türü?): {e}")
    if r.get("label") not in bilgi["etiketler"]:
        hatalar.append(f"label {r.get('label')!r} MODUL_BILGISI['etiketler'] içinde değil")
    c = r.get("confidence")
    if not isinstance(c, float) or not 0.0 <= c <= 1.0:
        hatalar.append(f"confidence 0–1 arası float olmalı, {c!r}")
    for alan, tur in (("probabilities", dict), ("details", dict), ("warnings", list), ("xai", dict)):
        if alan in r and not isinstance(r[alan], tur):
            hatalar.append(f"{alan} {tur.__name__} olmalı")
    if json.dumps(sonuclar[0], sort_keys=True, default=str) != json.dumps(sonuclar[1], sort_keys=True, default=str):
        hatalar.append("belirlenimci değil: aynı girdi iki çağrıda farklı sonuç verdi")
    return hatalar, uyarilar


def main(argv: list[str]) -> int:
    # Windows'ta çıktı boruya / dosyaya yönlenince cp1254 / cp437 kullanılır ve "GEÇTİ" bozulur; her zaman UTF-8 yaz.
    for akim in (sys.stdout, sys.stderr):
        if hasattr(akim, "reconfigure"):
            akim.reconfigure(encoding="utf-8", errors="replace")
    if not argv:
        print(__doc__)
        return 1
    kotu = 0
    for a in argv:
        modul = Path(a).resolve()
        print(f"== {modul.name}")
        if not modul.is_dir():
            print(f"   HATA: klasör yok: {a}")
            kotu += 1
            continue
        try:
            hatalar, uyarilar = denetle(modul)
        except Exception as e:  # denetleyicinin kendi hatası: bu modülü KALDI say, sıradakilere devam et
            hatalar, uyarilar = [f"denetleyici beklenmedik hata verdi — {_hata_metni(e)} (konu açın)"], []
        for u in uyarilar:
            print(f"   UYARI: {u}")
        for h in hatalar:
            print(f"   HATA: {h}")
        print("   GEÇTİ" if not hatalar else f"   KALDI ({len(hatalar)} hata)")
        kotu += bool(hatalar)
    return 1 if kotu else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
