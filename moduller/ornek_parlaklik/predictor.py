# -*- coding: utf-8 -*-
"""Örnek modül — sözleşmeyi gösterir, gerçek bir tanı yapmaz.

Görüntünün ortalama parlaklığına bakıp "Karanlık" / "Aydınlık" der. Kendi modülünüzü yazarken bu klasörü
`moduller/<modul_adi>/` olarak kopyalayın; `MODUL_BILGISI`'ni, `Predictor`'ı, testleri ve model kartını değiştirin.
Gerçek bir model ONNX ağırlığını `agirliklar/` altından `onnxruntime` ile (CPUExecutionProvider) yükler.
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
from PIL import Image, UnidentifiedImageError

MODUL_BILGISI = {
    "ad": "ornek_parlaklik",
    "baslik": "Örnek: Parlaklık",
    "surum": "0.1.0",
    "girdi_turu": "goruntu",
    "etiketler": ["Karanlık", "Aydınlık"],
    "yazarlar": ["PEMF Vet ekibi"],
    "model_dosyalari": {},  # gerçek modülde: {"agirliklar/model.onnx": "<sha256>"}
}

_ESIK = 0.5          # ortalama parlaklık (0–1) bu değerin altındaysa "Karanlık"
_EGIM = 12.0         # olasılığa çeviren lojistik eğrinin dikliği


class Predictor:
    def __init__(self, model_dir: str | None = None):
        # Gerçek modülde: ağırlık model_dir'den (yoksa bu klasörden) yüklenir; İNTERNETTEN İNDİRİLMEZ.
        self.model_dir = Path(model_dir) if model_dir else Path(__file__).parent

    def predict(self, girdi_yolu: str) -> dict:
        try:
            with Image.open(girdi_yolu) as im:
                gri = np.asarray(im.convert("L"), dtype=np.float32) / 255.0
        except (FileNotFoundError, UnidentifiedImageError, OSError) as e:
            raise ValueError(f"Görüntü okunamadı: {Path(girdi_yolu).name} — dosyanın bozuk olmadığını denetleyin") from e
        if gri.size == 0:
            raise ValueError("Görüntü boş")

        parlaklik = float(gri.mean())
        p_aydinlik = float(1.0 / (1.0 + np.exp(-_EGIM * (parlaklik - _ESIK))))
        etiket = "Aydınlık" if p_aydinlik >= 0.5 else "Karanlık"
        uyarilar = []
        if float(gri.std()) < 0.02:
            uyarilar.append("Görüntü neredeyse tek renk — çekimi yeniden yapın")
        return {
            "label": etiket,
            "confidence": round(max(p_aydinlik, 1.0 - p_aydinlik), 4),
            "probabilities": {"Karanlık": round(1.0 - p_aydinlik, 4), "Aydınlık": round(p_aydinlik, 4)},
            "details": {"ortalama_parlaklik": round(parlaklik, 4)},
            "warnings": uyarilar,
        }
