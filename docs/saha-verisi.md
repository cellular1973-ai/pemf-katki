# Saha verisi: nasıl toplanır, nasıl paylaşılır

Sahada topladığınız veri (fotoğraf, ses, ölçüm, cihaz günlüğü, ekran görüntüsü, seans kaydı) düzeltme ve kalibrasyon önerilerinin
kanıtıdır. Veri ne kadar iyi belgelenirse öneri o kadar hızlı uygulanır.

## 1. Nereye konur?

- **Küçük veri** (her dosya ≤ 50 MB; GitHub tek dosyada 100 MB'ı kabul etmez): önerinizin klasörüne, `oneriler/<YYYY-AA-GG>-<kisa-konu>/veri/`.
- **Büyük veri seti** (yüzlerce dosya, GB'lar): Google Drive / OneDrive gibi bir yere yükleyin, bağlantıyı önerinizin `README.md`'sine yazın.
  Depoya yalnız birkaç temsilî örnek koyun.

## 2. Her ölçümün bağlamı

Aynı değer farklı koşulda farklı anlama gelir. Her veri için şunları yazın (önerinin `README.md`'sinde tablo ya da `veri/bilgi.csv`):

| Bilgi | Örnek |
|---|---|
| Tarih ve saat | 2026-10-14 10:35 |
| Cihaz / kabin | Klinik kabini, cihaz no (Ayarlar → Sistem Bilgileri → Cihaz ID) |
| Yazılım sürümü | Ayarlar → Sistem Bilgileri → Yazılım Sürümü (ör. v1.9.50) |
| Firmware / kart | biliyorsanız kart açılış satırı (ör. "DDS v2.3") |
| Ölçüm aleti ve hassasiyeti | şerit metre (±1 mm), multimetre, osiloskop, gaussmetre, termometre |
| Ortam | ışık, oda sıcaklığı, kamera açısı / mesafesi |
| Kim ölçtü, kaç tekrar | 3 tekrar, ortalama ± sapma |

## 3. Biçimler

- **Görüntü:** JPEG / PNG, orijinal çözünürlükte, kırpmadan ve filtre uygulamadan.
- **Ses:** WAV (sıkıştırmasız) ya da cihazın verdiği biçim.
- **Ölçüm:** CSV; sütun adında birim: `alan_mT`, `sicaklik_C`, `direnc_ohm`, `mesafe_mm`.
- **Günlük / ekran görüntüsü:** olduğu gibi (`.log`, `.txt`, `.png`).

## 4. AI sonucunu düzeltmek için etiketli örnek

Bir AI modülü sahada yanılıyorsa en değerli veri, **modelin dediği** ile **doğru sonucun** yan yana olduğu örneklerdir:

```
oneriler/2026-10-14-termal-yanlis-hasta/veri/
├── goruntuler/            # modele verilen girdiler
└── etiketler.csv          # dosya, model_sonucu, model_guveni, dogru_sonuc, kim_belirledi, not
```

Hem yanlış hem doğru bilinen örnekleri ekleyin; yalnız yanlışlar, modelin nerede iyi olduğunu göstermez. Birkaç düzine örnek eşik ayarı için,
yüzlerce örnek yeniden eğitim için işe yarar.

## 5. Ham veriye dokunmayın

Ham veriyi `veri/ham/` altında olduğu gibi bırakın. İşlediyseniz (kırpma, ortalama alma, birim çevirme) sonucu `veri/islenmis/` altına koyun
ve nasıl işlediğinizi (betik ya da adım adım) yazın.

## 6. Başka kaynaktan veri

Açık bir veri seti ya da başka birinin ölçümünü kullandıysanız kaynağını (bağlantı, makale) yazın.
