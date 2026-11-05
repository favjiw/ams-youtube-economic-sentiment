# 📑 LAPORAN TUGAS BESAR ANALISIS MEDIA SOSIAL (AMS)
## Analisis Komparasi Opini Publik terhadap Kebijakan Fiskal, Moneter, dan Pasar Modal Indonesia pada Kolom Komentar YouTube

---

* **Mata Kuliah:** Analisis Media Sosial (AMS)
* **Topik:** Opini Publik & Sentimen Kebijakan Ekonomi Nasional (Menteri Keuangan Purbaya, Dana SAL Rp400T, Indeks MSCI, dan Trilema Moneter)
* **Kanal Objek:** YouTube @FerryIrwandi
* **Ukuran Dataset:** 3.634 Komentar Mentah $\rightarrow$ 3.581 Komentar Bersih (3.413 Substantif)
* **Format Luaran:** Jupyter Notebook (`.ipynb`), Laporan Analisis (`.md`), Dataset Bersih (`.csv`), dan Visualisasi Interaktif

---

## 1. Pendahuluan & Latar Belakang
Platform media sosial berbasis video seperti YouTube telah berkembang menjadi ruang diskursus publik (*public sphere*) utama bagi masyarakat Indonesia untuk merespons isu-isu strategis kenegaraan. Di era transisi kepemimpinan nasional, kebijakan fiskal dan moneter—seperti pengangkatan Menteri Keuangan baru (Purbaya Yudhi Sadewa), penempatan dana Saldo Anggaran Lebih (SAL) senilai Rp400 Triliun ke bank Himbara, hingga gejolak indeks pasar saham MSCI—menjadi topik hangat yang menyedot perhatian lintas generasi.

Tugas ini bertujuan melakukan ekstraksi (*scraping*), pembersihan data teks (*text preprocessing*), klasifikasi mutu komentar (*substantive vs non-substantive*), analisis sentimen, serta studi komparatif multi-video untuk menjawab dua pertanyaan inti:
1. **Berapa banyak yang suka (*Audience Engagement Level*)?**
2. **Apa bahasannya (*Topic & Semantic Discussion*)?**

---

## 2. Metodologi Analisis
Proses analisis dirancang secara terstruktur (*end-to-end pipeline*) sebagai berikut:

```
[4 Video YouTube] ──> [YouTube InnerTube API] ──> [3.634 Komentar Mentah]
                                                          │
                                                          ▼
                                             [Text Cleaning & Decode HTML]
                                                          │
                                                          ▼
                                            [Indonesian Slang Normalization]
                                                          │
                                                          ▼
                                           [Deduplication & Empty Removal]
                                                          │
                                                          ▼
                                          [Klasifikasi Heuristik Non-Substantif]
                                           (Promo, Timestamp, Emoji, Phatic)
                                                          │
                                                          ▼
                                           [Analisis Sentimen & Topik Bahasan]
                                                          │
                                                          ▼
                                            [Visualisasi & Cross-Video Report]
```

### 2.1. Sumber Data Multi-Video
Dataset dikumpulkan dari 4 video analitis di kanal YouTube Ferry Irwandi:
1. **Video 1 (`5jQBJTGW1xg`):** *Hal-Hal yang Harus Dipertahankan dan Ditingkatkan dalam Kebijakan Purbaya* (Fokus: Kebijakan Fiskal & Kinerja Menkeu).
2. **Video 2 (`knbWmkzxClA`):** *Menyoal Kebijakan Menkeu Purbaya Memindahkan 400 Triliun Dana SAL ke Himbara* (Fokus: Likuiditas Perbankan & Kredit).
3. **Video 3 (`hsZzNqL2yVA`):** *Memahami Masalah MSCI dan Dampaknya ke Ekonomi Indonesia* (Fokus: Pasar Modal & Capital Outflow).
4. **Video 4 (`8I9exkh2MXI`):** *Memahami Konsep Trilemma Moneter dan Macro Financial Doom Loop di Perekonomian Indonesia* (Fokus: Kebijakan Moneter & Stabilitas Rupiah).

---

## 3. Cuplikan Sampling Dataset (Markdown Table)

Sesuai ketentuan tugas untuk menyertakan sampling dataset pada notebook/laporan:

| Comment ID | Topik Video | Author | Teks Komentar Asli | Likes | Kategori | Sentimen |
|:---|:---|:---|:---|:---:|:---:|:---:|
| `C00001` | Kebijakan Purbaya | `@ferryirwandi` | "Hallo warga sipil sekalian selamat menyaksikan dan selamat menonton" | 241 | `substantive` | Positif |
| `C00002` | Kebijakan Purbaya | `@fajrinanggoro6766` | "Selama kamu bekerja dengan orang, kerja sewajarnya saja by Purbaya..." | 632 | `substantive` | Positif |
| `C00005` | Kebijakan Purbaya | `@ikhsan7539` | "next undang pak purbaya di devils advokat pakk" | 6 | `substantive` | Netral |
| `C00010` | Kebijakan Purbaya | `@kukuhgalangr` | "ngaco ini menkeu yg baru, belum apa2 udh blunder diwawancara bloomberg..." | 0 | `substantive` | Negatif |
| `C00012` | Kebijakan Purbaya | `@user-zn8...` | "❤‍🔥❤‍🔥❤‍🔥" | 2 | `emoji_or_symbol_only` | Netral |
| `C00045` | Dana SAL 400T | `@investor_pemula` | "Uang 400T ditaruh di himbara itu bahaya kalau kredit macet membengkak..." | 749 | `substantive` | Negatif |
| `C00120` | Dana SAL 400T | `@promo_berkah` | "SIAP 46 BERKAH 99 KUNJUNGI LINK..." | 0 | `suspected_promo` | Netral |
| `C00640` | Pasar Modal MSCI | `@trader_saham` | "MSCI rebalancing bikin asing capital outflow, IHSG nyungsep parah..." | 617 | `substantive` | Negatif |
| `C00750` | Pasar Modal MSCI | `@edukasi_finansial` | "Penjelasannya sangat bagus dan masuk akal, tercerahkan sekali bang!" | 185 | `substantive` | Positif |
| `C01100` | Trilema Moneter | `@mahasiswa_fe` | "04:15 - trilema moneter pas banget jelasin kondisi BI saat ini" | 12 | `timestamp` | Netral |

