# Katkı kılavuzu

## Başlamadan
- `README.md`, `KAPSAM.md` ve `docs/veri-kurallari.md`'yi okuyun.
- Büyük bir işe başlamadan önce **konu (issue)** açın ve ekibin "olur" demesini bekleyin. Aynı işi iki kişinin yapmasını önler.
- `iyi-ilk-is` etiketli konular başlamak için uygundur.

## Çalışma düzeni
1. Konuyu kendinize atayın (ya da yorumla isteyin).
2. `ana` dalından kendi dalınızı açın: `ogrenci/<kullanici>/<kisa-konu>`.
3. Küçük, anlamlı commit'ler atın. Commit mesajı Türkçe ve ne yaptığını söylesin: `kedi_deri_lezyonu: belirsiz görüntüde uyarı eklendi`.
4. Yerelde koşun:
   ```bash
   ruff check .
   python araclar/sozlesme_denetimi.py moduller/<modul_adi>
   pytest
   ```
5. Çekme isteği (PR) açın; şablondaki kutuları doldurun. CI aynı denetimleri koşar.
6. İnceleme yorumlarını yanıtlayın. Onaylanan PR `ana`ya birleştirilir; ana uygulamaya alma ayrı bir adımdır (`docs/entegrasyon.md`).

## Kurallar
- **Gerçek hasta verisi yok.** Sentetik ya da açık lisanslı veri (`docs/veri-kurallari.md`).
- **Sır yok:** parola, API anahtarı, jeton, kişisel e-posta listesi commit'lenmez.
- **Kapsam dışı alanlara** (`KAPSAM.md`) dokunan PR'lar kapatılır.
- Başkasının kodunu kullanıyorsanız lisansını ve kaynağını model kartına yazın; lisansı uyumsuz kod alınmaz.
- Saygılı ve yapıcı olun; inceleme kişiye değil koda yapılır.

## Sorular
Konu açın ya da Tartışmalar (Discussions) bölümünü kullanın.
