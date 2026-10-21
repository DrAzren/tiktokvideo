# Prompt: video dokumentari Borak Jiwa + pakej YouTube + versi TikTok

Salin semua dalam kotak di bawah ke sesi Claude Code yang baru, pada repo `drazren/tiktokvideo`. Isi dahulu setiap
`[...]`. Baris yang tidak berkaitan boleh dipadam.

```
Hasilkan satu video YouTube baru untuk saluran BORAK JIWA dengan konsep yang sama seperti video
"Sejarah Wad Psikiatri di Malaysia", menggunakan suara saya sendiri. Kemudian sediakan pakej YouTube
yang lengkap (dengan gambar muka saya dalam thumbnail) dan versi TikTok 9:16.

== MAKLUMAT VIDEO ==
- Tajuk kerja: [contoh: Sejarah Ubat Psikiatri di Malaysia]
- Rakaman suara saya: Google Drive, fail bertajuk "[nama fail di Drive]"
  (atau: fail yang saya lampirkan)
- Topik ringkas / sudut cerita: [2–3 ayat tentang apa video ini mahu sampaikan]
- Perkara/fakta yang mesti betul: [contoh: tarikh, nama hospital, nama ubat]
- Tambahan pada skrin (jika ada): [contoh: kad buku saya, lower third klinik, peta, garis masa]

== RUJUKAN (baca dahulu) ==
- Branch rujukan: claude/confident-wozniak-tylptp (jika belum di-merge ke main, fetch dan guna fail daripadanya).
- Kit jenama: brand/brand.md. Ia mengandungi nama, pautan klinik & buku, palet, fon, gambar muka
  (brand/dr_azren_cutout.png), kulit buku (brand/book_cover.jpg) dan peraturan tetap saya.
- Contoh lengkap yang perlu diikut: videos/wad-psikiatri-sejarah/
  (project.md, edit/align.py, edit/realign.py, edit/build_voice.py, doc/build_wad.py, doc/style.css,
  doc/synth.py, doc/score_wad.py, youtube/thumb_a.html, youtube/thumb_b.html, youtube/youtube_package.md,
  tiktok/make_ass.py, tiktok/compose.sh, tiktok/cover.html, tiktok/tiktok_post.md).
- Ikut CLAUDE.md repo ini untuk setup (scripts/setup.sh) dan pipeline.

== BAJET & PERATURAN ==
- JANGAN guna kredit Higgsfield tanpa kebenaran saya. Jika perlu, beri anggaran kredit dahulu dan tunggu
  jawapan saya. Utamakan guna semula klip/imej episod lepas, grafik HyperFrames, peta Natural Earth, dan
  muzik/SFX yang dijana sendiri (doc/synth.py).
- Jika saya benarkan kredit: had maksimum [contoh: 0 / 40 / 75] kredit.
- Tiada unsur seram, tiada rakaman arkib palsu. Visual sejarah dilabel "Dramatisasi · visual dijana AI".
- Jangan letak talian bantuan.
- Jangan ubah fail dalam raw/.

== LANGKAH ==
1. Muat turun suara saya → videos/<projek>/raw/. Transkripsi dengan Whisper large-v3, kemudian forced-align
   dengan MMS_FA per pulau ucapan.
2. Bersihkan suara (PALING PENTING):
   - Buang SEMUA ayat/frasa yang berulang dan retake. Semak perkataan yang durasinya luar biasa panjang
     (>1 s); retake selalu tersembunyi di situ.
   - Buang filler: "ha", "emm", "eh", "lah", "je", "dah", "dah macam", "sebenarnya"/"ni" di hujung ayat,
     perkataan berganda.
   - Isi ruang dengan room tone sebenar, bukan senyap digital. Pendekkan jeda panjang.
   - "ni"/"tu" yang melekat pada perkataan seterusnya boleh dikekalkan jika memotongnya merosakkan bunyi.
   - Sahkan dengan Whisper large-v3 (biasa + prompt filler) pada suara yang sudah dipotong. Senaraikan
     kepada saya apa yang dibuang.
3. Strategi: cadangkan dalam 4–8 ayat (struktur bab, visual setiap bab, grafik, muzik/SFX, anggaran
   panjang). Sahkan fakta dengan carian web. TUNGGU kelulusan saya sebelum render.
4. Bina komposisi HyperFrames 1920×1080 @ 24 fps dengan gaya yang sama: dokumentari sinematik, Ken Burns,
   peralihan dakwat & kertas koyak, garis masa era, tipografi kinetik, lower third
   "DR. AZREN · Klinik Nissa", kad buku 3D (kulit sebenar), kad penutup BORAK JIWA, sari kata Bahasa Melayu
   dengan kata kunci teal/emas dalam zon selamat.
5. Audio: skor & SFX asli (synth.py), duck di bawah suara (~16 dB), master −14 LUFS, TP ≤ −1 dBTP.
6. QA: snapshot setiap shot, blackdetect, ukur kelantangan, semak bingkai sekitar setiap potongan suara.

== HASIL AKHIR ==
A) YouTube
   - final_1080.mp4 (1920×1080) + salinan < 500 MB untuk dihantar (CRF 18, had 10 Mbps)
   - final_share_720p.mp4 (semakan) + fail sari kata .srt
B) Pakej YouTube (folder youtube/)
   - 2 thumbnail 1280×720 (A/B untuk "Test & compare"), DENGAN GAMBAR MUKA SAYA
     (brand/dr_azren_cutout.png, tepi kiri/kanan di-feather, muka tidak ditutup teks),
     tajuk besar Plus Jakarta Sans 800 kuning #FFD21F bergaris hitam, mesti jelas pada saiz kecil
   - 3 cadangan tajuk (tandakan yang disyorkan)
   - Deskripsi siap salin: pembuka 2 ayat, ringkasan, BAB bercap masa (0:00 ...), pautan
     "Tempah Konsultasi Bersama Dr Azren" dan pautan buku (dari brand/brand.md), ajakan komen,
     nota pendidikan + nota visual AI, hashtag
   - Tag, komen untuk di-pin (dengan pautan), senarai tetapan muat naik (Altered content = Yes,
     Education, sari kata .srt, end screen)
C) TikTok
   - final_tiktok_9x16.mp4 (1080×1920): versi 16:9 tanpa sari kata sebagai jalur di tengah, latar kabur
     yang digelapkan, tajuk + label bab di atas, sari kata besar dengan perkataan aktif kuning (ikut
     tiktok/make_ass.py + compose.sh), dalam zon selamat TikTok
   - tiktok_cover.jpg 1080×1920 dengan gambar muka saya
   - Kapsyen TikTok + hashtag ("pautan di bio"), ingatkan label AI-generated content
   - Cadangkan 1 klip pendek 60–90 s jika sesuai (jangan buat tanpa tanya)

Hantar setiap fail kepada saya bila siap, commit & push skrip (bukan footage), dan tambah catatan
sesi dalam project.md.
```

## Versi ringkas (bila semua sudah biasa)

```
Buat video Borak Jiwa baru: "[tajuk]". Suara saya di Google Drive: "[nama fail]".
Ikut sepenuhnya cara videos/wad-psikiatri-sejarah (branch claude/confident-wozniak-tylptp) dan brand/brand.md:
bersihkan suara (buang semua ulangan & filler, sahkan dengan Whisper), cadangkan strategi dan tunggu OK saya,
render 16:9, kemudian sediakan pakej YouTube (2 thumbnail dengan muka saya, tajuk, deskripsi dengan bab + pautan,
tag, komen pin) dan versi TikTok 9:16 + cover + kapsyen. Jangan guna kredit Higgsfield tanpa tanya saya dahulu.
```
