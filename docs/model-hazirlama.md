# Modeli hazırlama: eğitimden ONNX'e, ONNX'ten `predictor.py`'ye

## 1. Ana uygulamanın ortamı

Modülünüz bu sürümlerle çalışmalı. Eğitimde farklı sürüm kullanabilirsiniz; **teslim edilen `predictor.py`** bunlarla çalışmalı.

| Paket | Ana uygulamadaki sürüm | Modülde kullanım |
|---|---|---|
| Python | 3.10.2 | zorunlu |
| numpy | 1.26.4 | serbest (numpy 2'ye özgü çağrı yok) |
| onnxruntime | 1.19.2 | **model çalıştırma için tek yol** |
| pillow | 12.3.0 | görüntü okuma |
| librosa | 0.11.0 | ses (gerekirse `requirements.txt`'ye PR'da gerekçeyle ekleyin) |
| scipy | 1.15.3 | gerekirse |
| pandas | 2.3.3 | gerekirse (tablo okumak için standart `csv` modülü de yeter) |
| opencv-python | 4.11 | gerekirse (yalnız görüntü işleme; kamera / pencere YASAK) |
| torch / torchvision | 2.1.2 (CPU) | **modülde KULLANMAYIN**; yalnız eğitim ve ONNX'e aktarma |

## 2. Eğitim önerileri

- **Veri ayrımı:** eğitim / doğrulama / test kümelerini **hayvan bazında** ayırın; aynı hayvanın fotoğrafları iki kümede olursa sonuç olduğundan
  iyi çıkar.
- **Sınıf dengesi:** sınıflar dengesizse ağırlıklı kayıp ya da yeniden örnekleme kullanın; model kartına sınıf dağılımını yazın.
- **Metrikleri test kümesinde** ölçün: doğruluk tek başına yetmez; sınıf başına duyarlılık / özgüllük ve mümkünse AUC.
- **Ön işlemeyi bir yere yazın:** girdi boyutu, renk sırası (RGB), normalizasyon ortalaması ve standart sapması. `predictor.py`'de birebir
  aynısını kullanacaksınız; farklı olursa model sessizce yanlış tahmin yapar.

## 3. ONNX'e aktarma

**PyTorch:**
```python
import torch
model.eval()                                   # dropout / batchnorm çıkarım kipinde — belirlenimcilik için şart
ornek = torch.randn(1, 3, 224, 224)            # eğitimdeki girdi biçimi
torch.onnx.export(model, ornek, "model.onnx", input_names=["girdi"], output_names=["logit"], opset_version=17)
```

**scikit-learn** (`pip install skl2onnx`):
```python
from skl2onnx import convert_sklearn
from skl2onnx.common.data_types import FloatTensorType
onx = convert_sklearn(model, initial_types=[("girdi", FloatTensorType([None, ozellik_sayisi]))],
                      options={id(model): {"zipmap": False}})       # olasılıklar sözlük listesi değil, dizi olarak gelsin
open("model.onnx", "wb").write(onx.SerializeToString())
```

**TensorFlow / Keras** (`pip install tf2onnx`): `python -m tf2onnx.convert --saved-model kayitli_model --output model.onnx --opset 17`

**XGBoost** (`pip install onnxmltools`): `onnxmltools.convert_xgboost(model, initial_types=[("girdi", FloatTensorType([None, n]))])`

**Aktarımı doğrulayın** — ONNX çıktısı eğitim çerçevesinin çıktısıyla aynı olmalı:
```python
import numpy as np, onnxruntime as ort
oturum = ort.InferenceSession("model.onnx", providers=["CPUExecutionProvider"])
onnx_cikti = oturum.run(None, {"girdi": ornek.numpy()})[0]
assert np.allclose(onnx_cikti, model(ornek).detach().numpy(), atol=1e-4)
```

**Büyük model (> 95 MB):** daha küçük mimari deneyin ya da nicemleyin (doğruluğu yeniden ölçün):
```python
from onnxruntime.quantization import quantize_dynamic, QuantType
quantize_dynamic("model.onnx", "model_int8.onnx", weight_type=QuantType.QInt8)
```

## 4. SHA-256 özeti

Model dosyasını `moduller\<modul_adi>\agirliklar\model.onnx` olarak koyun, özetini alın ve `MODUL_BILGISI["model_dosyalari"]`'na yazın:
```powershell
(Get-FileHash moduller\kedi_deri_lezyonu\agirliklar\model.onnx -Algorithm SHA256).Hash.ToLower()
```
(macOS / Linux: `sha256sum moduller/kedi_deri_lezyonu/agirliklar/model.onnx`). Modeli her değiştirdiğinizde yeniden alın.

## 5. `predictor.py` iskeleti — görüntü sınıflandırma

Bu iskelet gerçek bir ONNX modeliyle ana uygulamanın Python'unda denetleyiciden geçti. Kendi değerlerinizi yazın.

```python
# -*- coding: utf-8 -*-
from __future__ import annotations

from pathlib import Path

import numpy as np
import onnxruntime as ort
from PIL import Image, UnidentifiedImageError

MODUL_BILGISI = {
    "ad": "kedi_deri_lezyonu",
    "baslik": "Kedi Deri Lezyonu",
    "surum": "0.1.0",
    "girdi_turu": "goruntu",
    "etiketler": ["Sağlıklı", "Lezyon"],
    "yazarlar": ["Ad Soyad <eposta>"],
    "model_dosyalari": {"agirliklar/model.onnx": "<sha256>"},
}

_BOYUT = 224
_ORT = np.array([0.485, 0.456, 0.406], dtype=np.float32)   # EĞİTİMDEKİYLE AYNI
_SS = np.array([0.229, 0.224, 0.225], dtype=np.float32)


class Predictor:
    def __init__(self, model_dir: str | None = None):
        kok = Path(model_dir) if model_dir else Path(__file__).parent
        self.oturum = ort.InferenceSession(str(kok / "agirliklar" / "model.onnx"), providers=["CPUExecutionProvider"])
        self.girdi_adi = self.oturum.get_inputs()[0].name

    def _hazirla(self, yol: str) -> np.ndarray:
        try:
            with Image.open(yol) as im:
                im = im.convert("RGB").resize((_BOYUT, _BOYUT), Image.BILINEAR)
                x = np.asarray(im, dtype=np.float32) / 255.0
        except (FileNotFoundError, UnidentifiedImageError, OSError) as e:
            raise ValueError(f"Görüntü okunamadı: {Path(yol).name} — dosyayı denetleyin") from e
        x = (x - _ORT) / _SS
        return x.transpose(2, 0, 1)[None].astype(np.float32)   # (1, 3, 224, 224)

    def predict(self, girdi_yolu: str) -> dict:
        logit = self.oturum.run(None, {self.girdi_adi: self._hazirla(girdi_yolu)})[0][0]
        e = np.exp(logit - logit.max())
        olas = e / e.sum()
        i = int(olas.argmax())
        etiketler = MODUL_BILGISI["etiketler"]
        return {
            "label": etiketler[i],
            "confidence": round(float(olas[i]), 4),
            "probabilities": {ad: round(float(p), 4) for ad, p in zip(etiketler, olas)},
        }
```

## 6. Tablo ve ses modülleri

**Tablo** (ör. kan tahlili): `MODUL_BILGISI`'ne `"girdi_turu": "tablo"` ve `"tablo_sutunlari": ["kreatinin", "ure", ...]` ekleyin (denetleyici
bu adlarla sentetik bir CSV üretir). `predict()` tek satırlık bir CSV okur, sütunları bu sırayla `float32` diziye çevirip modele verir.
Eksik ya da sayı olmayan değer → `ValueError("kreatinin değeri eksik")`. Eğitimde ölçekleme (StandardScaler vb.) kullandıysanız onu da
ONNX'in içine alın (scikit-learn'de `Pipeline` olarak aktarın) — ayrı bir pickle dosyası kullanmayın.

**Ses** (ör. solunum sesi): `"girdi_turu": "ses"`. Sabit örnekleme hızı ve süre (kısa kaydı sıfırla doldurun, uzunu kırpın); mel spektrogram
ayarları (n_mels, hop_length, fmax) eğitimdekiyle aynı. Sessiz kayıt için uyarı döndürün: `"warnings": ["Kayıtta ses yok — yeniden kaydedin"]`.

## 7. Açıklanabilirlik (isteğe bağlı)

`docs/ai-modul-sozlesmesi.md` §5. Görüntüde Grad-CAM için modelin PyTorch hâli gerekir; bunu konunuzda ekiple konuşun (ONNX'te gradyan
yoktur). Tablo modellerinde SHAP değerleri `xai.ust_oznitelikler` olarak döndürülebilir. Açıklama her zaman **tahmin edilen** sınıfı açıklamalı.
