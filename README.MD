# Kelompok 7: Social Media Data Pipeline

## Cara menjalankan
1. git clone <URL_REPO>
2. cp .env.example .env        (Windows PowerShell: Copy-Item .env.example .env)
3. docker compose up -d
4. python -m venv .venv
5. .venv\Scripts\activate      (Mac/Linux: source .venv/bin/activate)
6. pip install -r requirements.txt
7. python check_env.py

## Koneksi
| Komponen | Host | Port | Database |
|---|---|---|---|
| PostgreSQL OLTP | localhost | 5433 | socmed_oltp |
| PostgreSQL Staging | localhost | 5434 | socmed_staging |
| MinIO API | localhost | 9000 | bucket: raw |

## Aturan
- Jangan commit file .env
- B: sql/oltp/ dan generator/
- C: sql/staging/ dan ingestion/
- D: docs/
