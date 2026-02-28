import json
import time
import os
import logging
import boto3
from kafka import KafkaProducer
from kafka.errors import KafkaError

# AWS Glue Schema Registry Integration
from aws_glue_schema_registry.serde import KafkaSerializer
from aws_glue_schema_registry.adapter.jsonschema import JsonSchemaAdapter

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MSKProducer:
    def __init__(self, bootstrap_servers, registry_name='keystone-registry'):
        self.bootstrap_servers = bootstrap_servers
        self.registry_name = registry_name
        
        # 1. Initialize AWS Glue Schema Registry Serializer
        # This automatically registers/retrieves schemas from AWS Glue
        glue_client = boto3.client('glue', region_name=os.getenv("AWS_REGION", "ap-southeast-1"))
        self.serializer = KafkaSerializer(
            glue_client=glue_client,
            registry_name=self.registry_name,
            adapter=JsonSchemaAdapter()
        )

        # 2. Initialize Kafka Producer with Glue Serializer
        self.producer = KafkaProducer(
            bootstrap_servers=bootstrap_servers,
            value_serializer=self.serializer, # Enforces schema contracts
            retries=5,
            acks='all'
        )

    def send_record(self, topic, data, schema_name):
        """
        Sends data to MSK with schema validation.
        """
        try:
            # The serializer handles the schema registration under schema_name
            future = self.producer.send(topic, value=(data, schema_name))
            record_metadata = future.get(timeout=10)
            logger.info(f"Verified & Sent to {record_metadata.topic} with schema '{schema_name}'")
        except Exception as e:
            logger.error(f"Schema Validation or Send Failure: {e}")

if __name__ == "__main__":
    BOOTSTRAP_SERVERS = os.getenv("MSK_BOOTSTRAP_SERVERS", "localhost:9092")
    TOPIC = "orders"
    
    producer = MSKProducer(BOOTSTRAP_SERVERS)
    
    # Order schema defined as Python dict (converted to JSON Schema by adapter)
    order_data = {
        "order_id": f"ORD-{int(time.time())}",
        "customer_id": "CUST-999",
        "order_status": "delivered",
        "timestamp": str(datetime.utcnow())
    }
    
    # The 'order_schema' must exist or will be auto-created in the registry
    producer.send_record(TOPIC, order_data, schema_name="OlistOrderSchema")
    producer.producer.flush()
