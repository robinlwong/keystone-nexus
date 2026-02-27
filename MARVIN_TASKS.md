# Marvin's Task List - Keystone Nexus Group Project

**Date:** 2026-02-27  
**Project:** NTU M2G6 Data Engineering Group Project  
**Your Role:** Code debugging, README.md, dbt framework, ELT medallion implementation

---

## 🎯 Your Assigned Tasks

### 1. **Code Debugging & Error Check**

**Files to Review:**
- `src/ingestion/` - Will contain ingestion scripts
- `dags/` - Airflow DAG files
- `src/transformation/` - dbt models (when created)

**Focus Areas:**
- Function naming consistency (Python: `snake_case`, C++: `PascalCase`)
- Error handling (add try-catch blocks, retries for S3/Kafka failures)
- Security (no hardcoded credentials, use AWS Secrets Manager)
- Logging (structured JSON logging for better observability)

**Known Issues from Architecture Docs:**
```python
# ⚠️ C++ gRPC server needs error handling
# Current: No exception handling around Kafka producer
# Fix: Add try-catch blocks and reconnection logic

# ⚠️ Python Lakehouse consumer needs retry logic
# Current: No retry for S3 failures
# Fix: Add exponential backoff for boto3 operations

# ⚠️ Airflow DAG needs S3 verification
# Current: Assumes S3 copy always succeeds
# Fix: Add assertion to verify quarantine upload before purging
```

---

### 2. **README.md for Repository**

**Create:** `~/projects/keystone-nexus/README.md`

**Required Sections:**
```markdown
# Keystone Nexus
[Project badge: Build Status, License, etc.]

## 📋 Project Overview
- Brief description (1-2 paragraphs)
- Dataset: Brazilian E-Commerce (Olist)
- Tech stack: AWS S3, Athena, Airflow, dbt, Great Expectations

## 🏗️ Architecture
- Medallion architecture diagram (Bronze → Silver → Gold)
- Star schema ERD
- Data flow diagram

## 🚀 Quick Start
- Prerequisites (Python 3.11, AWS CLI, dbt)
- Setup instructions (./setup.sh)
- Run ingestion (python src/ingestion/...)
- Run transformations (dbt run)

## 📊 Data Quality
- Great Expectations integration
- Validation rules summary
- How to view Data Docs

## 🧪 Testing
- How to run tests (pytest, dbt test)
- Great Expectations checkpoints

## 📁 Project Structure
- Directory tree explanation

## 🤝 Contributors
- Team members

## 📄 License
```

**Tone:** Professional but accessible (mixed technical + business audience)

---

### 3. **Parse e2e dbt Framework**

**Create dbt Project Structure:**
```
keystone-nexus/
└── dbt/
    ├── dbt_project.yml
    ├── packages.yml
    ├── profiles.yml.example
    └── models/
        ├── staging/        # Bronze → Silver
        │   ├── stg_orders.sql
        │   ├── stg_order_items.sql
        │   ├── stg_customers.sql
        │   ├── stg_products.sql
        │   ├── stg_sellers.sql
        │   └── schema.yml  # Great Expectations YAML here!
        │
        ├── intermediate/   # Silver → Pre-Gold
        │   ├── int_orders_joined_items.sql
        │   └── int_customer_lifetime_value.sql
        │
        └── marts/          # Gold Layer (Star Schema)
            ├── dim_customer.sql
            ├── dim_product.sql
            ├── dim_seller.sql
            ├── dim_date.sql
            ├── fact_sales.sql
            ├── fact_reviews.sql
            └── schema.yml
```

**Key dbt Files to Create:**

**1. `dbt_project.yml`**
```yaml
name: 'keystone_nexus'
version: '1.0.0'
config-version: 2

profile: 'keystone_nexus_athena'

model-paths: ["models"]
analysis-paths: ["analyses"]
test-paths: ["tests"]
seed-paths: ["seeds"]
macro-paths: ["macros"]

models:
  keystone_nexus:
    staging:
      +materialized: view
      +schema: silver
    intermediate:
      +materialized: view
      +schema: silver
    marts:
      +materialized: table
      +schema: gold
```

**2. `packages.yml`**
```yaml
packages:
  - package: calogica/dbt_expectations
    version: [">=0.10.0", "<0.11.0"]
```

**3. `models/staging/schema.yml`** (with dbt-expectations)
```yaml
version: 2

models:
  - name: stg_orders
    description: "Staging layer for Olist orders"
    columns:
      - name: order_id
        description: "Primary key"
        tests:
          - not_null
          - unique
      
      - name: order_status
        tests:
          - accepted_values:
              values: ['created', 'approved', 'invoiced', 'processing',
                       'shipped', 'delivered', 'unavailable', 'canceled']
      
      - name: order_purchase_timestamp
        tests:
          - dbt_expectations.expect_column_values_to_be_between:
              min_value: "2016-01-01"
              max_value: "CURRENT_DATE"
```

