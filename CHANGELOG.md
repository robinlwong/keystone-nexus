# Changelog - Keystone Nexus

All notable changes to the Keystone Nexus project will be documented in this file.

## [1.6.0] - 2026-03-01
### Added
- **Auto Scaling Strategy:** Implemented AWS Auto Scaling Group (ASG) configuration (`infra/asg/asg_config.json`) for Python worker elasticity.
- **CloudWatch Monitoring:** Added CloudWatch alarm configuration (`infra/asg/cloudwatch_alarm.json`) to trigger scaling based on Kafka Consumer Lag.
- **Resilience Documentation:** Created `docs/RESILIENCE_STRATEGY.md` detailing the integration between ASG compute elasticity and Airflow data fidelity orchestration.

## [1.5.0] - 2026-03-01
### Added
- **Amazon RDS Proxy Integration:** Implemented connection pooling configuration (`infra/rds/proxy_config.json`) to prevent connection exhaustion during high-throughput operational query spikes.
- **Database Strategy Documentation:** Created `docs/DATABASE_STRATEGY.md` detailing the transition from direct DB access to proxied multiplexing.

## [1.4.0] - 2026-03-01
### Added
- **Intermediate Layer (`int_orders_joined.sql`):** Implemented a "Wide Table" to resolve complex 1-to-many relationships (Orders → Items/Payments) before Gold aggregation.
- **Staging Models:** Added `stg_order_payments.sql` and `stg_geolocation.sql` to support revenue reconciliation and geospatial analysis.
- **Gap Analysis Report:** Created `docs/IMPLEMENTATION_GAP_ANALYSIS.md` detailing the strategy for joining 9 disparate datasets and justifying dbt tooling decisions.

## [1.3.0] - 2026-02-28
### Added
- **Athena Partitioning Logic:** Implemented non-negotiable cost mitigation by bounding `fact_sales` and `fact_reviews` to specific `year/month/day` partitions.
- **Incremental Materialization:** Updated `dbt_project.yml` to use incremental materialization for Gold layer tables to further reduce scan volume.

## [1.2.0] - 2026-02-28
### Added
- **AWS Glue Schema Registry Integration:** Implemented data contract enforcement in `src/streaming/msk_producer_glue.py` and `src/ingestion/olist_lakehouse_enterprise_glue.py`.
- **Dynamic Schema Validation:** Automated schema registration and validation for MSK streaming events.

## [1.1.0] - 2026-02-28
### Added
- **dbt Marts Layer:** Implemented full Star Schema with `dim_customer`, `dim_product`, `dim_seller`, `dim_date`, `fact_sales`, and `fact_reviews`.
- **MSK Streaming Pivot:** Added `src/streaming/msk_producer.py` and `infra/msk/cluster_config.json` for AWS MSK integration.
- **Enterprise Ingestion:** Implemented `olist_ingestion_enterprise.cc` (C++ gRPC) and `olist_lakehouse_enterprise.py` (Python Arrow consumer).
- **Phased Documentation:** Restructured deployment roadmap into 4 distinct phases (`docs/phases/`).
- **Knowledge Integration:** Synced research notes and Redis decision documentation into `docs/`.

### Fixed
- **Staging Models:** Populated empty `stg_customers`, `stg_order_items`, `stg_products`, and `stg_sellers` files with SQL logic.
- **DAG Reliability:** Added S3 verification logic to `dags/olist_ingestion_dag.py` to prevent data loss.
- **Security:** Scrubbed private contact numbers from public documentation to maintain OpSec.

### Changed
- **Architecture Doc:** Consolidated all deployment phases and technical rationales into a comprehensive 100+ line `ARCHITECTURE.md`.
- **README:** Updated project overview to reflect the shift to real-time streaming with AWS MSK.

## [1.0.0] - 2026-02-27
### Added
- **Project Foundation:** Initial repository structure, `.gitignore`, and `README.md`.
- **Implementation Plan:** Comprehensive 5-phase roadmap and cost estimation.
- **Automation:** Created `setup.sh` for environment and S3 bucket initialization.
- **Data Quality:** Jarvis added Great Expectations suite and Data Quality Research documentation.
- **Status Reporting:** Initial `PROJECT_STATUS.md` and requirements coverage mapping.
