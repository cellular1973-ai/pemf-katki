# Öğrenci Rehberi — PEMF Vet'e adım adım katkı

Bu rehber, daha önce açık kaynak bir projeye katkı vermemiş biri için yazıldı. Sırayla okuyun ve sırayla yapın.

---

## 1. Proje ne, siz ne yapacaksınız?

**PEMF Vet**, veteriner kliniklerinde hayvanlara manyetik alan (PEMF) seansı uygulayan bir cihaz ve yazılımıdır. Hekim, uygulamanın
**AI Hub** ekranında yapay zekâ modüllerini kullanır: bir fotoğraf, ses kaydı ya da tahlil tablosu yükler, modül bir tahmin ve güven
değeri döndürür. Örneğin bir termal görüntüden "Sağlıklı / Hasta", bir kedi sesinden ruh hâli.

**Sahada çalışan sizsiniz**: cihazın ve AI modüllerinin gerçek hayvanlarda nasıl davrandığını ilk siz görürsünüz. Bu yüzden en değerli
katkılardan biri **düzeltme ve kalibrasyon önerileridir**: sahada ölçtüğünüz, gözlediğiniz bir sapmayı verisiyle getirirsiniz, ekip uygular
(§6). Ayrıca **yeni bir AI modülü** yazabilir (§5) ya da öneri, rapor şablonu, belge getirebilirsiniz (§7). Kabul edilen katkıyı proje ekibi
ana uygulamaya ekler; sürüm notlarında adınız geçer.

AI modülleri **karar desteğidir**: hekime bilgi verir, tek başına tanı koymaz, cihaza komut göndermez. Cihazın güvenliğiyle ilgili kısımlarda
(bobin sürüşü, ACİL DURDUR, firmware, ödeme) **kod** yazılmaz; oralarda gördüğünüz her şeyi düzeltme / kalibrasyon önerisi olarak getirin
(`KAPSAM.md`).

## 2. Neler yapabilirsiniz?

| İş | Ne teslim edersiniz | Zorluk |
|---|---|---|
| **Düzeltme / kalibrasyon önerisi** | Sahada ölçtüğünüz ya da gözlediğiniz sapma + verisi + önerdiğiniz değer (§6) | Kolay–orta |
| **Yeni AI modülü** | Eğitilmiş model (ONNX) + `predictor.py` + testler + model kartı | Orta–ileri |
| **Açıklanabilirlik (XAI)** | Modülünüzün kararını açıklayan ısı haritası ya da öznitelik listesi | İleri |
| **Öneri** | "Şu ekranda şu eksik / şu modül faydalı olur" — konu (issue) olarak | Kolay |
| **Rapor şablonu, belge, çeviri** | Markdown ya da HTML taslak — PR olarak | Kolay |

**Modül fikirleri** (önce konu açıp ekiple konuşun; aynı fikri iki kişi yapmasın):

| Girdi | Örnek fikir |
|---|---|
| Görüntü | deri lezyonu sınıflandırma · yara alanı ve iyileşme takibi · göz / kulak bulgusu · vücut kondisyon skoru |
| Ses | solunum sesi (normal / anormal) · öksürük türü |
| Tablo | kan tahlili değerlerinden böbrek / karaciğer risk tahmini |

## 3. Gerekenler

| Araç | Ne için | Nereden |
|---|---|---|
| **GitHub hesabı** | Depoyu kopyalamak (fork), değişiklik önermek (PR) | github.com |
| **Git** | Kodun sürümlerini yönetmek | git-scm.com (Windows: "Git for Windows") |
| **Python 3.10** | Modülün çalışacağı sürüm. Ana uygulama 3.10 kullanır; 3.11 / 3.12'ye özgü kod çalışmaz | python.org → Downloads → 3.10.x |
| **VS Code** | Kod düzenleyici; "Python" eklentisini kurun | code.visualstudio.com |
| GitHub Desktop *(isteğe bağlı)* | Git komutlarını bilmiyorsanız görsel arayüz | desktop.github.com |
| Google Colab / kendi GPU'nuz *(isteğe bağlı)* | Modeli eğitmek. Eğitim nerede yapılırsa yapılsın, teslim edilen modül CPU'da çalışmalı | colab.research.google.com |
| Netron *(isteğe bağlı)* | ONNX modelinizin girdi / çıktı adlarını görmek | netron.app |

