# Katkı kılavuzu (kısa)

Ayrıntılı, adım adım anlatım: [`OGRENCI-REHBERI.md`](OGRENCI-REHBERI.md).

## Başlamadan
- `README.md`, `KAPSAM.md` ve `docs/veri-kurallari.md`'yi okuyun.
- Bir işe başlamadan önce **konu (issue)** açın ve ekibin "olur" demesini bekleyin. Aynı işi iki kişinin yapmasını önler.
- `iyi-ilk-is` etiketli konular başlamak için uygundur.

## Çalışma düzeni
1. Depoyu **fork**'layın; kopyanızı indirin; ana depoyu `upstream` olarak ekleyin.
2. Her iş için ayrı dal açın: `git switch -c <kisa-konu>`.
3. Küçük, anlamlı commit'ler atın. Mesaj Türkçe ve ne yaptığını söylesin: `kedi_deri_lezyonu: bulanık görüntüde uyarı eklendi`.
4. Yerelde koşun — üçü de temiz olmadan PR açmayın:
   ```powershell
   ruff check .
   python araclar\sozlesme_denetimi.py moduller\<modul_adi>
   pytest
   ```
5. Kopyanıza push edin, ana deponun `ana` dalına **çekme isteği (PR)** açın; şablondaki kutuları doldurun; açıklamaya `Kapatır #<konu>` yazın.
6. CI (`denetim`) yeşil olmalı. İnceleme yorumlarını yanıtlayın; onaylanan PR ekip tarafından birleştirilir.

## Kurallar
- **Gerçek hasta verisi yok.** Sentetik ya da açık lisanslı veri (`docs/veri-kurallari.md`).
- **Sır yok:** parola, API anahtarı, jeton commit'lenmez.
- **Kapsam dışı alanlara** (`KAPSAM.md`) dokunan PR'lar kapatılır.
- Başkasının kodunu ya da modelini kullanıyorsanız lisansını ve kaynağını model kartına yazın.
- Saygılı ve yapıcı olun; inceleme kişiye değil koda yapılır.

## Sorular
Discussions bölümünde soru açın ya da konunuza yorum yazın.
