# Keystone Nexus - Technology Stack Documentation

This document provides a comprehensive overview of the technologies, frameworks, and cloud services used in the Keystone Nexus project.

---

## 🌩️ AWS Cloud Infrastructure (The Backbone)

The following AWS services are utilized to provide a scalable, serverless-first architecture for the Data Lakehouse.

| Service | Role in Project | Implementation Detail |
|:---|:---|:---|
| **AWS S3** | Data Lake Storage | Persistent storage for Bronze (Raw), Silver (Cleansed), and Gold (Business) layers. |
| **AWS MSK** | Managed Streaming | Apache Kafka cluster for high-velocity real-time event ingestion. |
| **AWS Glue** | Data Catalog & Schema Registry | Manages metadata, schema versioning, and enforces data contracts via Schema Registry. |
| **AWS Athena** | Serverless Query Engine | Executes SQL transformations and analytical queries directly against S3 Parquet files. |
| **AWS Secrets Manager** | Security & Credentials | Securely stores API keys, database credentials, and IAM secrets (no hardcoding). |
| **AWS EC2** | Compute Nodes | Hosts the C++ gRPC ingestion server and Python Lakehouse consumers on Ubuntu 24.04. |
| **Amazon MWAA** | Orchestration (Managed Airflow) | Coordinates the end-to-end pipeline, sensors, and data quality checkpoints. |
| **Amazon RDS** | Operational State | Manages transactional state and Airflow metadata via PostgreSQL. |
| **CloudWatch** | Monitoring & Alerting | Tracks metrics for Kafka consumer lag, S3 storage growth, and pipeline failures. |

---

## 🛠️ Software & Framework Stack

### Ingestion & Streaming
- **C++ (std=c++17):** Utilized for the high-performance gRPC ingestion server (`olist_ingestion_enterprise.cc`).
- **gRPC / Protocol Buffers:** Low-latency communication protocol for e-commerce event telemetry.
- **librdkafka:** The underlying C/C++ library for resilient Kafka production.
- **Python Kafka Client:** (`kafka-python` / `confluent-kafka`) used for Python-based producers and consumers.

### Data Processing & Transformation
- **dbt (Data Build Tool):** The core transformation engine for the Medallion architecture.
- **Apache Arrow (PyArrow):** High-speed, in-memory columnar data manipulation for the Lakehouse consumer.
- **Pandas:** Used for initial CSV analysis and lightweight data cleaning.
- **FastParquet:** Engine for writing optimized Parquet files to S3 with Snappy compression.

### Data Quality & Orchestration
- **Great Expectations:** The "immune system" of the pipeline, providing automated business logic validation.
- **dbt-expectations:** Integrated schema and value constraint testing within the dbt models.
- **Apache Airflow:** Workflow orchestration using Python-based DAGs.
- **Tenacity:** Python library for implementing exponential backoff retry logic for cloud operations.

### Deployment & Tooling
- **Git:** Version control and collaboration.
- **pnpm / Node.js:** Manages frontend dashboard dependencies and accelerates CI/CD pipelines.
- **dotenv:** Management of environment-specific configurations (gitignored).
- **JSON Logging:** Structured logging implemented across C++ and Python for enterprise observability.

---
**Status:** All components integrated and production-ready. 🎯
