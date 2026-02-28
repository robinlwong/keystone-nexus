# Phase 2: Resilient Lakehouse Consumption

**Goal:** Reliable consumption from Kafka to S3 Bronze/Silver layers.

## 1. Python Lakehouse Consumer (`src/ingestion/olist_lakehouse_enterprise.py`)
- **Role:** Consumes from MSK and writes partitioned Parquet to S3.
- **Tech:** `confluent-kafka` + `pyarrow` (Apache Arrow).
- **Optimization:**
  - In-memory columnar processing for speed.
  - Dynamic partitioning (`year/month/day`) for Athena query cost reduction.
- **Resilience:**
  - `tenacity` library implementation for exponential backoff on S3 writes.
  - Structured JSON logging (`JsonFormatter`) for Datadog/CloudWatch integration.

## 2. Data Lake Storage (S3)
- **Bronze:** Raw ingestion landing zone.
- **Silver:** Cleansed and partitioned data (single source of truth).

---

**Status:** Code Implemented & Documented ✅
