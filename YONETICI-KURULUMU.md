# Yönetici kurulumu (proje sahibi için)

## Kurulu olanlar (2026-10-11)
- Depo: **https://github.com/mert61-python/pemf-katki** — **gizli**, varsayılan dal `ana`.
- **Dal koruması (`ana`):** PR zorunlu · 1 onay · kod sahibi (`@mert61-python`) onayı · `denetim` CI'ı geçmeli ve dal güncel olmalı · yeni commit gelince
  eski onay düşer · force-push ve silme kapalı. Yönetici olarak siz doğrudan push edebilirsiniz; öğrenciler edemez.
- **Ayarlar:** Discussions ve Projects açık, Wiki kapalı, yalnız "squash" birleştirme, birleşen dal otomatik silinir.
- **Etiketler:** `oneri`, `hata`, `iyi-ilk-is`, `ai-modulu`, `kapsam-disi`, `entegre-edildi`.
- **CI (`denetim`):** yalnız Linux, ~1–2 dk; ruff + modül sözleşmesi denetleyicisi + testler. Depoda hiçbir gizli anahtar (secret) yok.

## Öğrenci eklemek
- GitHub web: depo → Settings → Collaborators → **Add people** → kullanıcı adı. Öğrenci yalnız bu depoyu görür; ana uygulama deposuna erişimi olmaz.
- Komutla: `gh api -X PUT repos/mert61-python/pemf-katki/collaborators/<kullanici_adi> -f permission=push`
- Ayrılan öğrenci: Settings → Collaborators → **Remove**.

## İsteğe bağlı: organizasyon
Öğrenci sayısı artarsa ücretsiz bir GitHub organizasyonu açılıp depo oraya taşınabilir (Settings → Transfer); takımlarla toplu yetki verilir.
Organizasyon API ile açılamaz, GitHub web'den açılır.

## Ana uygulamaya alma
Kabul edilen modül ana depoya `docs/entegrasyon.md`'deki yöntemle alınır: koordinatör bir entegrasyon oturumu açar (yama, kopya değil),
ardından bağımsız inceleme. Hoca paketinin entegrasyonu (AI-1 / AI-2) bunun ilk örneği.
