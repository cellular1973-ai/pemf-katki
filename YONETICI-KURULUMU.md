# Yönetici kurulumu (proje sahibi için)

Bu depo yerelde hazırlandı; GitHub'a yükleme ve ayarlar sahip tarafından yapılır.

## 1. Organizasyon ve depo
1. GitHub'da ücretsiz bir **organizasyon** açın (ör. `pemf-vet-katki`). Öğrenciler kişisel hesabınıza değil organizasyona davet edilir.
2. Organizasyonda **gizli (private)** depo oluşturun: `pemf-katki`. Varsayılan dal: `ana`.
3. Bu klasörü yükleyin:
   ```bash
   git remote add origin https://github.com/<organizasyon>/pemf-katki.git
   git push -u origin ana
   ```

## 2. Erişim
- **Takımlar:** `ogrenciler` (Write — yalnız bu depo) · `ekip` (Maintain). Ana uygulama deposuna öğrenci erişimi YOK.
- Davet etmeden önce katkı sözleşmesi imzalanır (`KATKI-SOZLESMESI-TASLAK.md`, hukukçu onayından sonra).
- Ayrılan öğrencinin erişimi takımdan çıkarılarak kapatılır.

## 3. Dal koruması (`ana`)
Settings → Branches → kural: **Require a pull request** · **Require approvals: 1** · **Require review from Code Owners** · **Require status checks:
`denetim`** · **Do not allow bypassing** · force-push ve silme kapalı.

## 4. Actions
- Settings → Actions → **Fork pull request workflows**: onay gereksin. Depoya **hiçbir gizli anahtar (secret) eklenmez.**
- Bu deponun CI'ı yalnız Linux'ta ~1–2 dk; gizli depoda dakika sınırını zorlamaz.

## 5. Topluluk
- **Discussions** açın (sorular, fikirler). **Projects** panosu: Öneri → Kabul → Yapılıyor → İncelemede → Ana uygulamaya alındı.
- Etiketler: `oneri`, `hata`, `iyi-ilk-is`, `ai-modulu`, `kapsam-disi`, `entegre-edildi`.
- Ders kapsamındaysa **GitHub Classroom** bu depodan ödev şablonu üretebilir.

## 6. Ana uygulamaya alma
Kabul edilen modül ana depoya `docs/entegrasyon.md`'deki yöntemle alınır: koordinatör bir entegrasyon oturumu açar (yama, kopya değil),
ardından bağımsız inceleme. Hoca paketinin entegrasyonu (AI-1 / AI-2) bunun ilk örneği.