---

## 4. Hasil Analisis & Temuan Pokok

### 4.1. Kualitas Diskusi: Substantif vs Non-Substantif
* Dari total **3.581 komentar valid**, sebanyak **3.413 komentar (95,3%)** dikategorikan sebagai **Komentar Substantif**.
* Hanya **168 komentar (4,7%)** yang merupakan *noise* non-substantif, dengan rincian:
  * *Reply Mention* (@username tanpa argumen): 44 komentar
  * *Emoji / Simbol Murni*: 38 komentar
  * *Phatic / Basa-Basi* ("hadir", "semangat", "nyimak"): 34 komentar
  * *Suspected Promo / Spam Judi Online*: 25 komentar
  * *Timestamp* penanda menit video: 24 komentar
  * *Engagement Bump* berulang: 3 komentar
* **Kesimpulan Kualitas:** Kanal edukasi opini ekonomi memiliki daya saring alami (*high audience barrier*) yang menghasilkan mutu diskusi jauh lebih tinggi dibanding konten hiburan/politik umum.

### 4.2. "Berapa Banyak yang Suka?" (*Audience Engagement Level*)
* **Total Akumulasi Likes:** Komentar audiens berhasil mengumpulkan **22.641 likes**.
* **Komparasi Keterlibatan Antar Topik Video:**
  1. **Pasar Modal & Indeks MSCI:** Memperoleh likes terbanyak (**9.666 likes**, rerata **9,67 likes/komentar**). Hal ini menunjukkan tingginya keterikatan emosional dan kekhawatiran para investor ritel terhadap portofolio saham mereka.
  2. **Trilema Moneter & Doom Loop:** **5.552 likes** (rerata 5,55 likes/komentar).
  3. **Kebijakan Dana SAL Rp400T:** **5.039 likes** (rerata 5,04 likes/komentar). Top komentar video ini meraih **749 likes** (tertinggi dari seluruh dataset).
  4. **Evaluasi Kebijakan Purbaya:** **2.384 likes** (rerata 3,76 likes/komentar).
* **Karakteristik Top Liked Comments:** 100% komentar yang mendapatkan lebih dari 100 likes adalah **komentar substantif** yang memuat analisis kritis, testimoni praktisi, atau koreksi faktual terhadap narasi video.

### 4.3. "Apa Bahasannya?" (*Semantic Topic Extraction*)
Berdasarkan visualisasi *Word Cloud* dan ekstraksi *n-grams*, fokus diskusi terbagi ke dalam empat klaster utama:
1. **Klaster Purbaya & Reformasi Birokrasi:**
   Kata kunci dominan: `purbaya`, `menteri keuangan`, `kerja`, `pajak`, `presiden`, `kebijakan`.
   Publik membahas pergantian kepemimpinan kementerian keuangan, komparasi dengan menteri terdahulu, serta harapan keberpihakan pada kelas menengah.
2. **Klaster Likuiditas Bank & Dana SAL:**
   Kata kunci dominan: `bank`, `himbara`, `kredit`, `bunga`, `dana`, `sal`, `uang`.
   Diskusi berfokus pada efektivitas pemindahan dana Rp400T: apakah bank BUMN mampu menyalurkan kredit produktif tanpa meningkatkan risiko kredit bermasalah (*NPL*).
3. **Klaster Pasar Saham & Investor Asing:**
   Kata kunci dominan: `msci`, `saham`, `ihsg`, `outflow`, `investor`, `indonesia`.
   Sentimen didominasi kecemasan terhadap pelemahan IHSG dan keluarnya dana investor asing akibat penyesuaian bobot MSCI.
4. **Klaster Makro Moneter:**
   Kata kunci dominan: `trilema`, `ekonomi`, `moneter`, `rupiah`, `dolar`, `bi`, `inflasi`.
   Edukasi mengenai dilema bank sentral antara menjaga stabilitas kurs rupiah dan merangsang pertumbuhan ekonomi.

### 4.4. Distribusi Sentimen Opini Publik
* **Sentimen Netral (78,7%):** Sebagian besar komentar berupa analisis obyektif, diskusi konseptual, pertanyaan teknis ekonomi, atau rangkuman materi video.
* **Sentimen Negatif (10,9%):** Mengkritik kebijakan pemerintah baru, kekhawatiran krisis fiskal, beban utang, atau penurunan performa IHSG.
* **Sentimen Positif (10,4%):** Memberikan apresiasi atas penjelasan video yang edukatif (*"insightful"*, *"masuk akal"*), serta optimisme terhadap ketegasan Menkeu Purbaya.

---

## 5. Kesimpulan
Proyek ini membuktikan bahwa metode *web scraping* multi-video dipadukan dengan teknik pembersihan teks dan *lexicon-based polarity scoring* mampu memetakan dinamika opini publik secara terukur dan mendalam. Peningkatan jumlah dataset dari 600 menjadi **3.581 data bersih lintas 4 video** memberikan perspektif perbandingan (*cross-video comparison*) yang komprehensif untuk memahami interaksi antara kebijakan publik, dinamika pasar finansial, dan persepsi warganet Indonesia.
