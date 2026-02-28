# AWS MSK - Streaming Ingestion Architecture

## 📋 Overview
As part of the pivot to real-time data processing, Keystone Nexus will leverage **AWS MSK (Managed Streaming for Apache Kafka)**. This transition moves the architecture from a batch-centric model to a near-real-time streaming paradigm.

## 🏗️ MSK Integration in Medallion Architecture

### 1. Source → MSK (Producer)
- **Producers:** Could be the C++ gRPC service (planned) or Python-based Kafka producers.
- **Topics:** Structured by entity (e.g., `orders`, `order_items`, `payments`).
- **Schema Registry:** AWS Glue Schema Registry will enforce data contracts.

### 2. MSK → Bronze (Streaming Ingestion)
- **AWS MSK Connect:** Use the S3 Sink Connector to automatically deliver stream data to S3 Bronze in Parquet format.
- **Alternative:** Spark Streaming or Flink (Kinesis Data Analytics) consuming from MSK and writing to S3.

### 3. Silver & Gold Layers
- **No Change:** dbt will continue to transform the S3 data into Silver and Gold layers. 
- **Benefit:** Transitioning to MSK allows for more frequent dbt runs (micro-batches) to keep the Gold layer fresh.

## 🛠️ Implementation Roadmap

1. **Cluster Provisioning:** Deploy a multi-AZ MSK cluster (m5.large or t3.small for dev).
2. **Topic Configuration:** Define retention policies and partitions.
3. **IAM Integration:** Use IAM Access Control for secure producer/consumer authentication.
4. **Monitoring:** Enable CloudWatch metrics and Prometheus/Grafana dashboards.

## 📂 Repository Recommendation: **Single Repository**

### Why keep it in `keystone-nexus`?
- **Visibility:** One place for evaluators to see the full project evolution from batch to stream.
- **Coordination:** The dbt models and Airflow DAGs are tightly coupled with the data MSK will produce.
- **Simplicity:** Managing one CI/CD pipeline and one set of environment variables is significantly easier for a group project.

### Suggested Folder Structure:
```
keystone-nexus/
├── src/
│   ├── ingestion/       # Batch logic
│   └── streaming/       # NEW: MSK Producers/Consumers
├── infra/               # NEW: Terraform/CloudFormation for MSK
├── dbt/                 # Core transformations
└── docs/
    └── MSK_PIVOT.md     # This documentation
```

---
**Decision:** Proceed with implementing MSK logic within the existing `keystone-nexus` repository under a `/streaming` directory.
