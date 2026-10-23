import os
import boto3
import psycopg2
from botocore.exceptions import ClientError
from dotenv import load_dotenv

load_dotenv()

def check_pg(name, port, db, user, pw):
    conn = psycopg2.connect(host="localhost", port=port, dbname=db, user=user, password=pw)
    conn.close()
    print(f"[OK] {name}")

check_pg("PostgreSQL OLTP", os.getenv("OLTP_PORT"), os.getenv("OLTP_DB"),
         os.getenv("OLTP_USER"), os.getenv("OLTP_PASSWORD"))
check_pg("PostgreSQL Staging", os.getenv("STG_PORT"), os.getenv("STG_DB"),
         os.getenv("STG_USER"), os.getenv("STG_PASSWORD"))

s3 = boto3.client("s3", endpoint_url="http://localhost:9000",
                  aws_access_key_id=os.getenv("MINIO_ROOT_USER"),
                  aws_secret_access_key=os.getenv("MINIO_ROOT_PASSWORD"),
                  region_name="us-east-1")
bucket = os.getenv("MINIO_BUCKET", "raw")
try:
    s3.head_bucket(Bucket=bucket)
except ClientError:
    s3.create_bucket(Bucket=bucket)
    print(f"[INFO] bucket '{bucket}' dibuat")

buckets = [b["Name"] for b in s3.list_buckets()["Buckets"]]
print(f"[OK] MinIO, bucket: {buckets}")