# AI Modül Sözleşmesi (sürüm 1)

Bu sözleşmeye uyan bir modül, ana uygulamanın AI merkezine (AI Hub) eklenebilir. Kurallar ana uygulamadaki mevcut modüllerin gerçek yapısından ve
dış kaynaklı paketlerin entegrasyonunda yaşanan sorunlardan çıkarıldı. Denetleyici (`araclar/sozlesme_denetimi.py`) kuralların çoğunu otomatik
denetler; denetleyiciden geçmeyen modül incelemeye alınmaz.

## 1. Klasör düzeni

```
moduller/<modul_adi>/            # küçük harf, alt çizgi: kedi_deri_lezyonu
├── __init__.py
├── predictor.py                 # Predictor sınıfı + MODUL_BILGISI
├── MODEL_KARTI.md               # zorunlu — sablonlar/model-karti.md
├── agirliklar/                  # model dosyaları (her biri ≤ 95 MB; aşağıya bakın)
└── tests/
    └── test_<modul_adi>.py      # en az: sözleşme testi + 2 örnek girdi
```

## 2. `predictor.py`

```python
MODUL_BILGISI = {
    "ad": "kedi_deri_lezyonu",          # klasör adıyla aynı
    "baslik": "Kedi Deri Lezyonu",      # arayüzde görünecek Türkçe ad
    "surum": "0.1.0",
    "girdi_turu": "goruntu",            # "goruntu" | "ses" | "tablo"
    "etiketler": ["Sağlıklı", "Lezyon"],
    "yazarlar": ["Ad Soyad <eposta>"],
    "model_dosyalari": {"agirliklar/model.onnx": "<sha256>"},
}

class Predictor:
    def __init__(self, model_dir: str | None = None):
        """Ağırlıkları model_dir'den (yoksa modülün kendi klasöründen) yükler. İNTERNETTEN İNDİRMEZ."""

    def predict(self, girdi_yolu: str) -> dict:
        """Tek girdi → JSON'a çevrilebilir sözlük."""
```

### `predict()` dönüşü

| Alan | Tür | Zorunlu | Açıklama |
|---|---|---|---|
| `label` | `str` | evet | `MODUL_BILGISI["etiketler"]`'den biri |
| `confidence` | `float` | evet | 0–1 arası; `label` için modelin güveni |
| `probabilities` | `dict[str, float]` | hayır | etiket → olasılık; toplam ≈ 1 |
| `details` | `dict` | hayır | modüle özgü ek sayılar (ör. lezyon alanı mm²) |
| `warnings` | `list[str]` | hayır | Türkçe, eylem söyleyen uyarılar: "Görüntü bulanık — yeniden çekin" |
| `xai` | `dict` | hayır | bkz. §5 |

Dönüş **katı JSON** olmalı: `NaN`, `inf`, numpy türleri yok (`float(x)`, `int(x)`, `.tolist()` kullanın).

## 3. Yasaklar (denetleyici bunları arar)

| Yasak | Neden |
|---|---|
| Ağ erişimi: `requests`, `urllib`, `http.client`, `socket`, `paho`, model indirme (`torch.hub`, `YOLO("yolov8n.pt")` gibi çıplak adla indirme) | Cihaz internetsiz çalışabilir; hasta verisi dışarı çıkamaz |
| `subprocess`, `os.system`, `os.popen` | Uygulama içinde başka program çalıştırılmaz |
| `sys.exit`, `os._exit`, `quit()`, `exit()` | Uygulamayı kapatır |
| Kamera, mikrofon, seri port, pencere: `cv2.VideoCapture`, `cv2.imshow`, `serial`, `sounddevice`, `tkinter` | Donanıma ve arayüze yalnız uygulama erişir |
| Sunucu açmak: `uvicorn.run`, `flask`, `fastapi` | Port açılmaz; modül fonksiyon olarak çağrılır |
| `eval`, `exec`, `pickle.load` / `joblib.load` YABANCI dosyada | Kod çalıştırma riski; yalnız kendi ağırlık dosyanız |
| `torch.load(...)` `weights_only=True` olmadan | Güvensiz çözme |
| Girdi dışında dosyaya yazmak (görsel, CSV, günlük) | Uygulama görsel kaydetmez; her şey bellekte döner |

## 4. Ortam ve sınırlar

- **Python 3.10** ile çalışmalı (ana uygulamanın sürümü). `match` ifadesi ve 3.11+ sözdizimi yok.
- **numpy 1.26** ile uyumlu olmalı (numpy 2'ye özgü çağrı yok).
- **Yalnız CPU varsayın.** GPU varsa hızlanabilir ama zorunlu olamaz. Tercih: **ONNX** (`onnxruntime`, `CPUExecutionProvider`).
- **Süre:** sıradan bir dizüstünde tek girdi ≤ 10 sn; ilk yükleme ≤ 30 sn.
- **Belirlenimci:** aynı girdi → aynı çıktı (rastgelelik varsa tohum sabit).
- **Ağırlık boyutu:** her dosya ≤ 95 MB (GitHub 100 MB sınırı). Daha büyük model gerekiyorsa konu açın; dağıtım ekiple planlanır.
- **İçe aktarma yan etkisiz:** modülü `import` etmek model yüklemez, dosya yazmaz, ağa çıkmaz; ağır iş `Predictor.__init__`'te.

## 5. Açıklanabilirlik (isteğe bağlı ama teşvik edilir)

`predict()` dönüşüne `xai` eklenebilir:

```python
"xai": {
    "yontem": "Grad-CAM",                 # ya da "SHAP", "Integrated Gradients"
    "aciklanan_etiket": "Lezyon",          # TAHMİN EDİLEN etiket açıklanmalı
    "gorsel_png_base64": "...",            # isteğe bağlı, bellekte üretilir, DOSYAYA YAZILMAZ
    "ust_oznitelikler": [["ozellik", 0.31]]  # tablo modelleri için
}
```

⚠️ Bilinen hatalar (gerçek projede yaşandı): açıklama **tahmin edilen** sınıfı açıklamalı (hep aynı sınıfı değil); ısı haritası nesnenin üstünde
olmalı (siyah dolguda ya da görüntü dışında değil); tek örnek açıklaması sıfıra çökmemeli (arka plan = girdinin kendisi olmamalı); açıklama
yığına bağlı olmamalı (aynı örnek tek başına ve bir yığın içinde aynı açıklamayı almalı).

## 6. Testler

`tests/test_<modul_adi>.py` en az şunları içerir:
1. **Sözleşme testi:** `predict()` dönüşü §2'deki alanları ve türleri taşıyor.
2. **İki örnek girdi** (sentetik ya da açık lisanslı; `docs/veri-kurallari.md`) ve beklenen etiket.
3. **Kötü girdi:** bozuk / boş dosya → anlaşılır bir `ValueError` (uygulamayı çökertmez, `sys.exit` yok).

## 7. Model kartı

`MODEL_KARTI.md` (şablon: `sablonlar/model-karti.md`): veri kaynağı ve lisansı, eğitim yöntemi, doğrulama metrikleri (ayrı test kümesinde),
bilinen sınırlar, amaçlanan kullanım, kullanılmaması gereken durumlar. Metrikler kanıtsız yazılmaz.