Eğitimde istediğiniz kütüphaneyi (PyTorch, TensorFlow, scikit-learn, XGBoost) kullanabilirsiniz. **Teslimde** model **ONNX** biçiminde olur
ve `onnxruntime` ile çalışır; ayrıntılar `docs/model-hazirlama.md`'de.

## 4. Kurulum (bir kez)

Komutlar Windows için yazıldı (PowerShell ya da Komut İstemi). macOS / Linux farkları parantez içinde.

**4.1 Depoyu kendi hesabınıza kopyalayın (fork).** https://github.com/mert61-python/pemf-katki sayfasında sağ üstteki **Fork** düğmesine
basın. Hesabınızda `<kullanici_adiniz>/pemf-katki` oluşur. Bundan sonra kendi kopyanızda çalışırsınız.

**4.2 Kopyanızı bilgisayarınıza indirin:**
```powershell
git clone https://github.com/<kullanici_adiniz>/pemf-katki.git
cd pemf-katki
git remote add upstream https://github.com/mert61-python/pemf-katki.git
```
`upstream`, ana depoyu takip etmenizi sağlar (§10).

**4.3 Python ortamını kurun:**
```powershell
py -3.10 -m venv .venv
.venv\Scripts\activate                 # (macOS / Linux: source .venv/bin/activate)
python -m pip install -r requirements.txt
```
Komut satırının başında `(.venv)` görmelisiniz. Her yeni terminalde `activate` komutunu yeniden çalıştırın.

**4.4 Her şeyin çalıştığını görün:**
```powershell
python araclar\sozlesme_denetimi.py moduller\ornek_parlaklik
pytest
```
Beklenen: `GEÇTİ` ve `... passed`. Hata alırsanız §11'e bakın ya da Tartışmalar (Discussions) bölümünde sorun.

## 5. İlk modülünüz — adım adım

**5.1 Konu açın.** Depoda **Issues → New issue → Öneri**. Formu doldurun: hangi sorunu çözüyor, girdi türü, çıktı etiketleri, kullanacağınız
veri (saha / açık veri seti). Ekip "olur" deyip `ai-modulu` etiketini koyunca başlayın. Konunun numarasını not edin (ör. `#12`).

**5.2 Kendi dalınızı açın** (her iş için ayrı dal):
```powershell
git switch -c deri-lezyonu
```

**5.3 Örnek modülü kopyalayıp adını değiştirin:**
```powershell
xcopy /E /I moduller\ornek_parlaklik moduller\kedi_deri_lezyonu      # (macOS / Linux: cp -r moduller/ornek_parlaklik moduller/kedi_deri_lezyonu)
ren moduller\kedi_deri_lezyonu\tests\test_ornek_parlaklik.py test_kedi_deri_lezyonu.py
```
Modül adı: küçük harf, Türkçe karakter yok, kelimeler alt çizgiyle (`kedi_deri_lezyonu`).

**5.4 `predictor.py`'deki `MODUL_BILGISI`'ni güncelleyin:** `ad` klasör adıyla AYNI olmalı; `baslik` hekimin göreceği Türkçe ad; `etiketler`
modelinizin sınıfları; `yazarlar` adınız ve e-postanız.

**5.5 Modelinizi eğitin ve ONNX'e aktarın.** Eğitimi kendi ortamınızda (Colab olabilir) yapın. Model dosyasını `agirliklar\model.onnx` olarak
koyun ve SHA-256 özetini `MODUL_BILGISI["model_dosyalari"]`'na yazın. Nasıl yapılacağı ve hazır kod iskeleti: **`docs/model-hazirlama.md`**.
Büyük eğitim veri setini depoya koymayın; bağlantısını model kartına yazın (`docs/saha-verisi.md`).

