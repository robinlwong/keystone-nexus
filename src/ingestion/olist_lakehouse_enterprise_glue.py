import json
import logging
import os
import boto3
import pyarrow as pa
import pyarrow.parquet as pq
import pyarrow.compute as pc
from confluent_kafka import Consumer
from tenacity import retry, stop_after_attempt, wait_exponential

# AWS Glue Schema Registry Integration
from aws_glue_schema_registry.serde import KafkaDeserializer

# ==========================================
# 1. STRUCTURED LOGGING
# ==========================================
class JsonFormatter(logging.Formatter):
    def format(self, record):
        log_obj = {
            "timestamp": self.formatTime(record),
            "level": record.levelname,
            "message": record.getMessage(),
        }
        return json.dumps(log_obj)

logger = logging.getLogger("lakehouse")
handler = logging.StreamHandler()
handler.setFormatter(JsonFormatter())
logger.addHandler(handler)
logger.setLevel(logging.INFO)

# ==========================================
# 2. CONFIGURATION
# ==========================================
KAFKA_BROKERS = os.getenv("KAFKA_BROKERS", "localhost:9092")
S3_BUCKET = os.getenv("S3_SILVER_BUCKET", "olist-data-lake-silver")

# 3. Initialize Glue Deserializer
glue_client = boto3.client('glue', region_name=os.getenv("AWS_REGION", "ap-southeast-1"))
deserializer = KafkaDeserializer(glue_client=glue_client)

consumer = Consumer({
    'bootstrap.servers': KAFKA_BROKERS,
    'group.id': 'lakehouse-enterprise-writers',
    'auto.offset.reset': 'earliest',
    'enable.auto.commit': False
})
consumer.subscribe(['orders'])

# ==========================================
# 4. CORE LOGIC (RESILIENCE)
# ==========================================
@retry(stop=stop_after_attempt(5), wait=wait_exponential(multiplier=1, min=4, max=10))
def write_to_s3_resilient(table, path):
    pq.write_to_dataset(
        table,
        root_path=path,
        partition_cols=['year', 'month', 'day'],
        compression='snappy'
    )

def process_batch(messages):
    try:
        valid_data = []
        for msg in messages:
            # INTEGRATION: Deserialize and validate against Glue Registry
            payload = deserializer.deserialize(msg.value())
            valid_data.append(payload.data)
        
        arrow_table = pa.Table.from_pylist(valid_data)
        
        # Partitioning logic
        timestamps = pc.strptime(arrow_table.column('order_purchase_timestamp'), format='%Y-%m-%d %H:%M:%S', unit='s')
        arrow_table = arrow_table.append_column('year', pc.year(timestamps))
        arrow_table = arrow_table.append_column('month', pc.month(timestamps))
        arrow_table = arrow_table.append_column('day', pc.day(timestamps))

        write_to_s3_resilient(arrow_table, f"s3://{S3_BUCKET}/orders/")
        consumer.commit()
        logger.info(f"Schema-validated batch written to Silver layer.")

    except Exception as e:
        logger.error(f"Batch Processing Error: {e}")

if __name__ == "__main__":
    logger.info("🚀 Lakehouse Consumer with AWS Glue Integration Starting...")
