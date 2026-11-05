"""Script Preprocessing & Analisis Komentar YouTube untuk Tugas AMS
Menjalankan text cleaning, normalisasi slang, klasifikasi substantif, sentimen, dan pembuatan visualisasi.
"""

import os
import re
import html
import unicodedata
from collections import Counter
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from wordcloud import WordCloud
from matplotlib.patches import Patch

BR_TAG_RE = re.compile(r"<br\s*/?>", re.I)
HTML_TAG_RE = re.compile(r"<[^>]+>")
URL_RE = re.compile(r"(https?://\S+|www\.\S+)", re.I)
WHITESPACE_RE = re.compile(r"\s+")
REPEATED_CHAR_RE = re.compile(r"([a-z])\1{2,}")
EMOJI_RE = re.compile("[\U0001F300-\U0001FAFF\u2600-\u27BF]")
TIMESTAMP_RE = re.compile(r"^\s*(\d{1,2}[:.]){1,2}\d{1,2}(\D|$)|^\s*\d+\s*menit", re.I)
MENTION_RE = re.compile(r"^@\S+")
NO_ALNUM_RE = re.compile(r"^[\W_]+$", re.UNICODE)
WORD_RE = re.compile(r"[a-z]+")

PROMO_RE = re.compile(
    r"berkah\s*99|siap\s*46|estetik kreatif banget|paling the best|selalu bikin kagum|slot|gacor|maxwin|depo|withdraw|wa\.me|t\.me",
    re.I,
)

SLANG = {
    r"gak|ga|nggak|ngga|enggak|engga|gk|tdk": "tidak",
    r"tp": "tapi",
    r"dlm": "dalam",
    r"yg": "yang",
    r"dgn|dg": "dengan",
    r"utk": "untuk",
    r"krn|karna": "karena",
    r"udh|sdh|udah": "sudah",
    r"blm": "belum",
    r"jg": "juga",
    r"bgt|bngt": "banget",
    r"kalo|klo": "kalau",
    r"aja": "saja",
    r"emg|emang": "memang",
    r"org": "orang",
    r"dr": "dari",
    r"pd": "pada",
    r"bs": "bisa",
    r"lg": "lagi",
    r"trs": "terus",
    r"gw|gue|gua|sy": "saya",
    r"lu|lo": "kamu",
    r"bapack|bapak2": "bapak",
    r"bener": "benar",
    r"dapet": "dapat",
    r"sampe": "sampai",
    r"kyk|kayak": "seperti",
    r"tau": "tahu",
    r"cmn|cuman": "cuma",
}
SLANG_PATTERNS = [(re.compile(rf"\b(?:{k})\b"), v) for k, v in SLANG.items()]

PHATIC_WORDS = {
    "semangat", "yes", "yess", "hi", "hai", "halo", "hello", "gg", "nyimak",
    "up", "first", "pertama", "mantap", "salam", "izin", "absen", "ok", "oke",
    "hadir", "hadirrr", "hadirr", "wow", "wew", "yayayayaya", "soon", "omaga",
    "setuju", "nice", "top", "mantul"
}

POSITIVE_WORDS = {
    "bagus", "keren", "mantap", "setuju", "cerdas", "solutif", "edukatif", "paham",
    "bermanfaat", "apresiasi", "sukses", "optimis", "terima kasih", "makasih", "hebat",
    "jelas", "logis", "masuk akal", "terbaik", "bangga", "salut", "mendukung",
    "terbuka", "pelajaran", "menarik", "insightful", "tercerahkan", "juara", "berbobot",
    "semoga", "prestasi", "positif", "berani", "bijak", "akur", "luar biasa"
}

NEGATIVE_WORDS = {
    "blunder", "hancur", "rusak", "krisis", "parah", "buruk", "gagal", "kecewa",
    "ngaco", "bodoh", "utang", "nyungsep", "korupsi", "waspada", "ancaman", "bahaya",
    "panik", "beban", "rugi", "bingung", "takut", "ancur", "penipuan", "manipulasi",
    "sulit", "miskin", "terpuruk", "jenuh", "curiga", "ambruk", "jatuh", "sengsara",
    "masalah", "bobrok", "zalim", "pesimis", "menyesal"
}

