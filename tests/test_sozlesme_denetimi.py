# -*- coding: utf-8 -*-
"""Denetleyicinin kendisi: örnek modül GEÇER, her kural ihlali KALIR (kapı gerçekten kırmızı olabiliyor mu?)."""
import importlib.util
import os
import subprocess
import sys
import textwrap
from pathlib import Path

import pytest

_KOK = Path(__file__).resolve().parents[1]
_spec = importlib.util.spec_from_file_location("sozlesme_denetimi", _KOK / "araclar" / "sozlesme_denetimi.py")
sd = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(sd)

_IYI_PREDICTOR = '''
import numpy as np
from PIL import Image
MODUL_BILGISI = {"ad": "{ad}", "baslik": "T", "surum": "0.1.0", "girdi_turu": "goruntu",
                 "etiketler": ["A", "B"], "yazarlar": ["t"], "model_dosyalari": {}}
class Predictor:
    def __init__(self, model_dir=None):
        pass
    def predict(self, girdi_yolu):
        with Image.open(girdi_yolu) as im:
            m = float(np.asarray(im.convert("L")).mean()) / 255.0
        {govde}
        return {"label": "A" if m < 0.5 else "B", "confidence": 0.9}
'''


def _modul(tmp_path: Path, ad: str = "deneme_modul", ust: str = "", govde: str = "pass") -> Path:
    d = tmp_path / ad
    (d / "tests").mkdir(parents=True)
    (d / "__init__.py").write_text("", encoding="utf-8")
    (d / "MODEL_KARTI.md").write_text("# kart\n", encoding="utf-8")
    (d / "tests" / "test_x.py").write_text("def test_x():\n    assert True\n", encoding="utf-8")
    kaynak = textwrap.dedent(_IYI_PREDICTOR).replace("{ad}", ad).replace("{govde}", govde)
    (d / "predictor.py").write_text(ust + kaynak, encoding="utf-8")
    return d


def _hatalar(modul: Path) -> list[str]:
    return sd.denetle(modul)[0]


def test_ornek_modul_gecer():
    assert _hatalar(_KOK / "moduller" / "ornek_parlaklik") == []


def test_iyi_sahte_modul_gecer(tmp_path):
    assert _hatalar(_modul(tmp_path)) == []


@pytest.mark.parametrize(
    "ust, govde, beklenen",
    [
        ("import requests\n", "pass", "yasaklı içe aktarma `requests`"),
        ("import subprocess\n", "pass", "yasaklı içe aktarma `subprocess`"),
        ("import sys\n", "sys.exit(1)", "yasaklı çağrı `sys.exit`"),
        ("import torch\n", "torch.load('x.pt')", "`torch.load` `weights_only=True` olmadan"),
        ("import cv2\n", "cv2.VideoCapture(0)", "yasaklı çağrı `cv2.VideoCapture`"),
        ("", "open('cikti.txt', 'w').write('x')", "dosyaya yazma"),
        ("", "eval('1+1')", "yasaklı çağrı `eval`"),
    ],
)
def test_yasaklar_duragan_yakalanir(tmp_path, ust, govde, beklenen):
    assert any(beklenen in h for h in _hatalar(_modul(tmp_path, ust=ust, govde=govde)))


def test_ad_klasorle_uyusmazsa_kalir(tmp_path):
    d = _modul(tmp_path, ad="dogru_ad")
    (d / "predictor.py").write_text((d / "predictor.py").read_text(encoding="utf-8").replace('"dogru_ad"', '"yanlis_ad"'), encoding="utf-8")
    assert any("klasör adıyla" in h for h in _hatalar(d))


def test_belirlenimci_olmayan_kalir(tmp_path):
    # Her çağrıda kesin farklı sonuç (rastgele değil — rastgele sayı iki çağrıda %50 aynı etiketi verip testi şansa bağlıyordu).
    govde = 'self.n = getattr(self, "n", 0) + 1\n        m = 0.0 if self.n == 1 else 1.0'
    assert any("belirlenimci değil" in h for h in _hatalar(_modul(tmp_path, govde=govde)))


