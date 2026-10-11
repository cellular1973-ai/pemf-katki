# Kapsam — neye katkı alınır, neye alınmaz

PEMF Vet gerçek hayvanlara manyetik alan uygulayan bir cihazı yönetir. Bazı alanlarda **kod** yalnız proje ekibinde kalır; ama **her alanda,
ölçüme dayalı düzeltme ve kalibrasyon önerisi** alınır — onu uygulamak ekibin işidir.

## Katkı alınan alanlar

- **Düzeltme ve kalibrasyon önerileri** — sahada ölçtüğünüz ya da gözlediğiniz bir hata, sapma ya da yanlış ayar; verisi ve önerilen düzeltmeyle
  (`docs/saha-verisi.md`, `sablonlar/duzeltme-kalibrasyon.md`). Cihaz parametreleri dahil her konu.
- **AI tanı modülleri** — görüntü, ses ya da tablo verisinden tahmin üreten, `docs/ai-modul-sozlesmesi.md`'ye uyan bağımsız paketler.
- **Açıklanabilirlik (XAI)** — modülün kendi kararını açıklayan, bellekte üretilen görsel ya da öznitelik listesi.
- **Rapor şablonları, belgeler, çeviriler, terimler.**
- **Arayüz önerileri** — ekran taslakları, kullanılabilirlik ve erişilebilirlik bulguları (kod değil, öneri olarak).

## KOD katkısı alınmayan alanlar

Bu alanlarda kod yazmayın; gördüğünüz sorunu ya da ölçtüğünüz değeri **düzeltme / kalibrasyon önerisi** olarak getirin.

| Alan | Neden |
|---|---|
| Bobin sürüşü, doz (frekans, duty, alan şiddeti) hesabı ve sınırları | Hayvanın aldığı enerjiyi doğrudan belirler |
| ACİL DURDUR ve her türlü durdurma yolu | Hasta güvenliği; hiçbir koşula bağlanamaz |
| Firmware (STM32, ESP) ve donanım iletişimi | Donanıma doğrudan yazar |
| AI çıktısından bobine giden yol (AI Pro kapalı döngüsü) | AI önerisi ancak hekim onayıyla ve proje içi güvenlik kapılarından geçerek kullanılır |
| Kimlik doğrulama, yetki, şifreleme, sırlar, jeton / ödeme | Erişim ve ticari güvenlik |
| Güncelleme ve paketleme hattı | Sahadaki cihazlara yazılım dağıtır |

**AI modülleri karar desteğidir.** Bir modülün çıktısı hekime gösterilir; tek başına tedavi ya da cihaz komutu üretmez. Modülünüz doz, bobin ya
da cihaz ayarı önermemelidir (cihaz ayarı önerileri düzeltme / kalibrasyon önerisi olarak gelir).