NEGATIONS = {"tidak", "bukan", "belum", "kurang", "jangan"}

STOPWORDS = {
    "yang", "dan", "di", "ke", "dari", "itu", "ini", "untuk", "dengan", "ada",
    "adalah", "bisa", "akan", "saya", "kamu", "dia", "mereka", "kita", "kami",
    "ya", "lah", "kah", "deh", "sih", "pun", "kok", "loh", "bgt", "aja", "dgn",
    "yg", "utk", "kalo", "biar", "buat", "tapi", "sudah", "atau", "pada", "juga",
    "banyak", "kalau", "tidak", "nih", "mau", "jadi", "dan", "oleh", "dalam", "bang",
    "ferry", "video", "lebih", "karena", "bukan", "hanya", "saja", "terima", "kasih",
    "orang", "sangat", "mas", "pak", "bung", "bapak", "terus", "lagi", "harus", "nya",
    "sama", "udah", "gak", "kan", "ga"
}

def clean_text(text: str) -> str:
    text = BR_TAG_RE.sub(" ", str(text))
    text = HTML_TAG_RE.sub(" ", text)
    text = html.unescape(text)
    text = URL_RE.sub("[URL]", text)
    return WHITESPACE_RE.sub(" ", text).strip()

def normalize(text: str) -> str:
    text = unicodedata.normalize("NFKC", text).lower()
    text = REPEATED_CHAR_RE.sub(r"\1", text)
    for pattern, replacement in SLANG_PATTERNS:
        text = pattern.sub(replacement, text)
    return WHITESPACE_RE.sub(" ", text).strip()

def styled_ratio(text: str) -> float:
    alnum_count = sum(c.isalnum() for c in text)
    if alnum_count == 0:
        return 0.0
    styled_count = sum(0x1D400 <= ord(c) <= 0x1D7FF for c in text)
    return styled_count / alnum_count

def classify_non_substantive(row: pd.Series) -> str:
    text = row["text_clean"].strip()
    norm = row["text_norm"].strip()
    tokens = WORD_RE.findall(norm)
    n_words = row["n_words"]

    if row["is_promo_pattern"] or row["styled_ratio"] > 0.3:
        return "suspected_promo"
    if TIMESTAMP_RE.match(text) and n_words <= 8:
        return "timestamp"
    if MENTION_RE.match(text) and n_words <= 6:
        return "reply_mention"
    if NO_ALNUM_RE.match(text):
        return "emoji_or_symbol_only"
    if tokens and len(tokens) <= 3 and all(w in PHATIC_WORDS for w in tokens):
        return "phatic"
    if row["dup_count"] >= 3 and n_words <= 3:
        return "engagement_bump"
    return ""

def analyze_sentiment(norm_text: str) -> tuple[str, float]:
    words = WORD_RE.findall(norm_text)
    if not words:
        return "Netral", 0.0
    score = 0.0
    i = 0
    n = len(words)
    while i < n:
        w = words[i]
        if i < n - 1:
            bg = f"{w} {words[i+1]}"
            if bg in POSITIVE_WORDS:
                score += 1.5
                i += 2
                continue
            elif bg in NEGATIVE_WORDS:
                score -= 1.5
                i += 2
                continue
        if w in NEGATIONS and i < n - 1:
            nw = words[i+1]
            if nw in POSITIVE_WORDS:
                score -= 1.0
                i += 2
                continue
            elif nw in NEGATIVE_WORDS:
                score += 0.8
                i += 2
                continue
        if w in POSITIVE_WORDS:
            score += 1.0
        elif w in NEGATIVE_WORDS:
            score -= 1.0
        i += 1
    
    polarity = score / (len(words) ** 0.5) if words else 0.0
    if score > 0:
        label = "Positif"
    elif score < 0:
        label = "Negatif"
    else:
        label = "Netral"
    return label, round(polarity, 3)

