from datetime import datetime, timezone

from ingestion.config import get_logger
from ingestion.extract import run_extract

log = get_logger("pipeline")


def main():
    batch_id = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S")
    log.info("=== PIPELINE START (batch %s) ===", batch_id)

    # 1. Extract: OLTP -> MinIO
    manifest = run_extract(batch_id)

    # 2. Load: MinIO -> Staging (dikerjakan C di ingestion/load.py)
    try:
        from ingestion.load import run_load
    except ImportError:
        log.warning("ingestion/load.py belum ada, tahap load dilewati.")
    else:
        run_load(batch_id, manifest)

    total = sum(t["rows"] for t in manifest["tables"])
    log.info("=== PIPELINE SELESAI: %d tabel, %d baris total ===",
             len(manifest["tables"]), total)


if __name__ == "__main__":
    main()