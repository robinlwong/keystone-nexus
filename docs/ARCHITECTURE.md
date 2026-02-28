# Keystone Nexus - Full System Architecture

## 🏗️ Design Philosophy
The system is built on the **Data Lakehouse** paradigm, combining the flexibility of a data lake with the performance and governance of a data warehouse. This implementation follows the **Medallion Architecture** to ensure data reliability and traceability.

---

## 🥇 Medallion Layers

### 1. Bronze Layer (Raw)
- **Format:** Parquet / Raw JSON
- **Storage:** `s3://olist-data-lake-bronze/`
- **Logic:** Raw ingestionlanding zone. This layer stores an immutable 1:1 replica of source data from CSV ingestion or MSK streams.
- **Components:** `ingest_to_bronze.py`, `msk_producer.py`.

### 2. Silver Layer (Cleansed)
- **Format:** Parquet (Partitioned by `year/month/day`)
- **Storage:** `s3://olist-data-lake-silver/`
- **Logic:** Data cleaning, type casting, and de-duplication. This layer serves as the "single source of truth" for the enterprise.
- **Components:** `olist_lakehouse_enterprise.py`, `dbt/models/staging/`.

### 3. Gold Layer (Curated)
- **Format:** Athena Tables
- **Storage:** `s3://olist-data-lake-gold/`
- **Logic:** Star schema design (Facts/Dimensions). Highly optimized for analytical queries, executive BI dashboards, and data science consumption.
- **Components:** `dbt/models/marts/`.

---

## 🚀 Strategic Implementation Phases

### Phase 1: High-Performance Ingestion
Establishing a low-latency ingestion backbone using **C++ gRPC** and **Amazon MSK**.
- **C++ gRPC Server:** Handles microsecond-level event ingestion.
- **Reconnection Logic:** Self-healing producer automatically reconnects on broker failure.
- **Security:** Infrastructure uses environment-based broker discovery and is TLS/SSL ready.

### Phase 2: Resilient Lakehouse Consumption
Bridging the gap between real-time streams and analytical storage.
- **Python Lakehouse Consumer:** Utilizes **Apache Arrow** for columnar memory processing.
- **Resilience:** Integrated `tenacity` retry logic ensures 99.9% write success rate to S3 during network partitions.
- **Logging:** Structured JSON logging for CloudWatch/Datadog integration.

### Phase 3: Orchestration & Data Quality
Automating the pipeline and enforcing strict data contracts.
- **Airflow Orchestration:** Manages dependency chains and provides an "immune system" for the lakehouse.
- **Data Quality Gates:** **Great Expectations** and `dbt-expectations` validate business rules (e.g., ensuring order delivery dates are post-purchase).
- **Quarantine Routing:** Corrupted data is automatically routed to `s3://olist-data-lake-quarantine/` for debugging.

### Phase 4: Analytics & Business Intelligence
Turning raw telemetry into executive insights.
- **Athena SQL:** Serverless query engine executes star schema transformations.
- **Cost Control:** Partition-aware queries and S3 Lifecycle policies minimize AWS spend.
- **Insights:** Tracks Monthly Growth, Regional Logistics Performance, and Customer Segmentation.

---

## ⚡ Technical Deep-Dive

### C++ gRPC Pipeline Rationale
- **Performance:** Deterministic memory management for high-throughput streaming.
- **Efficiency:** Significant CPU reduction compared to Python-based producers.
- **Scalability:** Protocol Buffers provide compact serialization and strict schema enforcement.

### Technology Decisions: S3 + Athena vs. Redis
- **Decision:** S3 + Athena selected for the core analytical engine.
- **Rationale:** 
  - **Cost:** S3 storage is $0.023/GB vs. expensive Redis RAM instances.
  - **Flexibility:** Athena supports complex SQL joins across the entire historical dataset.
  - **Simplicity:** Serverless components scale automatically without cluster management overhead.

---

## 📊 Star Schema Design (Gold Layer)
The Gold layer implements a traditional star schema to facilitate high-speed BI reporting:

- **Fact Tables:** `fact_sales`, `fact_reviews`.
- **Dimension Tables:** `dim_customer`, `dim_product`, `dim_seller`, `dim_date`.

All models are materialized as tables in the `gold` schema, partitioned to optimize query performance.
