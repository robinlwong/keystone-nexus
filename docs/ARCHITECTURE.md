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

### 2. Silver Layer (Cleansed & Joined)
- **Format:** Parquet (Partitioned by `year/month/day`)
- **Storage:** `s3://olist-data-lake-silver/`
- **Logic:** 
  - **Staging:** Data cleaning, type casting, and de-duplication (`stg_*` models).
  - **Intermediate:** Complex joins across the 9-file dataset (e.g., `int_orders_joined`). This layer resolves 1-to-many fan-out risks before final aggregation.
- **Components:** `olist_lakehouse_enterprise.py`, `dbt/models/staging/`, `dbt/models/intermediate/`.

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

---

## 📈 Strategic Recommendations & Deficiency Mitigations

To ensure this Enterprise Lakehouse operates flawlessly at scale, the following architectural controls have been implemented:

### 1. Schema Evolution (AWS Glue Schema Registry)
- **Deficiency:** Hard-coded JSON parsing in the consumer is brittle. If the source platform updates an event payload, downstream Parquet files will be corrupted, breaking Athena queries.
- **Remedy:** Leverage the **AWS Glue Schema Registry**. By connecting Kafka to this registry, payloads that violate the registered schema are rejected at the ingestion layer. This ensures downstream queries never fail due to unexpected structural changes.

### 2. Cost Mitigation with Athena Partitioning
- **Deficiency:** Athena charges per byte scanned ($5 per TB). Unbounded queries could scan the entire multi-year database, causing prohibitive costs.
- **Remedy:** Mandatory **year/month/day partitioning**. By bounding SQL queries to specific partitions, scan volume is reduced by up to 98%, ensuring predictable cloud spend.

### 3. RDS Connection Pooling (Amazon RDS Proxy)
- **Deficiency:** Operational queries (e.g., shipment status checks) hit the RDS PostgreSQL database. Auto-scaling EC2 workers would rapidly exhaust the database's concurrent connection limit.
- **Remedy:** Route all microservice connections through **Amazon RDS Proxy**. This service pools and shares database connections, preventing the DB from being overwhelmed during traffic spikes.

### 4. Resilience (AWS ASG & Airflow Orchestration)
- **Deficiency:** Static worker nodes cannot efficiently handle e-commerce traffic spikes without over-provisioning (wasting money) or under-provisioning (causing lag).
- **Remedy:** Utilize **AWS Auto Scaling Groups** bound to **CloudWatch alarms** monitoring Kafka Consumer Lag. Instances scale-out automatically to catch up. This is orchestrated by **Apache Airflow (MWAA)** to guarantee data fidelity between layers.

### 5. Ecosystem Tooling: Adopt pnpm
- **Deficiency:** Standard package managers lead to disk bloat on EC2 and slow CI/CD pipeline builds.
- **Remedy:** **Standardization on pnpm.** Utilizing a global content-addressable store on the OS minimizes disk usage and significantly accelerates AWS CodeBuild pipelines by eliminating redundant dependency downloads.