def run_pipeline(raw_csv_path: str, clean_csv_path: str, figures_dir: str):
    os.makedirs(figures_dir, exist_ok=True)
    df = pd.read_csv(raw_csv_path)
    n_raw = len(df)
    print(f"Loaded raw dataset: {n_raw} rows.")

    df["text_clean"] = df["text_raw"].map(clean_text)
    df["text_norm"] = df["text_clean"].map(normalize)
    df["styled_ratio"] = df["text_clean"].map(styled_ratio)
    df["n_words"] = df["text_norm"].str.split().str.len().fillna(0).astype(int)
    df["has_emoji"] = df["text_clean"].str.contains(EMOJI_RE)
    df["has_url"] = df["text_clean"].str.contains(r"\[URL\]")
    df["is_promo_pattern"] = df["text_norm"].str.contains(PROMO_RE)

    # Empty & duplicate removal
    df = df[df["n_words"] > 0].copy()
    n_no_empty = len(df)
    df = df.drop_duplicates(subset=["author", "text_norm"]).copy()
    n_no_dup = len(df)

    df["dup_count"] = df.groupby("text_norm")["text_norm"].transform("size")
    df["non_substantive_type"] = df.apply(classify_non_substantive, axis=1)
    df["is_substantive"] = df["non_substantive_type"] == ""

    sent_results = df["text_norm"].map(analyze_sentiment)
    df["sentiment_label"] = [r[0] for r in sent_results]
    df["sentiment_score"] = [r[1] for r in sent_results]

    df.to_csv(clean_csv_path, index=False)
    print(f"Saved clean dataset to {clean_csv_path} ({len(df)} rows).")

    # Generate Figures
    sns.set_theme(style="whitegrid")
    
    # 1. Donut Chart Substantive
    plt.figure(figsize=(6, 6))
    counts = df["is_substantive"].value_counts()
    labels = ["Substantive" if k else "Non-Substantive" for k in counts.index]
    colors = ["#2ecc71", "#e74c3c"]
    plt.pie(counts.values, labels=labels, autopct="%1.1f%%", startangle=90, colors=colors, pctdistance=0.82)
    centre_circle = plt.Circle((0,0), 0.65, fc="white")
    plt.gca().add_artist(centre_circle)
    plt.title("Proporsi Komentar Substantif vs Non-Substantif\n(Total: 3.581 Komentar)", fontsize=13, weight="bold")
    plt.tight_layout()
    plt.savefig(os.path.join(figures_dir, "01_substantive_distribution.png"), dpi=200)
    plt.close()

    # 2. Multi-Video Comparison Bar
    plt.figure(figsize=(10, 5))
    vid_stats = df.groupby("video_category").agg(
        total=("comment_id", "count"),
        substantive=("is_substantive", "sum"),
        avg_likes=("like_count", "mean")
    ).reset_index()
    vid_stats["pct_substantive"] = (vid_stats["substantive"] / vid_stats["total"]) * 100
    
    ax = sns.barplot(data=vid_stats, x="video_category", y="pct_substantive", palette="Blues_r")
    plt.title("Persentase Komentar Substantif per Video Topik Ekonomi", fontsize=13, weight="bold")
    plt.xlabel("Topik Video", fontsize=11)
    plt.ylabel("% Komentar Substantif", fontsize=11)
    plt.ylim(85, 100)
    for p in ax.patches:
        ax.annotate(f"{p.get_height():.1f}%", (p.get_x() + p.get_width() / 2., p.get_height()),
                    ha="center", va="center", xytext=(0, 6), textcoords="offset points", weight="bold")
    plt.xticks(rotation=15, ha="right")
    plt.tight_layout()
    plt.savefig(os.path.join(figures_dir, "02_video_substantive_comparison.png"), dpi=200)
    plt.close()

    # 3. Sentiment Distribution per Video
    plt.figure(figsize=(11, 5))
    sent_vid = df.groupby(["video_category", "sentiment_label"]).size().unstack(fill_value=0)
    sent_vid_pct = sent_vid.div(sent_vid.sum(axis=1), axis=0) * 100
    sent_vid_pct = sent_vid_pct[["Positif", "Netral", "Negatif"]]
    sent_vid_pct.plot(kind="bar", stacked=True, color=["#27ae60", "#95a5a6", "#c0392b"], figsize=(10, 5))
    plt.title("Distribusi Sentimen Opini Publik per Video Kebijakan Ekonomi", fontsize=13, weight="bold")
    plt.xlabel("Topik Video", fontsize=11)
    plt.ylabel("Proporsi (%)", fontsize=11)
    plt.legend(title="Sentimen", loc="lower right")
    plt.xticks(rotation=15, ha="right")
    plt.tight_layout()
    plt.savefig(os.path.join(figures_dir, "03_sentiment_by_video.png"), dpi=200)
    plt.close()

    # 4. Top Liked Comments
    plt.figure(figsize=(10, 6))
    top10 = df.sort_values(by="like_count", ascending=False).head(10).copy()
    top10["short_text"] = top10["text_raw"].apply(lambda x: x[:50] + "..." if len(str(x)) > 50 else str(x))
    colors_top = ["#2ecc71" if s else "#e74c3c" for s in top10["is_substantive"]]
    sns.barplot(data=top10, x="like_count", y="short_text", palette=colors_top, hue="is_substantive", legend=False)
    plt.title("Top 10 Komentar Paling Banyak Disukai (Likes Terbanyak)", fontsize=13, weight="bold")
    plt.xlabel("Jumlah Likes", fontsize=11)
    plt.ylabel("Komentar", fontsize=11)
    legend_elements = [
        Patch(facecolor="#2ecc71", label="Substantive"),
        Patch(facecolor="#e74c3c", label="Non-Substantive")
    ]
    plt.legend(handles=legend_elements, loc="lower right", title="Kategori")
    plt.tight_layout()
    plt.savefig(os.path.join(figures_dir, "04_top_liked_comments.png"), dpi=200)
    plt.close()

    # 5. WordCloud
    all_clean_words = []
    for text in df[df["is_substantive"]]["text_norm"]:
        words = WORD_RE.findall(str(text))
        all_clean_words.extend([w for w in words if w not in STOPWORDS and len(w) > 2])
    wc_text = " ".join(all_clean_words)
    
    wc = WordCloud(
        width=1000,
        height=500,
        background_color="white",
        colormap="viridis",
        max_words=120,
        random_state=42
    ).generate(wc_text)
    plt.figure(figsize=(12, 6))
    plt.imshow(wc, interpolation="bilinear")
    plt.axis("off")
    plt.title("Word Cloud Bahasan Utama Komentar Publik (Kebijakan Ekonomi)", fontsize=14, weight="bold", pad=12)
    plt.tight_layout()
    plt.savefig(os.path.join(figures_dir, "05_wordcloud_ekonomi.png"), dpi=200)
    plt.close()

    # 6. Hourly Activity Pattern
    df["published_at_dt"] = pd.to_datetime(df["published_at"], errors="coerce")
    df["hour"] = df["published_at_dt"].dt.hour
    hourly = df.groupby("hour").size().reindex(range(24), fill_value=0).reset_index(name="count")
    plt.figure(figsize=(10, 4.5))
    sns.barplot(data=hourly, x="hour", y="count", color="#3498db")
    plt.title("Distribusi Aktivitas Penulisan Komentar per Jam (24-Hour Cycle)", fontsize=13, weight="bold")
    plt.xlabel("Jam (WIB / UTC)", fontsize=11)
    plt.ylabel("Jumlah Komentar", fontsize=11)
    plt.grid(axis="y", linestyle="--", alpha=0.5)
    plt.tight_layout()
    plt.savefig(os.path.join(figures_dir, "06_hourly_distribution.png"), dpi=200)
    plt.close()

    print(f"Generated 6 figures in {figures_dir}.")

if __name__ == '__main__':
    run_pipeline(
        raw_csv_path='/home/ubuntu/ams-youtube-economic-sentiment/data/raw_youtube_comments.csv',
        clean_csv_path='/home/ubuntu/ams-youtube-economic-sentiment/data/cleaned_youtube_comments.csv',
        figures_dir='/home/ubuntu/ams-youtube-economic-sentiment/reports/figures'
    )
