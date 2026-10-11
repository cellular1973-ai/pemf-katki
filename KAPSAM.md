# Kapsam — neye katkı alınır, neye alınmaz

PEMF Vet gerçek hayvanlara manyetik alan uygulayan bir cihazı yönetir. Bazı alanlar hasta güvenliği, kişisel veri ya da ticari güvenlik
nedeniyle **yalnız proje ekibinde** kalır. Bu alanlara dokunan katkı önerileri kibarca reddedilir — sizinle ilgili değil, cihazın güvenliğiyle
ilgili.

## Katkı alınan alanlar

- **AI tanı modülleri** — görüntü, ses ya da tablo verisinden tahmin üreten, `docs/ai-modul-sozlesmesi.md`'ye uyan bağımsız paketler.
- **Açıklanabilirlik (XAI)** — modülün kendi kararını açıklayan, bellekte üretilen görsel ya da öznitelik listesi.
- **Rapor şablonları, belgeler, çeviriler, terimler.**
- **Arayüz önerileri** — ekran taslakları, kullanılabilirlik ve erişilebilirlik bulguları (kod değil, öneri olarak).
- **Test verisi** — `docs/veri-kurallari.md`'ye uyan sentetik ya da açık lisanslı veri.

## Katkı ALINMAYAN alanlar

| Alan | Neden |
|---|---|
| Bobin sürüşü, doz (frekans, duty, alan şiddeti) hesabı ve sınırları | Hayvanın aldığı enerjiyi doğrudan belirler |
| ACİL DURDUR ve her türlü durdurma yolu | Hasta güvenliği; hiçbir koşula bağlanamaz |
| Firmware (STM32, ESP) ve donanım iletişimi | Donanıma doğrudan yazar |
| AI çıktısından bobine giden yol (AI Pro kapalı döngüsü) | AI önerisi ancak hekim onayıyla ve proje içi güvenlik kapılarından geçerek kullanılır |
| Kimlik doğrulama, yetki, şifreleme, sırlar, lisans / jeton / ödeme | Kişisel veri ve ticari güvenlik |
| Güncelleme ve paketleme hattı | Sahadaki cihazlara yazılım dağıtır |
| Gerçek hasta verisi | KVKK; bu depoya hiçbir biçimde girmez |

**AI modülleri karar desteğidir.** Bir modülün çıktısı hekime gösterilir; tek başına tedavi ya da cihaz komutu üretmez. Modülünüz doz, bobin ya
da cihaz ayarı önermemelidir.
