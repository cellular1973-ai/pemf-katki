# PEMF Vet — Katkı Deposu

PEMF Vet, veteriner kliniklerinde kullanılan bir manyetik alan (PEMF) seans sistemidir: masaüstü uygulama, mobil uygulama, yapay zekâ
destekli tanı modülleri ve bobinleri süren donanım. Bu depo, projeye **öğrencilerin ve dış katkıcıların** güvenle katkı vermesi için
hazırlandı. Ana uygulamanın kaynak kodu burada **yok**; katkılar tanımlı sözleşmeler üzerinden yapılır ve proje ekibi tarafından
incelenerek ana uygulamaya alınır.

## Neye katkı verebilirsiniz?

| Alan | Örnek | Nereden başlanır |
|---|---|---|
| **Yapay zekâ modülleri** | Yeni bir tanı modeli (görüntü, ses ya da tablo verisi), mevcut bir modelin iyileştirilmesi | `docs/ai-modul-sozlesmesi.md`, `moduller/ornek_parlaklik/` |
| **Açıklanabilirlik (XAI)** | Bir modelin kararını açıklayan ısı haritası ya da öznitelik katkısı | Sözleşmenin "XAI" bölümü |
| **Rapor şablonları** | Seans raporu, AI analiz raporu taslakları | Konu açarak öneri |
| **Arayüz önerileri** | Ekran taslağı, kullanılabilirlik bulgusu, erişilebilirlik | "Öneri" konu şablonu |
| **Belgeler ve çeviri** | Kullanım kılavuzu, terimler | Konu açarak öneri |

Neye **katkı alınmaz** (güvenlik gereği): `KAPSAM.md`.

## Hızlı başlangıç (AI modülü)

```bash
python -m venv .venv && .venv\Scripts\activate        # Windows (Linux/macOS: source .venv/bin/activate)
pip install -r requirements.txt
python araclar/sozlesme_denetimi.py moduller/ornek_parlaklik   # örnek modül sözleşmeye uyuyor mu?
pytest
```

Kendi modülünüz için örnek modülü (`moduller/ornek_parlaklik/`) `moduller/<modul_adi>/` olarak kopyalayın, `docs/ai-modul-sozlesmesi.md`'yi izleyin ve
denetleyiciyi kendi modülünüzde koşturun.

## Katkı nasıl ilerler?

1. Bir **konu (issue)** açın: öneri ya da hata şablonuyla. Büyük işlere başlamadan önce ekiple konuşun.
2. Kendi dalınızda çalışın, **çekme isteği (PR)** açın. CI denetleyiciyi ve testleri koşar.
3. Proje ekibi inceler. Kabul edilen katkı ana uygulamaya **ekip tarafından** alınır: dosya olduğu gibi kopyalanmaz, uygulamanın güvenlik ve
   paketleme kurallarına uyarlanır ve bağımsız bir incelemeden geçer (`docs/entegrasyon.md`).
4. Katkınız sürüm notlarında ve modülün model kartında adınızla anılır.

Ayrıntılar: `KATKI.md`. Veri kuralları: `docs/veri-kurallari.md` — **gerçek hasta verisi bu depoya ASLA girmez.**

## Hukuki not

Bu depo özeldir; içeriği paylaşılmaz. Katkılar `KATKI-SOZLESMESI-TASLAK.md`'deki koşullara tabidir (taslak — imzalanmadan önce danışmanınız ve
üniversitenizin ilgili birimiyle gözden geçirilmelidir).
