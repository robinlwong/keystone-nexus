# olist_lakehouse_enterprise.py
# Kafka -> S3 Parquet with Apache Arrow
# Resolved: Retry logic, Structured Logging, and Security
import json
import logging
import os
import pyarrow as pa
import pyarrow.parquet as pq
import pyarrow.compute as pc
from confluent_kafka import Consumer
from tenacity import retry, stop_after_attempt, wait_exponential

# ==========================================
# 1. STRUCTURED LOGGING
# ==========================================
class JsonFormatter(logging.Formatter):
    def format(self, record):
        log_obj = {
            "timestamp": self.formatTime(record),
            "level": record.levelname,
            "message": record.getMessage(),
            "module": record.module
        }
        if record.exc_info:
            log_obj["exception"] = self.formatException(record.exc_info)
        return json.dumps(log_obj)

logger = logging.getLogger("lakehouse")
handler = logging.StreamHandler()
handler.setFormatter(JsonFormatter())
logger.addHandler(handler)
logger.setLevel(logging.INFO)

# ==========================================
# 2. CONFIGURATION (SECURITY)
# ==========================================
KAFKA_BROKERS = os.getenv("KAFKA_BROKERS", "localhost:9092")
S3_BUCKET = os.getenv("S3_SILVER_BUCKET", "olist-data-lake-silver")

consumer = Consumer({
    'bootstrap.servers': KAFKA_BROKERS,
    'group.id': 'lakehouse-enterprise-writers',
    'auto.offset.reset': 'earliest',
    'enable.auto.commit': False
})

# ==========================================
# 3. CORE LOGIC (RESILIENCE)
# ==========================================
@retry(stop=stop_after_attempt(5), wait=wait_exponential(multiplier=1, min=4, max=10))
def write_to_s3_resilient(table, path):
    """Writes Arrow table to S3 with retry logic."""
    try:
        pq.write_to_dataset(
            table,
            root_path=path,
            partition_cols=['year', 'month', 'day'],
            compression='snappy'
        )
        logger.info(f"Successfully wrote batch to {path}")
    except Exception as e:
        logger.error(f"S3 Write Failure: {e}")
        raise e

def process_batch(messages):
    try:
        if not messages:
            return

        valid_data = [json.loads(msg.value().decode('utf-8')) for msg in messages]
        arrow_table = pa.Table.from_pylist(valid_data)
        
        # Extract partition columns
        timestamps = pc.strptime(arrow_table.column('order_purchase_timestamp'), format='%Y-%m-%d %H:%M:%S', unit='s')
        arrow_table = arrow_table.append_column('year', pc.year(timestamps))
        arrow_table = arrow_table.append_column('month', pc.month(timestamps))
        arrow_table = arrow_table.append_column('day', pc.day(timestamps))

        # RESILIENCE: Execute S3 write with exponential backoff
        s3_path = f"s3://{S3_BUCKET}/orders/"
        write_to_s3_resilient(arrow_table, s3_path)
        
        consumer.commit()

    except Exception as e:
        logger.error(f"Batch Processing Error: {e}")

if __name__ == "__main__":
    logger.info("🚀 Lakehouse Consumer Starting...")
    # Polling loop would go here