**5.6 `predictor.py`'yi yazın.** `docs/model-hazirlama.md`'deki iskeleti kullanın. Kurallar `docs/ai-modul-sozlesmesi.md`'de; en önemlileri:
- ön işleme (boyut, normalizasyon) eğitimdekiyle **birebir aynı** olmalı;
- internete çıkmak, dosya yazmak, kamera açmak, `sys.exit` YASAK;
- dönüş: `{"label": ..., "confidence": ...}` ve isteğe bağlı `probabilities`, `details`, `warnings`.

**5.7 Testleri yazın** (`tests\test_kedi_deri_lezyonu.py`): örnek modüldeki üç test türü — sözleşme alanları, en az iki örnek girdi ve
beklenen etiket, bozuk girdide anlaşılır `ValueError`. Örnek girdiler küçük (≤ 1 MB) olmalı; sahadan örnek kullanabilirsiniz.

**5.8 Model kartını doldurun** (`MODEL_KARTI.md`, şablon: `sablonlar\model-karti.md`): veri kaynağı (saha / açık veri seti), eğitim / test ayrımı,
ayrı test kümesindeki metrikler ve nasıl hesaplandıkları, bilinen sınırlar.

**5.9 Yerelde denetleyin** — üçü de temiz olmadan PR açmayın:
```powershell
ruff check .
python araclar\sozlesme_denetimi.py moduller\kedi_deri_lezyonu
pytest
```

**5.10 Değişikliği kaydedip kopyanıza gönderin:**
```powershell
git add moduller\kedi_deri_lezyonu
git commit -m "kedi_deri_lezyonu: ilk sürüm (ONNX, 2 sınıf)"
git push -u origin deri-lezyonu
```

**5.11 Çekme isteği (PR) açın.** GitHub'da kendi kopyanızın sayfasında çıkan **Compare & pull request** düğmesine basın. Hedef:
`mert61-python/pemf-katki` deposunun `ana` dalı. Açıklamaya `Kapatır #12` yazın (konu numaranız) ve şablondaki denetim listesini işaretleyin.

**5.12 CI'ı izleyin.** PR sayfasında `denetim` adlı otomatik kontrol çalışır (ruff + denetleyici + testler). İlk PR'ınızda çalışması için
ekibin onayı gerekebilir; bekleyin. Kırmızı olursa **Details** bağlantısından hatayı okuyun, düzeltin, aynı dala yeniden `git push` yapın;
PR kendiliğinden güncellenir.

**5.13 İnceleme.** Ekip yorum yazar ya da değişiklik ister. Yanıtlayın, düzeltin, yeniden gönderin. Onaylanınca ekip birleştirir (merge).

**5.14 Sonrası.** Birleştirilen modülü ana uygulamaya ekip alır: kendi ortamında yeniden ölçer, uygulamanın güvenlik kurallarına uyarlar,
bağımsız bir incelemeden geçirir (`docs/entegrasyon.md`). Bu birkaç hafta sürebilir; sonucu konunuzda duyurulur.

## 6. Düzeltme ve kalibrasyon önerisi — adım adım

Sahada bir şeyin yanlış ya da kayık olduğunu gördüğünüzde: ölçün, veriyle belgeleyin, düzeltmeyi önerin. Cihazın ayarını kendiniz
değiştirmeyin; önerinizi ekip uygular.

**Neler önerilebilir? (örnekler)**

