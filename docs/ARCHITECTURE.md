# Keystone Nexus - System Architecture

## 🏗️ Design Philosophy
The system is built on the **Data Lakehouse** paradigm, combining the flexibility of a data lake with the performance and governance of a data warehouse.

## 🥇 Medallion Layers

### 1. Bronze Layer (Raw)
- **Format:** Parquet
- **Storage:** `s3://olist-data-lake-bronze/`
- **Logic:** Raw ingestion from source. Immutable storage of historical data.

### 2. Silver Layer (Cleansed)
- **Format:** Parquet (Partitioned by `year/month/day`)
- **Storage:** `s3://olist-data-lake-silver/`
- **Logic:** Data cleaning, type casting, and de-duplication. This layer is the "single source of truth."

### 3. Gold Layer (Curated)
- **Format:** Athena Tables
- **Storage:** `s3://olist-data-lake-gold/`
- **Logic:** Star schema design (Facts/Dimensions). Highly optimized for analytical queries and BI dashboards.

## ⚡ High-Performance Streaming: C++ gRPC Pipeline
While the primary pipeline is Python-based for flexibility, the architecture includes a blueprint for a **C++ gRPC Ingestion Pipeline**.

### Why C++ gRPC?
- **Performance:** Microsecond-level response times for high-throughput streaming.
- **Efficiency:** Low CPU/Memory footprint compared to Python interpreters.
- **Scalability:** Uses Protocol Buffers for efficient data serialization.

### Use Case
- Targeted for future Phase 2 optimization where high-speed IoT or real-time event streaming (Kafka) is required.
- **Trade-offs:** Higher development complexity and strict schema enforcement vs. Python's ease of use and flexibility.

## 🛡️ Technology Decisions

### S3 + Athena vs. Redis
- **Decision:** S3 + Athena was selected for the primary storage and query layer.
- **Rationale:** 
  - **Cost:** S3 is significantly more cost-effective for large historical datasets.
  - **Analytics:** Athena provides SQL-based analytical capabilities across the entire lakehouse without the RAM constraints of a KV store like Redis.
  - **Simplicity:** Serverless architecture reduces operational overhead.
