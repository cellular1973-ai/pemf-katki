# Model Kartı — <Modül başlığı>

| | |
|---|---|
| Modül adı | `<modul_adi>` |
| Sürüm | 0.1.0 |
| Yazarlar | Ad Soyad (kurum) |
| Girdi | görüntü / ses / tablo — biçim, çözünürlük, örnekleme hızı |
| Çıktı | etiketler ve anlamları |

## Amaçlanan kullanım
Hangi hayvan, hangi soru, kim kullanır. **Karar desteğidir; tek başına tanı koymaz, doz ya da cihaz ayarı önermez.**

## Kullanılmaması gereken durumlar
Model nerede yanılır ya da hiç denenmedi (tür, yaş, çekim koşulu …).

## Veri
- Kaynak: saha verisi (nerede, ne zaman, hangi cihazla toplandı) ve / veya açık veri seti (bağlantı).
- Örnek sayısı, sınıf dağılımı, eğitim / doğrulama / test ayrımı (aynı hayvan iki kümede olmamalı).
- Etiketleri kim belirledi (hekim, laboratuvar sonucu …).

## Yöntem
Mimari, ön işleme, eğitim ayarları, ONNX'e aktarma.

## Sonuçlar (ayrı test kümesinde)
| Ölçüt | Değer |
|---|---|
| Doğruluk | |
| Duyarlılık / özgüllük (sınıf başına) | |
| AUC | |

Sayıların nasıl üretildiği (betik / not defteri) ve kanıtı. Kanıtsız metrik yazılmaz.

## Bilinen sınırlar ve önyargılar

## Açıklanabilirlik (varsa)
Yöntem; tahmin edilen sınıfı açıkladığını nasıl doğruladınız.

## Ağırlık dosyaları
| Dosya | Boyut | SHA-256 |
|---|---|---|