| Konu | Ne ölçülür / toplanır | Ne önerilir |
|---|---|---|
| AI modülü sahada yanılıyor | yanlış ve doğru sonuçlu örnekler: girdi + modelin sonucu + doğru sonuç | eşik değişikliği, yeniden eğitim için veri |
| Petri plakasının kabindeki konumu | A1 kuyucuğunun kabin koordinatı (x, y, z mm), plakanın yönü | yapılandırmadaki plaka konumu |
| Fantom eksen yönü | fantomun uzun / kısa ekseninin kabinde hangi yöne baktığı | eksen işareti |
| Yeşil halka çapı | şerit metreyle çap (bugün 184 mm varsayılıyor) | halka çapı değeri |
| Petri kanser renk eşikleri | kontrol kuyucuklarıyla (sağlıklı / kanserli bilinen) görüntüler | renk eşikleri |
| Kabin ve kamera | ArUco işaretinin yeri, kamera açısı, bilinen bir noktanın ölçülen ve uygulamanın gösterdiği konumu | kamera / kabin kalibrasyonu |
| Bobin | bobin direnci (multimetre), bobin merkezinde ölçülen alan (mT) ile uygulamanın gösterdiği değer | direnç değeri, alan düzeltme katsayısı |
| Sensör | sıcaklık / akım okumasının referans aletle karşılaştırması | sapma (offset) ve ölçek düzeltmesi |
| Arayüz | yanlış birim, yanlış etiket, anlaşılmayan uyarı (ekran görüntüsüyle) | doğru metin / birim |

**6.1 Konu açın:** Issues → **Düzeltme / kalibrasyon** formu. Ne gördüğünüzü, koşulları ve önerinizi kısaca yazın; küçük dosyaları
(fotoğraf, CSV) forma sürükleyip bırakabilirsiniz. Basit bir düzeltme için bu kadarı yeterlidir.

**6.2 Ölçüm ya da veri çoksa öneri klasörü hazırlayın:**
```powershell
git switch ana
git fetch upstream
git merge upstream/ana
git switch -c halka-capi
mkdir oneriler\2026-10-14-yesil-halka-capi\veri\ham
copy sablonlar\duzeltme-kalibrasyon.md oneriler\2026-10-14-yesil-halka-capi\README.md
```
Ölçüm dosyalarınızı `veri\ham\` altına koyun, `README.md`'yi doldurun: ne gördünüz, koşullar (tarih, cihaz, yazılım sürümü, ölçüm aleti),
veri, analiz, önerilen değer, ekip nasıl doğrulayabilir. Veriyi nasıl düzenleyeceğiniz: **`docs/saha-verisi.md`**.

**6.3 Gönderin ve PR açın** (§5.10–5.13 ile aynı): `git add oneriler\2026-10-14-yesil-halka-capi` → `git commit -m "yesil halka capi: olcum
ve oneri"` → `git push -u origin halka-capi` → PR, açıklamaya `Kapatır #<konu>`.

**6.4 Sonrası:** ekip ölçümünüzü inceler (gerekirse tekrar ettirir), öneriyi ana uygulamaya ayar ya da düzeltme olarak işler ve konuda
duyurur.

**Ölçüm yaparken:** cihaz çalışırken ölçüyorsanız ACİL DURDUR elinizin altında olsun; seans ve cihaz ayarlarını ölçüm için değiştirmeniz
gerekiyorsa hekim / sorumlu kişiyle birlikte yapın.

## 7. Öneri, rapor şablonu, belge

