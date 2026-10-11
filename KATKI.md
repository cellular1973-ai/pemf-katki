# Katkı kılavuzu (kısa)

Ayrıntılı, adım adım anlatım: [`OGRENCI-REHBERI.md`](OGRENCI-REHBERI.md).

## Başlamadan
- `README.md` ve `KAPSAM.md`'yi okuyun.
- Bir işe başlamadan önce **konu (issue)** açın: **Düzeltme / kalibrasyon** (sahada ölçtüğünüz sapma) ya da **Öneri** (yeni modül, rapor,
  arayüz). Ekip "olur" deyince başlayın; aynı işi iki kişinin yapmasını önler.
- `iyi-ilk-is` etiketli konular başlamak için uygundur.

## Çalışma düzeni
1. Depoyu **fork**'layın; kopyanızı indirin; ana depoyu `upstream` olarak ekleyin.
2. Her iş için ayrı dal açın: `git switch -c <kisa-konu>`.
3. Küçük, anlamlı commit'ler atın. Mesaj Türkçe ve ne yaptığını söylesin: `yesil halka capi: olcum ve oneri`.
4. AI modülüyse yerelde koşun — üçü de temiz olmadan PR açmayın:
   ```powershell
   ruff check .
   python araclar\sozlesme_denetimi.py moduller\<modul_adi>
   pytest
   ```
   Düzeltme / kalibrasyon önerisiyse: `oneriler\<YYYY-AA-GG>-<konu>\README.md` dolu, ham veri `veri\ham\` altında (`docs/saha-verisi.md`).
5. Kopyanıza push edin, ana deponun `ana` dalına **çekme isteği (PR)** açın; şablondaki kutuları doldurun; açıklamaya `Kapatır #<konu>` yazın.
6. CI (`denetim`) yeşil olmalı. İnceleme yorumlarını yanıtlayın; onaylanan PR ekip tarafından birleştirilir.

## Kurallar
- **Kod katkısı alınmayan alanlarda** (`KAPSAM.md`) kod yazmayın; oralar için düzeltme / kalibrasyon önerisi getirin.
- **Cihaz ayarlarını kendiniz değiştirmeyin;** önerin, ekip uygular.
- **Sır yok:** parola, API anahtarı, jeton commit'lenmez.
- Başka kaynaktan aldığınız kod, model ya da veri için kaynağını yazın.
- Saygılı ve yapıcı olun; inceleme kişiye değil koda yapılır.

## Sorular
Discussions bölümünde soru açın ya da konunuza yorum yazın.
