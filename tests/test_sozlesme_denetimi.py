# -*- coding: utf-8 -*-
"""Denetleyicinin kendisi: örnek modül GEÇER, her kural ihlali KALIR (kapı gerçekten kırmızı olabiliyor mu?)."""
import importlib.util
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
    govde = "import random\n        m = random.random()"
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
    # İçe aktarma adı gizlenmiş ağ erişimi: durağan aşama göremez, kafes yakalar.
    govde = "s = __import__('so' + 'cket').socket(); s.connect(('127.0.0.1', 9))"
    assert any("yasak erişim" in h for h in _hatalar(_modul(tmp_path, govde=govde)))


def test_eksik_dosyalar_kalir(tmp_path):
    d = _modul(tmp_path)
    (d / "MODEL_KARTI.md").unlink()
    assert any("MODEL_KARTI.md" in h for h in _hatalar(d))