def test_gecersiz_etiket_ve_guven_kalir(tmp_path):
    d = _modul(tmp_path)
    kaynak = (d / "predictor.py").read_text(encoding="utf-8")
    kaynak = kaynak.replace('"confidence": 0.9', '"confidence": 1.7').replace('"A" if m < 0.5 else "B"', '"Z"')
    (d / "predictor.py").write_text(kaynak, encoding="utf-8")
    hatalar = _hatalar(d)
    assert any("label" in h for h in hatalar) and any("confidence" in h for h in hatalar)


def test_nan_kati_json_degil(tmp_path):
    d = _modul(tmp_path)
    kaynak = (d / "predictor.py").read_text(encoding="utf-8")
    kaynak = kaynak.replace('"confidence": 0.9}', '"confidence": 0.9, "details": {"x": float("nan")}}')
    (d / "predictor.py").write_text(kaynak, encoding="utf-8")
    assert any("katı JSON" in h for h in _hatalar(d))


def test_calisirken_ag_erisimi_kafeste_yakalanir(tmp_path):
    # Adı gizlenmiş ağ erişimi (`sys.modules` üzerinden): durağan aşama göremez, kafes yakalar.
    govde = "s = sys.modules['so' + 'cket'].socket(); s.connect(('127.0.0.1', 9))"
    assert any("yasak erişim" in h for h in _hatalar(_modul(tmp_path, ust="import sys\n", govde=govde)))


def test_eksik_dosyalar_kalir(tmp_path):
    d = _modul(tmp_path)
    (d / "MODEL_KARTI.md").unlink()
    assert any("MODEL_KARTI.md" in h for h in _hatalar(d))


# --- Modülün fırlattığı hatalar denetleyiciyi çökertmez, HATA olarak raporlanır ---

def test_predict_hata_verirse_kalir_cokmez(tmp_path):
    hatalar = _hatalar(_modul(tmp_path, govde="raise RuntimeError('model bozuk')"))
    assert any("predict() sentetik girdide hata verdi" in h and "model bozuk" in h for h in hatalar)


def test_predictor_kurulumu_hata_verirse_kalir(tmp_path):
    d = _modul(tmp_path)
    kaynak = (d / "predictor.py").read_text(encoding="utf-8")
    kaynak = kaynak.replace("        pass\n", "        raise FileNotFoundError('agirlik yok')\n", 1)  # __init__ gövdesi
    (d / "predictor.py").write_text(kaynak, encoding="utf-8")
    assert any("Predictor() hata verdi" in h and "agirlik yok" in h for h in _hatalar(d))


def test_ice_aktarma_hata_verirse_kalir(tmp_path):
    assert any("içe aktarma hata verdi" in h for h in _hatalar(_modul(tmp_path, ust="import olmayan_paket_xyz\n")))


def test_bir_modul_cokse_de_siradakiler_denetlenir(tmp_path, capsys):
    kotu = _modul(tmp_path / "a", ad="kotu_modul", govde="raise RuntimeError('x')")
    iyi = _modul(tmp_path / "b", ad="iyi_modul")
    assert sd.main([str(kotu), str(iyi)]) == 1
    cikti = capsys.readouterr().out
    assert "== kotu_modul" in cikti and "KALDI" in cikti
    assert "== iyi_modul" in cikti and "GEÇTİ" in cikti


# --- Takma adlar ve atlatma yolları durağan aşamada yakalanır ---

@pytest.mark.parametrize(
    "ust, govde, beklenen",
    [
        ("from os import system\n", "system('echo x')", "`system` (= `os.system`)"),
        ("import os as isletim\n", "isletim.system('echo x')", "`isletim.system` (= `os.system`)"),
        ("from sys import exit as cik\n", "cik(1)", "(= `sys.exit`)"),
        ("import numpy as n\n", "n.save('x.npy', n.zeros(1))", "`n.save` (= `numpy.save`)"),
        ("import importlib\n", "importlib.import_module('socket')", "`importlib.import_module`"),
        ("", "__import__('socket')", "`__import__`"),
        ("", "open('cikti.txt', mode='w')", "dosyaya yazma"),
        ("from pathlib import Path\n", "Path('cikti.txt').write_text('x')", "`.write_text()`"),
    ],
)
def test_takma_ad_ve_atlatmalar_duragan_yakalanir(tmp_path, ust, govde, beklenen):
    assert any(beklenen in h for h in _hatalar(_modul(tmp_path, ust=ust, govde=govde)))


