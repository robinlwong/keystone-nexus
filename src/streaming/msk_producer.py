import json
import time
import os
from kafka import KafkaProducer
from kafka.errors import KafkaError
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MSKProducer:
    def __init__(self, bootstrap_servers):
        # In production with MSK, you'd typically use IAM authentication
        # For development/public MSK, plain or SASL_SSL is common
        self.producer = KafkaProducer(
            bootstrap_servers=bootstrap_servers,
            value_serializer=lambda v: json.dumps(v).encode('utf-8'),
            retries=5,
            acks='all' # Ensure data durability
        )

    def send_order(self, topic, order_data):
        try:
            future = self.producer.send(topic, order_data)
            # Wait for record to be effectively sent
            record_metadata = future.get(timeout=10)
            logger.info(f"Sent message to {record_metadata.topic} partition {record_metadata.partition}")
        except KafkaError as e:
            logger.error(f"Error sending to MSK: {e}")

if __name__ == "__main__":
    BOOTSTRAP_SERVERS = os.getenv("MSK_BOOTSTRAP_SERVERS", "localhost:9092")
    TOPIC = "orders"
    
    producer = MSKProducer(BOOTSTRAP_SERVERS)
    
    # Mock order for testing
    sample_order = {
        "order_id": "msk_test_001",
        "customer_id": "cust_123",
        "order_status": "created",
        "timestamp": time.time()
    }
    
    producer.send_order(TOPIC, sample_order)
    producer.producer.flush()
