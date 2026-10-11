# -*- coding: utf-8 -*-
"""AI modül sözleşmesi denetleyicisi (docs/ai-modul-sozlesmesi.md).

Kullanım:  python araclar/sozlesme_denetimi.py moduller/<modul_adi> [moduller/<baska> ...]
Çıkış kodu: 0 = hepsi geçti · 1 = en az bir HATA var. UYARI'lar çıkış kodunu etkilemez.

İki aşama:
  1) Durağan: klasör düzeni, MODUL_BILGISI, model dosyası boyutu ve SHA-256, yasaklı içe aktarma ve çağrılar (AST ile).
  2) Çalıştırma: modül ağ / alt süreç kafesi içinde içe aktarılır, sentetik girdiyle predict() İKİ kez çağrılır;
     dönüş biçimi, katı JSON, belirlenimcilik, süre ve "dosya yazmadı" denetlenir.
"""
from __future__ import annotations

import ast
import hashlib
import importlib.util
import json
import math
import os
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
YASAK_CAGRI = {
    "sys.exit": "uygulamayı kapatır", "os._exit": "uygulamayı kapatır", "exit": "uygulamayı kapatır", "quit": "uygulamayı kapatır",
    "os.system": "başka program çalıştırma", "os.popen": "başka program çalıştırma",
    "eval": "kod çalıştırma", "exec": "kod çalıştırma",
    "cv2.VideoCapture": "kamera", "cv2.imshow": "pencere", "cv2.namedWindow": "pencere", "cv2.waitKey": "pencere",
    "cv2.imwrite": "dosyaya yazma", "np.save": "dosyaya yazma", "np.savez": "dosyaya yazma", "numpy.save": "dosyaya yazma",
    "torch.hub.load": "internetten model indirme", "uvicorn.run": "sunucu açma",
}


def _ad(dugum: ast.AST) -> str:
    """`a.b.c` biçimli çağrı adını çıkarır; çözülemezse boş dize."""
    if isinstance(dugum, ast.Name):
        return dugum.id
    if isinstance(dugum, ast.Attribute):
        ust = _ad(dugum.value)
        return f"{ust}.{dugum.attr}" if ust else ""
    return ""


def duragan_denetim(dosya: Path) -> list[str]:
    hatalar = []
    try:
        agac = ast.parse(dosya.read_text(encoding="utf-8"), filename=str(dosya))
    except SyntaxError as e:
        return [f"{dosya.name}:{e.lineno}: Python 3.10'da sözdizimi hatası — {e.msg}"]
    for d in ast.walk(agac):
        if isinstance(d, (ast.Import, ast.ImportFrom)):
            adlar = [a.name for a in d.names] if isinstance(d, ast.Import) else [d.module or ""]
            for ad in adlar:
                kok = ad.split(".")[0]
                if kok in YASAK_ICE_AKTARMA:
                    hatalar.append(f"{dosya.name}:{d.lineno}: yasaklı içe aktarma `{ad}` ({YASAK_ICE_AKTARMA[kok]})")
        elif isinstance(d, ast.Call):
            ad = _ad(d.func)
            if ad in YASAK_CAGRI:
                hatalar.append(f"{dosya.name}:{d.lineno}: yasaklı çağrı `{ad}` ({YASAK_CAGRI[ad]})")
            if ad == "torch.load":
                ok = any(k.arg == "weights_only" and isinstance(k.value, ast.Constant) and k.value.value is True for k in d.keywords)
                if not ok:
                    hatalar.append(f"{dosya.name}:{d.lineno}: `torch.load` `weights_only=True` olmadan (güvensiz çözme)")
            if ad == "open" and len(d.args) >= 2 and isinstance(d.args[1], ast.Constant) and isinstance(d.args[1].value, str):
                if any(k in d.args[1].value for k in "wax+"):
                    hatalar.append(f"{dosya.name}:{d.lineno}: dosyaya yazma `open(..., {d.args[1].value!r})` — sonuç bellekte dönmeli")
    return hatalar


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