**4. `models/marts/fact_sales.sql`**
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
    CAST(TO_CHAR(o.order_purchase_timestamp, 'YYYYMMDD') AS INT) AS date_key,
    oi.price,
    oi.freight_value,
    (oi.price + oi.freight_value) AS total_order_value,
    DATEDIFF(day, o.order_purchase_timestamp, o.order_delivered_customer_date) AS delivery_lag_days
FROM orders o
JOIN order_items oi ON o.order_id = oi.order_id
WHERE o.order_status = 'delivered'
```

---

### 4. **ELT Medallion Implementation**

**Adhere to Provided Structure:**

**Bronze Layer (Raw S3 Parquet):**
- Location: `s3://olist-data-lake-bronze/`
- Content: Raw CSV → Parquet conversion (1:1 copy)
- No transformations, no cleaning
- Schema validation only

**Silver Layer (Cleansed S3 Parquet):**
- Location: `s3://olist-data-lake-silver/`
- Content: Cleaned, validated, partitioned data
- **Great Expectations enforcement here** ← Jarvis handles this
- Partitioning: `year=YYYY/month=MM/day=DD`

**Gold Layer (Star Schema via Athena):**
- Location: `s3://olist-data-lake-gold/`
- Content: Business-ready dimension and fact tables
- Queryable via AWS Athena
- Optimized for BI dashboards

**Your Deliverable:** Document the flow in README.md with a diagram

---

### 5. **C++ gRPC Pipeline (Documented, Not Implemented)**

**From Architecture Docs:**
- High-speed ingestion via gRPC → Kafka
- Microsecond response time
- 5ms micro-batching

**Your Task:**
- **DO NOT implement** (focus on Python pipeline first)
- **Document** in `docs/ARCHITECTURE.md`:
  - Why C++ gRPC? (Performance justification)
  - When to use? (High-throughput streaming scenarios)
  - Trade-offs vs Python (complexity vs speed)
  - Future roadmap (Phase 2 optimization)

---

## 📌 Notes from Jarvis

**What Jarvis Has Completed:**
1. ✅ `init_olist_expectations.py` - Great Expectations suite (in `src/validation/`)
2. ✅ Data quality research document (18KB, in `docs/DATA_QUALITY_RESEARCH.md`)
3. ✅ Project structure setup (directories, .gitignore, requirements.txt)

**Redis Note:**
- Course module 2.2 covers Redis (key-value store)
- **Not needed for this project** (using S3 + Athena instead)
- Move any Redis materials to `~/knowledge/keystone-nexus/` if encountered
- Document in README.md under "Technology Decisions": Why we chose S3 over Redis

**Coordination:**
- Jarvis focuses on: Data quality validation + research
- Marvin focuses on: Code implementation + documentation + dbt
- Final integration: Merge both branches before presentation

---

## 🎓 Presentation Prep (Shared Responsibility)

**Marvin's Sections (Technical):**
1. Architecture deep-dive (3 minutes)
   - Medallion layers explained
   - Why dbt over raw SQL?
   - Cost optimization strategy (partitioning, serverless)

2. Live demo (if time permits)
   - Run `dbt run` → Show transformation
   - Run `dbt test` → Show validation passing
   - Query Gold layer via Athena → Show results

**Jarvis's Sections (Data Quality):**
1. Great Expectations overview (2 minutes)
   - Why data quality matters (business impact)
   - The 6 dimensions of data quality
   - Live Data Docs demonstration

2. Business value proposition (1 minute)
   - Prevented incidents: 12/year (48 hours saved)
   - ROI: 20:1 on data quality investment

---

## ✅ Checklist (Before Final Commit)

- [ ] All code reviewed for errors
- [ ] Function naming consistency verified
- [ ] Error handling added (try-catch, retries)
- [ ] README.md complete and professional
- [ ] dbt project structure created
- [ ] All dbt models tested (`dbt run`, `dbt test`)
- [ ] Architecture documented (diagram + rationale)
- [ ] Redis decision documented (why not used)
- [ ] Committed to GitHub (main branch)

---

## 🚨 Important Reminders

1. **No `~/` paths in documentation** - Use relative paths (`docs/`, `src/`)
2. **GROUP PROJECT** - This is collaborative, not individual work
3. **ELT Medallion** - Must follow Bronze → Silver → Gold structure
4. **C++ gRPC** - Document only, don't implement (scope management)
5. **Gemini's "woke" naming** - We had a laugh, but "Keystone Nexus" is locked in 😄

---

**Questions?** Coordinate via the group chat or update `MARVIN_TASKS.md` with blockers.

**Deadline:** Align on final deliverables before presentation rehearsal.

Good luck, Marvin! 🚀
