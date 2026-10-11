# Model Kartı — Örnek: Parlaklık

| | |
|---|---|
| Modül adı | `ornek_parlaklik` |
| Sürüm | 0.1.0 |
| Yazarlar | PEMF Vet ekibi |
| Girdi | herhangi bir görüntü (PNG / JPEG) |
| Çıktı | "Karanlık" / "Aydınlık" |

## Amaçlanan kullanım
**Yalnız sözleşmeyi göstermek için.** Tanı yapmaz; kendi modülünüz için kopyalanacak iskelettir.

## Kullanılmaması gereken durumlar
Her türlü klinik kullanım.

## Veri
Eğitim verisi yok; kural tabanlı (ortalama gri düzey + lojistik eğri). Testler kodla üretilen tek renkli görüntülerle koşar.

## Yöntem
Görüntü gri tonlamaya çevrilir, ortalama parlaklık 0–1 aralığında hesaplanır, `1 / (1 + e^(-12 (x - 0.5)))` ile "Aydınlık" olasılığına çevrilir.

## Sonuçlar
Uygulanmaz (öğretici örnek).

## Bilinen sınırlar
Görüntünün içeriğine bakmaz. Neredeyse tek renkli görüntüde uyarı üretir.

## Ağırlık dosyaları
Yok.
