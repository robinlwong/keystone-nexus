# Keystone Nexus - Google Docs Content

**Source:** Project collaboration documents  
**Date:** 2026-02-27

---

## Document 1: Great Expectations & ELT Pipeline Guide

### Dataset Comparison
- **Olist (Brazilian E-Commerce):** Best for business insights (orders, reviews, locations, payments)
- **Instacart Market Basket:** Pattern recognition ("people who bought X also bought Y")
- **London Bicycles:** Temporal/spatial analysis (BigQuery EU region constraint!)

### ELT Medallion Architecture

**Bronze Layer (Raw):**
- Goal: 1:1 copy of source data
- No cleaning allowed
- Format: Exact replica (CSV → Parquet)

**Silver Layer (Cleansed):**
- Fix date formats
- Handle null values
- Join tables together
- Start building dimensions and facts

**Gold Layer (Business-Ready):**
- Star Schema (dimension + fact tables)
- Optimized for CEO/CMO queries
- Fast aggregation performance

### Great Expectations Integration

**Python Approach:**
```python
import great_expectations as gx
context = gx.get_context()
suite = context.add_expectation_suite(expectation_suite_name="order_quality_tests")

# Rule: Every order MUST have an ID
context.add_expectation(
    expectation_suite_name="order_quality_tests",
    expectation_configuration=gx.expectations.ExpectColumnValuesToNotBeNull(column="order_id")
)
```

**dbt-expectations Approach (YAML):**
```yaml
version: 2

models:
  - name: stg_orders
    columns:
      - name: order_id
        tests:
          - not_null
          - unique
      
      - name: order_status
        tests:
          - accepted_values:
              values: ['delivered', 'shipped', 'canceled', 'invoiced', 'processing']
      
      - name: order_purchase_timestamp
        tests:
          - dbt_expectations.expect_column_values_to_be_between:
              min_value: "2016-01-01"
              max_value: "CURRENT_DATE"
```

### dbt Project Structure (Medallion)

```
ecommerce_dbt_project/
├── dbt_project.yml
├── packages.yml
└── models/
    ├── staging/        # Bronze Layer
    │   ├── stg_orders.sql
    │   └── schema.yml
    ├── intermediate/   # Silver Layer
    │   └── int_orders_joined_items.sql
    └── marts/          # Gold Layer
        ├── dim_customer.sql
        ├── dim_product.sql
        ├── fact_sales.sql
        └── schema.yml
```

### fact_sales.sql Example

```sql
{{ config(materialized='table') }}

WITH orders AS (
    SELECT * FROM {{ ref('stg_orders') }}
),
order_items AS (
    SELECT * FROM {{ ref('stg_order_items') }}
)

SELECT 
    o.order_id,
    oi.order_item_id,
    o.customer_id,
    oi.product_id,
    oi.seller_id,
    o.order_purchase_timestamp,
    CAST(TO_CHAR(o.order_purchase_timestamp, 'YYYYMMDD') AS INT) AS date_key,
    oi.price,
    oi.freight_value,
    (oi.price + oi.freight_value) AS total_order_value,
    DATEDIFF(day, o.order_purchase_timestamp, o.order_delivered_customer_date) AS delivery_lag_days
FROM orders o
JOIN order_items oi ON o.order_id = oi.order_id
WHERE o.order_status = 'delivered'
```

### Key Concepts

**ref() Function:**
- Creates dependency graph
- dbt knows build order automatically

**config() Block:**
- Tells dbt how to materialize (table, view, incremental)
- No need to write CREATE TABLE manually

**BigQuery EU Constraint:**
- Compute and storage MUST be in same region
- Configure in `profiles.yml`: `location: EU`
- GDPR compliance + cost optimization

---

## Document 2: init_olist_expectations.py

**Purpose:** Programmatic Great Expectations suite for Olist logistics data

**Key Rules:**
1. **Primary Key Integrity:** order_id not null, unique
2. **Chronological Integrity:** delivery_date > purchase_date (no "time travel")
3. **Delivery Gap Baseline:** estimated_delivery > purchase_date
4. **Status Validation:** Must be in predefined set

**Integration:**
- Generates JSON in `gx/expectations/` directory
- Airflow DAG reads JSON file
- Executes against Parquet files in Silver bucket via Athena
- Corrupted data → Dead Letter Quarantine

---

## Document 3: Project Naming

**Selected:** Project Keystone (now "Keystone Nexus")

**Other Options:**
- Trust & Quality: ClearStream, TrueNorth ELT, Aegis Analytics
- Architecture: StellaMart Pipeline, Nexus Commerce
- **Action & Velocity: FlowForge, Olisto Dynamics, DataPulse** ← Gemini's "woke" names 😄

---

## Document 4: (Access Denied - Private)

Unable to fetch. Likely contains additional implementation details or team coordination notes.

---

**Status:** Documents reviewed and archived  
**Next:** Implement Great Expectations script and research data quality importance
