# Katkınız ana uygulamaya nasıl girer?

Bu depodaki bir katkı kabul edildiğinde ana uygulamaya **proje ekibi** alır. Süreç, dış kaynaklı AI paketlerinin entegrasyonunda kullanılan
yöntemin aynısıdır:

1. **Ölçüm:** modül, ana uygulamanın ortamında (Python 3.10, yalnız CPU, internetsiz) sizin testlerinizle ve ekibin kendi örnekleriyle koşturulur.
   "Model kartında yazıyor" kanıt sayılmaz; metrikler yeniden ölçülür.
2. **Uyarlama, kopyalama değil:** dosyalarınız olduğu gibi kopyalanmaz. Ana uygulamanın güvenlik kuralları (kod koruması, model dosyası çözümü,
   bellek içi görsel, zaman sınırı, kilitler) modülün çevresine eklenir. Modülün kendi mantığı korunur.
3. **Arayüz bağlantısı:** AI Hub'daki kart, girdi formu ve sonuç ekranı ekip tarafından eklenir. Arayüz için öneriniz varsa konu açın.
4. **Bağımsız inceleme:** entegrasyonu yazmayan bir inceleme, modülün kurallara uyduğunu ve uygulamanın geri kalanını bozmadığını doğrular.
5. **Yayın:** modül bir sonraki sürümle sahaya gider; sürüm notlarında ve model kartında adınız yer alır.

Sizden istenen: denetleyiciden geçen, testleri olan, model kartı dolu bir modül ve inceleme sorularına yanıt.
