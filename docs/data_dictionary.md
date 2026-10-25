# Data Dictionary: Skema Awal Media Sosial

## 1. Database sumber (OLTP, schema `public`)

### comments
Komentar pada post

| Kolom | Tipe | Nullable | Key | Keterangan |
|---|---|---|---|---|
| comment_id | integer | NO | PK | ID unik komentar |
| post_id | integer | NO | FK -> posts.post_id | Post yang dikomentari |
| user_id | integer | NO | FK -> users.user_id | Penulis komentar |
| content | text | NO | - | Isi komentar |
| created_at | timestamp without time zone | NO | - | Waktu komentar dibuat |

### follows
Relasi mengikuti antar pengguna

| Kolom | Tipe | Nullable | Key | Keterangan |
|---|---|---|---|---|
| follow_id | integer | NO | PK | ID unik relasi |
| follower_id | integer | NO | FK -> users.user_id | Pengguna yang mengikuti |
| followed_id | integer | NO | FK -> users.user_id | Pengguna yang diikuti |
| created_at | timestamp without time zone | NO | - | Waktu mulai mengikuti |

### hashtags
Master hashtag

| Kolom | Tipe | Nullable | Key | Keterangan |
|---|---|---|---|---|
| hashtag_id | integer | NO | PK | ID unik hashtag |
| tag | character varying(60) | NO | - | Teks hashtag (unik) |

### likes
Like pengguna pada post (satu pengguna satu like per post)

| Kolom | Tipe | Nullable | Key | Keterangan |
|---|---|---|---|---|
| like_id | integer | NO | PK | ID unik like |
| post_id | integer | NO | FK -> posts.post_id | Post yang di-like |
| user_id | integer | NO | FK -> users.user_id | Pengguna yang me-like |
| created_at | timestamp without time zone | NO | - | Waktu like |

### post_hashtags
Tabel penghubung post dan hashtag (many-to-many)

| Kolom | Tipe | Nullable | Key | Keterangan |
|---|---|---|---|---|
| post_id | integer | NO | PK, FK -> posts.post_id | ID post |
| hashtag_id | integer | NO | PK, FK -> hashtags.hashtag_id | ID hashtag |

### posts
Unggahan yang dibuat pengguna

| Kolom | Tipe | Nullable | Key | Keterangan |
|---|---|---|---|---|
| post_id | integer | NO | PK | ID unik post |
| user_id | integer | NO | FK -> users.user_id | Pembuat post |
| content | text | NO | - | Isi teks post |
| media_type | character varying(10) | NO | - | Jenis media: text / image / video |
| created_at | timestamp without time zone | NO | - | Waktu post dibuat |

### users
Akun pengguna platform

| Kolom | Tipe | Nullable | Key | Keterangan |
|---|---|---|---|---|
| user_id | integer | NO | PK | ID unik pengguna |
| username | character varying(50) | NO | - | Nama pengguna (unik) |
| email | character varying(120) | NO | - | Alamat email (unik) |
| full_name | character varying(100) | NO | - | Nama lengkap |
| bio | text | YES | - | Deskripsi singkat profil |
| country | character varying(2) | YES | - | Kode negara (ISO 2 huruf) |
| is_verified | boolean | YES | - | Status akun terverifikasi |
| created_at | timestamp without time zone | NO | - | Waktu akun dibuat |

## 2. Staging (schema `staging`)

Struktur tiap tabel **sama dengan OLTP** (kolom asli tidak diubah), tanpa PK/FK, ditambah tiga kolom penanda landing:

| Kolom | Tipe | Keterangan |
|---|---|---|
| source_table | varchar(50) | Nama tabel asal data |
| batch_id | varchar(20) | ID batch ingestion (UTC, format YYYYMMDDTHHMMSS) |
| ingested_at | timestamp | Waktu data masuk ke staging (UTC) |

## 3. Data lake (MinIO)

- Bucket: `raw`
- Lokasi data: `<tabel>/dt=<YYYYMMDD>/batch_id=<batch_id>/part-NNNN.parquet`
- Manifest per batch: `_manifests/<batch_id>.json` (daftar tabel, jumlah baris, lokasi file)
- Isi file identik dengan tabel OLTP (tanpa kolom penanda)
