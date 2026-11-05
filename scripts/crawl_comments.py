"""Script Crawling Komentar YouTube untuk Tugas Analisis Media Sosial (AMS)
Mengambil data komentar dari multi-video YouTube topik Kebijakan Ekonomi Nasional.
"""

import csv
import time
from datetime import datetime, timezone
from youtube_comment_downloader import YoutubeCommentDownloader

def crawl_youtube_comments(videos, output_file, max_per_video=1000):
    downloader = YoutubeCommentDownloader()
    fieldnames = [
        'comment_id', 'cid', 'video_id', 'video_title', 'video_category',
        'published_at', 'author', 'text_raw', 'like_count', 'reply_count',
        'is_reply', 'has_heart'
    ]

    total = 0
    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        cid_counter = 1
        
        for v in videos:
            print(f"[CRAWL] Memulai pengambilan komentar: {v['video_id']} - {v['video_title']}...")
            count = 0
            t0 = time.time()
            for c in downloader.get_comments_from_url(f"https://www.youtube.com/watch?v={v['video_id']}", sort_by=0):
                ts = c.get('time_parsed')
                dt_str = datetime.fromtimestamp(ts, tz=timezone.utc).strftime('%Y-%m-%d %H:%M:%S') if ts else ''
                
                raw_votes = c.get('votes', 0)
                try:
                    like_count = int(raw_votes) if raw_votes else 0
                except ValueError:
                    like_count = 0
                    
                raw_replies = c.get('replies', 0)
                try:
                    reply_count = int(raw_replies) if raw_replies else 0
                except ValueError:
                    reply_count = 0

                writer.writerow({
                    'comment_id': f"C{cid_counter:05d}",
                    'cid': c.get('cid', ''),
                    'video_id': v['video_id'],
                    'video_title': v['video_title'],
                    'video_category': v['category'],
                    'published_at': dt_str,
                    'author': c.get('author', ''),
                    'text_raw': c.get('text', ''),
                    'like_count': like_count,
                    'reply_count': reply_count,
                    'is_reply': c.get('reply', False),
                    'has_heart': c.get('heart', False)
                })
                cid_counter += 1
                count += 1
                if count >= max_per_video:
                    break
            dur = time.time() - t0
            print(f"  [OK] Berhasil mengunduh {count} komentar dalam {dur:.1f}s")
            total += count

    print(f"[SELESAI] Total seluruh komentar tersimpan: {total} baris ke {output_file}")
    return total

if __name__ == '__main__':
    video_list = [
        {
            'video_id': '5jQBJTGW1xg',
            'video_title': 'Hal-Hal yang Harus Dipertahankan dan Ditingkatkan dalam Kebijakan Purbaya',
            'category': 'Kebijakan Fiskal Purbaya'
        },
        {
            'video_id': 'knbWmkzxClA',
            'video_title': 'Menyoal Kebijakan Menkeu Purbaya Memindahkan 400 Triliun Dana SAL ke Himbara',
            'category': 'Kebijakan Dana SAL 400T'
        },
        {
            'video_id': 'hsZzNqL2yVA',
            'video_title': 'Memahami Masalah MSCI dan Dampaknya ke Ekonomi Indonesia',
            'category': 'Pasar Modal & Indeks MSCI'
        },
        {
            'video_id': '8I9exkh2MXI',
            'video_title': 'Memahami Konsep Trilemma Moneter dan Macro Financial Doom Loop di Perekonomian Indonesia',
            'category': 'Kebijakan Moneter & Doom Loop'
        }
    ]
    crawl_youtube_comments(video_list, 'data/raw_youtube_comments.csv', max_per_video=1000)
