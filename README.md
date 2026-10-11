# PEMF Vet — Katkı Deposu

PEMF Vet, veteriner kliniklerinde kullanılan bir manyetik alan (PEMF) seans sistemidir: masaüstü uygulama, mobil uygulama, yapay zekâ
destekli tanı modülleri ve bobinleri süren donanım. Bu depo, projeye **öğrencilerin ve dış katkıcıların** katkı vermesi için hazırlandı.
Ana uygulamanın kaynak kodu burada **yok**; katkılar tanımlı kurallar üzerinden yapılır ve proje ekibi tarafından incelenerek ana
uygulamaya alınır.

> **Yeni misiniz? Buradan başlayın → [`OGRENCI-REHBERI.md`](OGRENCI-REHBERI.md)** — ne yapacağınızı, hangi araçları nasıl kullanacağınızı ve
> ilk katkınızı adım adım anlatır.

## Neye katkı verebilirsiniz?

| Alan | Örnek | Belge |
|---|---|---|
| **Yapay zekâ modülleri** | Yeni bir tanı modeli (görüntü, ses ya da tablo verisi) | [`docs/ai-modul-sozlesmesi.md`](docs/ai-modul-sozlesmesi.md), [`docs/model-hazirlama.md`](docs/model-hazirlama.md) |
| **Açıklanabilirlik (XAI)** | Modelin kararını açıklayan ısı haritası ya da öznitelik katkısı | Sözleşme §5 |
| **Rapor şablonları, belgeler, çeviri** | Seans raporu taslağı, kullanım kılavuzu | `docs/` altına PR |
| **Öneri** | Ekran taslağı, eksik özellik, kullanılabilirlik bulgusu | Issues → Öneri |

Neye **katkı alınmaz** (güvenlik gereği): [`KAPSAM.md`](KAPSAM.md).

## Depoda ne var?

| Yol | İçerik |
|---|---|
| `OGRENCI-REHBERI.md` | Adım adım başlangıç rehberi |
| `KATKI.md` | Çalışma düzeni ve kurallar (kısa) |
| `KAPSAM.md` | Katkı alınan / alınmayan alanlar |
| `docs/ai-modul-sozlesmesi.md` | Bir AI modülünün uyması gereken kurallar |
| `docs/model-hazirlama.md` | Eğitimden ONNX'e, ONNX'ten `predictor.py`'ye; ana uygulamanın paket sürümleri |
| `docs/veri-kurallari.md` | Hangi veri kullanılabilir (gerçek hasta verisi ASLA) |
| `docs/entegrasyon.md` | Kabul edilen katkı ana uygulamaya nasıl girer |
| `araclar/sozlesme_denetimi.py` | Modülünüzü kurallara karşı otomatik denetler |
| `moduller/ornek_parlaklik/` | Kopyalayıp kullanacağınız çalışan örnek modül |
| `sablonlar/model-karti.md` | Model kartı şablonu |

## Hızlı başlangıç

```powershell
py -3.10 -m venv .venv
.venv\Scripts\activate                                            # macOS / Linux: source .venv/bin/activate
python -m pip install -r requirements.txt
python araclar\sozlesme_denetimi.py moduller\ornek_parlaklik      # beklenen: GEÇTİ
pytest                                                            # beklenen: ... passed
```

## Katkı nasıl ilerler?

1. **Konu (issue) açın** — öneri ya da hata şablonuyla. Ekip "olur" deyince başlayın.
2. Depoyu **fork**'layın, kendi kopyanızda bir dal açıp çalışın, **çekme isteği (PR)** açın. `denetim` CI'ı denetleyiciyi ve testleri koşar.
3. Proje ekibi inceler ve birleştirir. Kabul edilen katkı ana uygulamaya ekip tarafından alınır (`docs/entegrasyon.md`).
4. Katkınız sürüm notlarında ve modülün model kartında adınızla anılır.

**Gerçek hasta verisi bu depoya ASLA girmez** — [`docs/veri-kurallari.md`](docs/veri-kurallari.md). Bu depo herkese açıktır.
