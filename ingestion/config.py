import os
import logging
import boto3
from botocore.config import Config
from dotenv import load_dotenv
from sqlalchemy import create_engine

load_dotenv()

BUCKET = os.getenv("MINIO_BUCKET", "raw")
CHUNK_SIZE = 100_000  # baris per file Parquet


def get_oltp_engine():
    url = (f"postgresql+psycopg2://{os.getenv('OLTP_USER')}:{os.getenv('OLTP_PASSWORD')}"
           f"@localhost:{os.getenv('OLTP_PORT')}/{os.getenv('OLTP_DB')}")
    return create_engine(url)


def get_staging_engine():
    url = (f"postgresql+psycopg2://{os.getenv('STG_USER')}:{os.getenv('STG_PASSWORD')}"
           f"@localhost:{os.getenv('STG_PORT')}/{os.getenv('STG_DB')}")
    return create_engine(url)


def get_s3():
    return boto3.client(
        "s3",
        endpoint_url="http://localhost:9000",
        aws_access_key_id=os.getenv("MINIO_ROOT_USER"),
        aws_secret_access_key=os.getenv("MINIO_ROOT_PASSWORD"),
        region_name="us-east-1",
        config=Config(s3={"addressing_style": "path"}),
    )


def get_logger(name):
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )
    return logging.getLogger(name)