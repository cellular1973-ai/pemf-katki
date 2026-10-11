# -*- coding: utf-8 -*-
"""Örnek modülün testleri — kendi modülünüz için en az bu üç türü yazın (sözleşme §6)."""
import importlib.util
import json
from pathlib import Path

import numpy as np
import pytest
from PIL import Image

_KOK = Path(__file__).resolve().parents[1]
_spec = importlib.util.spec_from_file_location("ornek_parlaklik_predictor", _KOK / "predictor.py")
predictor = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(predictor)


def _goruntu(yol: Path, deger: int) -> Path:
    Image.fromarray(np.full((32, 32), deger, dtype=np.uint8)).save(yol)
    return yol


def test_sozlesme_alanlari(tmp_path):
    r = predictor.Predictor().predict(str(_goruntu(tmp_path / "a.png", 200)))
    assert r["label"] in predictor.MODUL_BILGISI["etiketler"]
    assert isinstance(r["confidence"], float) and 0.0 <= r["confidence"] <= 1.0
    json.dumps(r, allow_nan=False)  # katı JSON


@pytest.mark.parametrize("deger, beklenen", [(20, "Karanlık"), (235, "Aydınlık")])
def test_ornek_girdiler(tmp_path, deger, beklenen):
    assert predictor.Predictor().predict(str(_goruntu(tmp_path / "g.png", deger)))["label"] == beklenen


def test_bozuk_girdi_anlasilir_hata_verir(tmp_path):
    bozuk = tmp_path / "bozuk.png"
    bozuk.write_bytes(b"bu bir png degil")
    with pytest.raises(ValueError, match="okunamadı"):
        predictor.Predictor().predict(str(bozuk))
