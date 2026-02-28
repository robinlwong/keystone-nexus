# Changelog - Keystone Nexus

All notable changes to the Keystone Nexus project will be documented in this file.

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
