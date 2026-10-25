from collections import defaultdict
from pathlib import Path

from sqlalchemy import text

from ingestion.config import get_oltp_engine, get_staging_engine

DESC = {
    "users": {
        "_": "Akun pengguna platform",
        "user_id": "ID unik pengguna", "username": "Nama pengguna (unik)",
        "email": "Alamat email (unik)", "full_name": "Nama lengkap",
        "bio": "Deskripsi singkat profil", "country": "Kode negara (ISO 2 huruf)",
        "is_verified": "Status akun terverifikasi", "created_at": "Waktu akun dibuat",
    },
    "posts": {
        "_": "Unggahan yang dibuat pengguna",
        "post_id": "ID unik post", "user_id": "Pembuat post",
        "content": "Isi teks post", "media_type": "Jenis media: text / image / video",
        "created_at": "Waktu post dibuat",
    },
    "comments": {
        "_": "Komentar pada post",
        "comment_id": "ID unik komentar", "post_id": "Post yang dikomentari",
        "user_id": "Penulis komentar", "content": "Isi komentar",
        "created_at": "Waktu komentar dibuat",
    },
    "likes": {
        "_": "Like pengguna pada post (satu pengguna satu like per post)",
        "like_id": "ID unik like", "post_id": "Post yang di-like",
        "user_id": "Pengguna yang me-like", "created_at": "Waktu like",
    },
    "follows": {
        "_": "Relasi mengikuti antar pengguna",
        "follow_id": "ID unik relasi", "follower_id": "Pengguna yang mengikuti",
        "followed_id": "Pengguna yang diikuti", "created_at": "Waktu mulai mengikuti",
    },
    "hashtags": {
        "_": "Master hashtag",
        "hashtag_id": "ID unik hashtag", "tag": "Teks hashtag (unik)",
    },
    "post_hashtags": {
        "_": "Tabel penghubung post dan hashtag (many-to-many)",
        "post_id": "ID post", "hashtag_id": "ID hashtag",
    },
}

COLS = text("""
    SELECT table_name, column_name, data_type, character_maximum_length, is_nullable
    FROM information_schema.columns WHERE table_schema = :s
    ORDER BY table_name, ordinal_position
""")

KEYS = text("""
    SELECT tc.table_name, kcu.column_name, tc.constraint_type,
           ccu.table_name AS ref_table, ccu.column_name AS ref_col
    FROM information_schema.table_constraints tc
    JOIN information_schema.key_column_usage kcu
      ON tc.constraint_name = kcu.constraint_name AND tc.table_schema = kcu.table_schema
    LEFT JOIN information_schema.constraint_column_usage ccu
      ON tc.constraint_name = ccu.constraint_name AND tc.constraint_type = 'FOREIGN KEY'
    WHERE tc.table_schema = 'public' AND tc.constraint_type IN ('PRIMARY KEY', 'FOREIGN KEY')
""")


def fmt_type(dtype, length):
    return f"{dtype}({length})" if length else dtype


def main():
    out = ["# Data Dictionary: Skema Awal Media Sosial", ""]

    with get_oltp_engine().connect() as c:
        cols = defaultdict(list)
        for t, col, dt, ln, nul in c.execute(COLS, {"s": "public"}):
            cols[t].append((col, fmt_type(dt, ln), nul))
        keys = defaultdict(list)
        for t, col, kind, rt, rc in c.execute(KEYS):
            keys[(t, col)].append(f"FK -> {rt}.{rc}" if kind == "FOREIGN KEY" else "PK")

    out += ["## 1. Database sumber (OLTP, schema `public`)", ""]
    for t in sorted(cols):
        d = DESC.get(t, {})
        out += [f"### {t}", f"{d.get('_', '')}", "",
                "| Kolom | Tipe | Nullable | Key | Keterangan |", "|---|---|---|---|---|"]
        for col, typ, nul in cols[t]:
            key = ", ".join(dict.fromkeys(keys.get((t, col), []))) or "-"
            out.append(f"| {col} | {typ} | {nul} | {key} | {d.get(col, '')} |")
        out.append("")

    out += [
        "## 2. Staging (schema `staging`)", "",
        "Struktur tiap tabel **sama dengan OLTP** (kolom asli tidak diubah), tanpa PK/FK, "
        "ditambah tiga kolom penanda landing:", "",
        "| Kolom | Tipe | Keterangan |", "|---|---|---|",
        "| source_table | varchar(50) | Nama tabel asal data |",
        "| batch_id | varchar(20) | ID batch ingestion (UTC, format YYYYMMDDTHHMMSS) |",
        "| ingested_at | timestamp | Waktu data masuk ke staging (UTC) |", "",
        "## 3. Data lake (MinIO)", "",
        "- Bucket: `raw`",
        "- Lokasi data: `<tabel>/dt=<YYYYMMDD>/batch_id=<batch_id>/part-NNNN.parquet`",
        "- Manifest per batch: `_manifests/<batch_id>.json` (daftar tabel, jumlah baris, lokasi file)",
        "- Isi file identik dengan tabel OLTP (tanpa kolom penanda)", "",
    ]

    # Verifikasi struktur staging sesuai (kolom asli + 3 penanda)
    with get_staging_engine().connect() as c:
        stg = defaultdict(list)
        for t, col, *_ in c.execute(COLS, {"s": "staging"}):
            stg[t].append(col)
    for t in sorted(cols):
        expected = [x[0] for x in cols[t]] + ["source_table", "batch_id", "ingested_at"]
        assert stg[t] == expected, f"Struktur staging.{t} tidak sesuai OLTP + kolom penanda"

    Path("docs").mkdir(exist_ok=True)
    Path("docs/data_dictionary.md").write_text("\n".join(out), encoding="utf-8")
    print("Tersimpan: docs/data_dictionary.md (struktur staging terverifikasi)")


if __name__ == "__main__":
    main()