class _Kafes:
    """Çalıştırma aşamasında ağ ve alt süreç erişimini keser (ihlal → istisna, denetleyici yakalar)."""

    def __enter__(self):
        self._eski = (socket.socket.connect, socket.socket.connect_ex, socket.getaddrinfo, socket.create_connection, subprocess.Popen)

        def yasak(*_a, **_k):
            raise PermissionError("sözleşme kafesi: ağ / alt süreç erişimi yasak")

        socket.socket.connect = yasak
        socket.socket.connect_ex = yasak
        socket.getaddrinfo = yasak
        socket.create_connection = yasak
        subprocess.Popen = yasak
        return self

    def __exit__(self, *_):
        (socket.socket.connect, socket.socket.connect_ex, socket.getaddrinfo, socket.create_connection, subprocess.Popen) = self._eski
        return False


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
        hatalar.extend(duragan_denetim(py))
    if hatalar:
        return hatalar, uyarilar

    spec = importlib.util.spec_from_file_location(f"_denetim_{modul.name}", modul / "predictor.py")
    mod = importlib.util.module_from_spec(spec)
    calisma = Path(tempfile.mkdtemp(prefix="sozlesme_"))
    once_modul = _dosya_listesi(modul)
    eski_cwd = os.getcwd()
    try:
        os.chdir(calisma)
        with _Kafes():
            try:
                spec.loader.exec_module(mod)
            except SystemExit:
                return ["içe aktarma `sys.exit` çağırdı"], uyarilar
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
            for goreli, beklenen in (bilgi.get("model_dosyalari") or {}).items():
                yol = modul / goreli
                if not yol.is_file():
                    hatalar.append(f"model dosyası yok: {goreli}")
                    continue
                mb = yol.stat().st_size / 1e6
                if mb > AZAMI_AGIRLIK_MB:
                    hatalar.append(f"{goreli} {mb:.0f} MB > {AZAMI_AGIRLIK_MB} MB (konu açın, dağıtım ekiple planlanır)")
                if _sha256(yol) != beklenen:
                    hatalar.append(f"{goreli} SHA-256 MODUL_BILGISI'ndekiyle uyuşmuyor")
            Predictor = getattr(mod, "Predictor", None)
            if Predictor is None:
                return hatalar + ["predictor.py'de Predictor sınıfı yok"], uyarilar
            try:
                girdi = _sentetik_girdi(bilgi["girdi_turu"], calisma, bilgi)
            except LookupError as e:
                uyarilar.append(f"çalıştırma aşaması atlandı: {e}")
                return hatalar, uyarilar
            once_calisma = _dosya_listesi(calisma)
            t0 = time.perf_counter()
            try:
                p = Predictor()
            except SystemExit:
                return hatalar + ["Predictor() `sys.exit` çağırdı"], uyarilar
            yukleme = time.perf_counter() - t0
            if yukleme > AZAMI_YUKLEME_SN:
                hatalar.append(f"ilk yükleme {yukleme:.1f} sn > {AZAMI_YUKLEME_SN:.0f} sn")
            sonuclar = []
            for _ in range(2):
                t0 = time.perf_counter()
                try:
                    r = p.predict(str(girdi))
                except SystemExit:
                    return hatalar + ["predict() `sys.exit` çağırdı"], uyarilar
                except PermissionError as e:
                    return hatalar + [f"predict() yasak erişim denedi: {e}"], uyarilar
                sure = time.perf_counter() - t0
                if sure > AZAMI_SURE_SN:
                    hatalar.append(f"predict() {sure:.1f} sn > {AZAMI_SURE_SN:.0f} sn")
                sonuclar.append(r)
    finally:
        os.chdir(eski_cwd)

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
    yeni = (_dosya_listesi(calisma) - once_calisma) | (_dosya_listesi(modul) - once_modul)
    if yeni:
        hatalar.append(f"predict() dosya yazdı: {sorted(yeni)[:5]}")
    return hatalar, uyarilar


def main(argv: list[str]) -> int:
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
        hatalar, uyarilar = denetle(modul)
        for u in uyarilar:
            print(f"   UYARI: {u}")
        for h in hatalar:
            print(f"   HATA: {h}")
        print("   GEÇTİ" if not hatalar else f"   KALDI ({len(hatalar)} hata)")
        kotu += bool(hatalar)
    return 1 if kotu else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