- **Öneri:** Issues → Öneri formu. Ekran önerisiyse bir taslak çizimi (kâğıt fotoğrafı da olur) ya da ekran görüntüsü ekleyin.
- **Rapor şablonu / belge / çeviri:** `docs\` altında yeni bir Markdown dosyası olarak yazın, §5.10–5.13'teki gibi PR açın.

## 8. Kurallar (özet)

1. **Kod katkısı alınmayan alanlarda** (`KAPSAM.md`) kod yazmayın; oralar için düzeltme / kalibrasyon önerisi getirin.
2. **Sır yok** — parola, API anahtarı, jeton commit'lenmez.
3. **Dosya boyutu** — model dosyası ≤ 95 MB; tek veri dosyası ≤ 50 MB; testlerdeki örnek girdiler ≤ 1 MB.
4. **Başka kaynaktan aldığınız kod, model ya da veri** — kaynağını yazın.

## 9. Git'te sık kullanılanlar

| Ne yapmak istiyorsunuz | Komut |
|---|---|
| Hangi dosyalar değişti? | `git status` |
| Ne değiştirdim? | `git diff` |
| Yeni dal | `git switch -c <ad>` |
| Dallar arasında geçiş | `git switch <ad>` |
| Kaydet | `git add <dosya>` → `git commit -m "mesaj"` |
| Kopyanıza gönder | `git push` |
| Son commit mesajını düzelt (henüz push etmediyseniz) | `git commit --amend` |

## 10. Kopyanızı ana depoyla güncel tutmak

Başkalarının katkıları ana depoya girdikçe kopyanız geride kalır. Yeni bir işe başlamadan önce:
```powershell
git switch ana
git fetch upstream
git merge upstream/ana
git push
git switch -c yeni-is
```
Açık bir PR'ınız varken ana depo değiştiyse ve GitHub "çakışma var" diyorsa: `git switch <dalınız>` → `git merge ana` → çakışan dosyaları
VS Code'da düzeltin → `git add` → `git commit` → `git push`.

## 11. Denetleyici ne dedi, ne yapmalı?

| Mesaj | Anlamı | Çözüm |
|---|---|---|
| `yasaklı içe aktarma requests / urllib / socket` | Ağa çıkmaya çalışıyorsunuz | Modeli internetten indirmeyin; ağırlık `agirliklar\` altında olmalı |
| `yasaklı çağrı sys.exit` | Hata olunca programı kapatıyorsunuz | `raise ValueError("Türkçe açıklama")` kullanın |
| `torch.load weights_only=True olmadan` | PyTorch modeli güvensiz yükleniyor | Modeli ONNX'e çevirin (önerilen) |
| `dosyaya yazma open(..., 'w')` / `cv2.imwrite` | Sonucu dosyaya kaydediyorsunuz | Her şeyi sözlükte döndürün; görsel gerekirse bellekte base64 |
| `MODUL_BILGISI['ad'] klasör adıyla aynı değil` | Kopyalarken ad değişmedi | `ad`'ı klasör adıyla aynı yapın |
| `SHA-256 uyuşmuyor` | Modeli değiştirdiniz ama özeti güncellemediniz | Özeti yeniden hesaplayın (`docs/model-hazirlama.md`) |
| `dönüş katı JSON değil` | numpy sayısı ya da NaN döndü | `float(x)`, `int(x)`, `.tolist()` kullanın; NaN üretmeyin |
| `belirlenimci değil` | Aynı girdi iki kez farklı sonuç verdi | Rastgeleliği kaldırın (dropout eğitimde kalmalı; `model.eval()` ile dışa aktarın) |
| `predict() X sn > 10 sn` | Çok yavaş | Daha küçük model, daha küçük girdi boyutu ya da nicemleme (quantization) |
| `label ... etiketler içinde değil` | Döndürdüğünüz etiket listede yok | `MODUL_BILGISI["etiketler"]` ile aynı yazımı kullanın |

## 12. Sık sorulanlar

- **GPU şart mı?** Hayır. Eğitimi GPU'da (Colab) yapabilirsiniz; teslim edilen modül CPU'da çalışmalı.
- **Python 3.12 ile eğitebilir miyim?** Evet. Ama `predictor.py` Python 3.10 ve numpy 1.26 ile çalışmalı; denetleyiciyi 3.10 ortamında koşun.
- **PyTorch `.pt` dosyası teslim edebilir miyim?** Hayır, ONNX'e çevirin (`docs/model-hazirlama.md`).
- **Modelim 95 MB'tan büyük.** Daha küçük bir mimari ya da nicemleme deneyin; olmuyorsa konunuzda yazın.
- **Veri nereden bulurum?** En değerlisi sahada kendi topladığınız veri (`docs/saha-verisi.md`). Eğitim için yetmezse açık veri setleri
  (Kaggle, Zenodo, makale ekleri) ile tamamlayın; kaynağını model kartına yazın.
- **Cihazın bir ayarını değiştirmek gerekiyor.** Kendiniz değiştirmeyin; ölçümünüzle düzeltme / kalibrasyon önerisi açın (§6), ekip uygular.
- **Takıldım.** Discussions bölümünde soru açın ya da konunuza yorum yazın.
