# Phase 3: Orchestration & Data Quality

**Goal:** Automated validation and "Dead Letter" routing.

## 1. Airflow Orchestration (`dags/olist_ingestion_dag.py`)
- **Role:** Manages the batch workflow and dependency chain.
- **Key Logic:** `verify_and_purge` task ensures data integrity by verifying S3 upload success before deleting source files.

## 2. Data Quality Gates (`src/validation/`)
- **Tech:** Great Expectations & dbt-expectations.
- **Integration:**
  - Schema validation at the Staging layer (`dbt/models/staging/schema.yml`).
  - Business rule validation (e.g., `delivery_date > purchase_date`).

## 3. Transformation Framework (`dbt/`)
- **Role:** Handles the T in ELT.
- **Structure:**
  - **Staging:** Deduplication and type casting (`stg_orders.sql`).
  - **Marts:** Star schema generation for the Gold layer.

---

**Status:** Code Implemented & Documented ✅
