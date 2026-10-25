import io
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

from ingestion.config import BUCKET, get_s3, get_staging_engine, get_logger

log = get_logger("load")

SCHEMA = "staging"
DDL_PATH = Path(__file__).resolve().parent.parent / "sql" / "staging" / "01_schema.sql"


def ensure_schema(conn):
    """Jalankan DDL staging (idempotent)."""
    with conn.cursor() as cur:
        cur.execute(DDL_PATH.read_text(encoding="utf-8-sig"))
    conn.commit()


def list_parquet_keys(s3, prefix):
    keys = []
    paginator = s3.get_paginator("list_objects_v2")
    for page in paginator.paginate(Bucket=BUCKET, Prefix=prefix + "/"):
        keys += [o["Key"] for o in page.get("Contents", []) if o["Key"].endswith(".parquet")]
    return sorted(keys)


def load_table(conn, s3, entry, batch_id, ingested_at):
    """Load satu tabel dari MinIO ke staging. Kolom asli tidak diubah."""
    table = entry["table"]
    target = f'{SCHEMA}."{table}"'

    with conn.cursor() as cur:
        # Supaya aman dijalankan ulang untuk batch yang sama
        cur.execute(f"DELETE FROM {target} WHERE batch_id = %s", (batch_id,))

        total = 0
        for key in list_parquet_keys(s3, entry["prefix"]):
            body = s3.get_object(Bucket=BUCKET, Key=key)["Body"].read()
            df = pd.read_parquet(io.BytesIO(body))

            # Satu-satunya manipulasi: kolom penanda landing
            df["source_table"] = table
            df["batch_id"] = batch_id
            df["ingested_at"] = ingested_at

            buf = io.StringIO()
            df.to_csv(buf, index=False, header=False, na_rep="\\N")
            buf.seek(0)
            cols = ", ".join(f'"{c}"' for c in df.columns)
            cur.copy_expert(
                f"COPY {target} ({cols}) FROM STDIN WITH (FORMAT csv, NULL '\\N')", buf
            )
            total += len(df)
            log.info("  %s: %s dimuat (%d baris)", table, key.split("/")[-1], len(df))

        cur.execute(f"SELECT count(*) FROM {target} WHERE batch_id = %s", (batch_id,))
        in_staging = cur.fetchone()[0]

    conn.commit()

    status = "OK" if in_staging == entry["rows"] else "BEDA"
    log.info("[%s] %s: source=%d, staging=%d", status, table, entry["rows"], in_staging)
    if status == "BEDA":
        raise RuntimeError(f"Row count tidak cocok untuk tabel {table}")
    return in_staging


def run_load(batch_id, manifest):
    s3 = get_s3()
    ingested_at = datetime.now(timezone.utc).replace(tzinfo=None).isoformat(sep=" ", timespec="seconds")
    conn = get_staging_engine().raw_connection()
    try:
        ensure_schema(conn)
        log.info("Batch %s: load %d tabel ke schema '%s'", batch_id, len(manifest["tables"]), SCHEMA)
        for entry in manifest["tables"]:
            load_table(conn, s3, entry, batch_id, ingested_at)
        log.info("Load selesai.")
    finally:
        conn.close()