def test_pickle_load_uyari_verir(tmp_path):
    # m ≤ 1 olduğundan çağrı hiç çalışmaz; yalnız durağan uyarı denetlenir ve modül yine de geçer.
    hatalar, uyarilar = sd.denetle(_modul(tmp_path, ust="import pickle\n", govde="if m > 2: pickle.load(None)"))
    assert hatalar == []
    assert any("`pickle.load`" in u for u in uyarilar)


# --- Çalıştırma aşamasında dosyaya yazma ve os.system kafeste engellenir ---

def test_baska_klasore_yazma_engellenir_ve_kalir(tmp_path):
    hedef = tmp_path / "disari" / "iz.txt"
    hedef.parent.mkdir()
    # Durağan aşamanın göremeyeceği biçimde (getattr ile) yazma.
    govde = f"getattr(sys.modules['pathlib'].Path({str(hedef)!r}), 'write_' + 'text')('x')"
    hatalar = _hatalar(_modul(tmp_path, ust="import sys\nimport pathlib\n", govde=govde))
    assert any("dosyaya yazma yasak" in h for h in hatalar)
    assert not hedef.exists()


def test_numpy_ile_yazma_engellenir(tmp_path):
    hedef = tmp_path / "iz.npy"
    govde = f"getattr(np, 'sa' + 've')({str(hedef)!r}, np.zeros(1))"
    assert any("dosyaya yazma yasak" in h for h in _hatalar(_modul(tmp_path, govde=govde)))
    assert not hedef.exists()


def test_os_system_kafeste_yakalanir(tmp_path):
    govde = "getattr(os, 'sys' + 'tem')('echo x')"
    assert any("yasak erişim" in h for h in _hatalar(_modul(tmp_path, ust="import os\n", govde=govde)))


def test_kafes_cikista_her_seyi_geri_yukler():
    import builtins
    import io
    import socket
    once = (builtins.open, io.open, os.open, os.system, socket.socket.connect, subprocess.Popen)
    with sd._Kafes(yazma_yasak=True):
        assert builtins.open is not once[0]
    assert (builtins.open, io.open, os.open, os.system, socket.socket.connect, subprocess.Popen) == once


# --- Dosya boyutu, listelenmemiş ağırlık, geçici klasör, çıktı kodlaması ---

def test_listelenmemis_buyuk_dosya_kalir(tmp_path, monkeypatch):
    monkeypatch.setattr(sd, "AZAMI_AGIRLIK_MB", 0.001)  # 1 KB
    d = _modul(tmp_path)
    (d / "agirliklar").mkdir()
    (d / "agirliklar" / "gizli.onnx").write_bytes(b"\0" * 2000)
    assert any("agirliklar/gizli.onnx" in h and "MB >" in h for h in _hatalar(d))


def test_listelenmemis_agirlik_uyari_verir(tmp_path):
    d = _modul(tmp_path)
    (d / "agirliklar").mkdir()
    (d / "agirliklar" / "model.onnx").write_bytes(b"x")
    hatalar, uyarilar = sd.denetle(d)
    assert hatalar == []
    assert any("agirliklar/model.onnx" in u and "model_dosyalari" in u for u in uyarilar)


@pytest.mark.parametrize("govde", ["pass", "raise RuntimeError('x')"])
def test_gecici_klasor_silinir(tmp_path, monkeypatch, govde):
    acilan = []
    gercek = sd.tempfile.mkdtemp

    def kaydet(*a, **k):
        acilan.append(Path(gercek(*a, **k)))
        return str(acilan[-1])

    monkeypatch.setattr(sd.tempfile, "mkdtemp", kaydet)
    sd.denetle(_modul(tmp_path, govde=govde))
    assert len(acilan) == 1 and not acilan[0].exists()


def test_cikti_her_zaman_utf8(tmp_path):
    # Windows'ta boruya yönlenen çıktı ASCII / cp1254 olabilir; denetleyici yine de UTF-8 yazmalı.
    ortam = {**os.environ, "PYTHONIOENCODING": "ascii"}
    ortam.pop("PYTHONUTF8", None)
    s = subprocess.run(
        [sys.executable, str(_KOK / "araclar" / "sozlesme_denetimi.py"), str(_KOK / "moduller" / "ornek_parlaklik")],
        capture_output=True, env=ortam, timeout=120,
    )
    assert s.returncode == 0, s.stderr.decode("utf-8", "replace")
    assert "GEÇTİ" in s.stdout.decode("utf-8")
