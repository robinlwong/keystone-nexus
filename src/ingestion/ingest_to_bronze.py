import os
import json
import logging
import boto3
import pandas as pd
from datetime import datetime
from botocore.exceptions import ClientError
from tenacity import retry, stop_after_attempt, wait_exponential

# ==========================================
# 1. CONFIGURATION & LOGGING
# ==========================================
class JsonFormatter(logging.Formatter):
    """Custom JSON formatter for structured logging."""
    def format(self, record):
        log_obj = {
            "timestamp": self.formatTime(record),
            "level": record.levelname,
            "message": record.getMessage(),
            "module": record.module,
            "func": record.funcName
        }
        if record.exc_info:
            log_obj["exception"] = self.formatException(record.exc_info)
        return json.dumps(log_obj)

# Setup logging
logger = logging.getLogger("ingestion")
handler = logging.StreamHandler()
handler.setFormatter(JsonFormatter())
logger.addHandler(handler)
logger.setLevel(logging.INFO)

# Environment variables
S3_BRONZE_BUCKET = os.getenv("S3_BRONZE_BUCKET", "olist-data-lake-bronze")
AWS_REGION = os.getenv("AWS_REGION", "ap-southeast-1")

# ==========================================
# 2. AWS HELPERS (SECRETS & S3)
# ==========================================
def get_secret(secret_name):
    """Retrieves secrets from AWS Secrets Manager."""
    session = boto3.session.Session()
    client = session.client(service_name='secretsmanager', region_name=AWS_REGION)
    try:
        response = client.get_secret_value(SecretId=secret_name)
        return json.loads(response['SecretString'])
    except ClientError as e:
        logger.error(f"Failed to retrieve secret {secret_name}: {e}")
        return None

@retry(stop=stop_after_attempt(5), wait=wait_exponential(multiplier=1, min=4, max=10))
def upload_to_s3(file_path, bucket, object_name):
    """Uploads a file to S3 with exponential backoff retry logic."""
    s3_client = boto3.client('s3', region_name=AWS_REGION)
    try:
        s3_client.upload_file(file_path, bucket, object_name)
        logger.info(f"Successfully uploaded {file_path} to s3://{bucket}/{object_name}")
        return True
    except ClientError as e:
        logger.error(f"Upload failed for {file_path}: {e}")
        raise e

# ==========================================
# 3. CORE INGESTION LOGIC
# ==========================================
def process_file_to_bronze(local_csv_path, table_name):
    """
    Converts local CSV to Parquet and uploads to Bronze layer.
    """
    try:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        parquet_path = f"/tmp/{table_name}_{timestamp}.parquet"
        
        # 1. Read CSV and convert to Parquet
        logger.info(f"Processing {local_csv_path} to Parquet...")
        df = pd.read_csv(local_csv_path)
        df.to_parquet(parquet_path, index=False)
        
        # 2. Upload to S3 Bronze
        s3_key = f"raw/{table_name}/{table_name}_{timestamp}.parquet"
        upload_to_s3(parquet_path, S3_BRONZE_BUCKET, s3_key)
        
        # 3. Cleanup local temp file
        os.remove(parquet_path)
        return True
        
    except Exception as e:
        logger.error(f"Failed to process {table_name}: {e}")
        return False

if __name__ == "__main__":
    # Example usage for one table
    # In production, this would be triggered by Airflow with dynamic paths
    tables = ["orders", "order_items", "customers"]
    
    for table in tables:
        # Mock local file path for testing
        mock_path = f"data/olist_{table}_dataset.csv"
        if os.path.exists(mock_path):
            process_file_to_bronze(mock_path, table)
        else:
            logger.warning(f"File {mock_path} not found. Skipping...")
