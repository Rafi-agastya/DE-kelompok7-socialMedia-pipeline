import io
import sys
from pathlib import Path

import pyarrow.parquet as pq
from sqlalchemy import text

from ingestion.config import BUCKET, get_oltp_engine, get_staging_engine, get_s3, get_logger
from ingestion.load import list_parquet_keys

log = get_logger("validate")


def latest_batch_id(s3):
    objs = s3.list_objects_v2(Bucket=BUCKET, Prefix="_manifests/").get("Contents", [])
    if not objs:
        raise RuntimeError("Belum ada manifest di MinIO. Jalankan run_pipeline.py dulu.")
    return sorted(o["Key"] for o in objs)[-1].split("/")[-1].replace(".json", "")


def minio_rows(s3, prefix):
    total = 0
    for key in list_parquet_keys(s3, prefix):
        body = s3.get_object(Bucket=BUCKET, Key=key)["Body"].read()
        total += pq.ParquetFile(io.BytesIO(body)).metadata.num_rows
    return total


def main():
    s3 = get_s3()
    batch_id = sys.argv[1] if len(sys.argv) > 1 else latest_batch_id(s3)
    oltp, stg = get_oltp_engine(), get_staging_engine()

    with oltp.connect() as c:
        tables = [r[0] for r in c.execute(text(
            "SELECT table_name FROM information_schema.tables "
            "WHERE table_schema='public' AND table_type='BASE TABLE' ORDER BY 1"))]

    rows, all_ok = [], True
    for t in tables:
        with oltp.connect() as c:
            n_oltp = c.execute(text(f'SELECT count(*) FROM public."{t}"')).scalar()
        n_minio = minio_rows(s3, f"{t}/dt={batch_id[:8]}/batch_id={batch_id}")
        with stg.connect() as c:
            n_stg = c.execute(text(
                f'SELECT count(*) FROM staging."{t}" WHERE batch_id = :b'), {"b": batch_id}).scalar()
            n_null = c.execute(text(
                f'SELECT count(*) FROM staging."{t}" WHERE batch_id = :b AND '
                f'(source_table IS NULL OR batch_id IS NULL OR ingested_at IS NULL)'),
                {"b": batch_id}).scalar()

        ok = n_oltp == n_minio == n_stg and n_null == 0
        all_ok &= ok
        rows.append((t, n_oltp, n_minio, n_stg, n_null, "PASS" if ok else "FAIL"))

    header = ("Tabel", "OLTP", "MinIO", "Staging", "Kolom penanda kosong", "Status")
    lines = [f"Validasi batch {batch_id}", "",
             "| " + " | ".join(header) + " |",
             "|" + "---|" * len(header)]
    for r in rows:
        lines.append("| " + " | ".join(f"{v:,}" if isinstance(v, int) else str(v) for v in r) + " |")
    tot = [sum(r[i] for r in rows) for i in (1, 2, 3)]
    lines.append(f"| **TOTAL** | {tot[0]:,} | {tot[1]:,} | {tot[2]:,} | | "
                 f"**{'PASS' if all_ok else 'FAIL'}** |")

    report = "\n".join(lines)
    print("\n" + report)
    Path("docs").mkdir(exist_ok=True)
    Path("docs/validation_report.md").write_text(report, encoding="utf-8")
    log.info("Laporan disimpan: docs/validation_report.md")
    sys.exit(0 if all_ok else 1)


if __name__ == "__main__":
    main()
    