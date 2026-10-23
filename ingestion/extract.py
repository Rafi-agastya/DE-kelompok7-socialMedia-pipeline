import io
import json
from datetime import datetime, timezone

import pandas as pd
from sqlalchemy import text

from ingestion.config import BUCKET, CHUNK_SIZE, get_oltp_engine, get_s3, get_logger

log = get_logger("extract")


def list_tables(engine, schema="public"):
    """Ambil daftar tabel otomatis dari database, jadi tidak perlu hardcode."""
    q = text("""
        SELECT table_name FROM information_schema.tables
        WHERE table_schema = :schema AND table_type = 'BASE TABLE'
        ORDER BY table_name
    """)
    with engine.connect() as conn:
        return [r[0] for r in conn.execute(q, {"schema": schema})]


def extract_table(engine, s3, table, batch_id, schema="public"):
    """Salin satu tabel ke MinIO sebagai Parquet. Data TIDAK diubah."""
    date_part = batch_id[:8]
    prefix = f"{table}/dt={date_part}/batch_id={batch_id}"
    total_rows, part = 0, 0

    query = f'SELECT * FROM "{schema}"."{table}"'
    with engine.connect().execution_options(stream_results=True) as conn:
        for chunk in pd.read_sql(text(query), conn, chunksize=CHUNK_SIZE):
            part += 1
            buf = io.BytesIO()
            chunk.to_parquet(buf, engine="pyarrow", index=False)
            buf.seek(0)
            key = f"{prefix}/part-{part:04d}.parquet"
            s3.put_object(Bucket=BUCKET, Key=key, Body=buf.getvalue())
            total_rows += len(chunk)
            log.info("  %s: part %d uploaded (%d baris)", table, part, len(chunk))

    log.info("[OK] %s -> %d baris, %d file", table, total_rows, part)
    return {"table": table, "rows": total_rows, "files": part, "prefix": prefix}


def run_extract(batch_id=None):
    batch_id = batch_id or datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S")
    engine, s3 = get_oltp_engine(), get_s3()

    tables = list_tables(engine)
    if not tables:
        raise RuntimeError("Tidak ada tabel di OLTP. Pastikan DDL dari B sudah jalan.")

    log.info("Batch %s: extract %d tabel: %s", batch_id, len(tables), tables)
    results = []
    for t in tables:
        try:
            results.append(extract_table(engine, s3, t, batch_id))
        except Exception:
            log.exception("[GAGAL] %s", t)
            raise

    manifest = {
        "batch_id": batch_id,
        "extracted_at": datetime.now(timezone.utc).isoformat(),
        "tables": results,
    }
    # Manifest dipakai C (untuk load) dan D (untuk validasi row count)
    s3.put_object(
        Bucket=BUCKET,
        Key=f"_manifests/{batch_id}.json",
        Body=json.dumps(manifest, indent=2).encode(),
    )
    log.info("Extract selesai. Manifest: _manifests/%s.json", batch_id)
    return manifest


if __name__ == "__main__":
    run_extract()