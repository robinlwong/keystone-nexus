# Keystone Nexus - Implementation Plan

**Project:** NTU M2G6 Module 2 Assignment  
**Dataset:** Brazilian E-Commerce (Olist)  
**Target:** End-to-end data pipeline with AWS deployment  
**Status:** Planning Phase

---

## Executive Summary

Keystone Nexus implements a scalable, enterprise-grade data lakehouse for Olist e-commerce analytics. The architecture combines high-performance C++ ingestion, Python-based ETL, serverless analytics, and automated data quality checks.

**Key Differentiators:**
- **Low-latency ingestion:** C++ gRPC → Kafka (microsecond response)
- **Cost-optimized storage:** S3 Parquet with year/month/day partitioning
- **Serverless analytics:** AWS Athena (pay-per-query, no cluster overhead)
- **Data quality gates:** Great Expectations with Athena execution engine
- **Resilient pipelines:** Dead letter quarantine for corrupted data

---

## Project Requirements Mapping

### 1. Data Ingestion ✅
**Requirement:** Ingest Olist CSV files into database/warehouse  
**Implementation:**
- **Source:** Brazilian E-Commerce Dataset by Olist (9 CSV files)
- **Ingestion Path:** 
  - Option A (Simple): Python script → Direct S3 upload → Bronze layer
  - Option B (Enterprise): C++ gRPC Server → Kafka → Python workers → S3 Parquet
- **Technology:** pandas, pyarrow, boto3
- **Target:** S3 Bronze bucket (`s3://olist-data-lake-bronze/`)

### 2. Data Warehouse Design ✅
**Requirement:** Star schema with dimension and fact tables  
**Implementation:**
- **Schema Type:** Medallion Architecture (Bronze → Silver → Gold)
  - **Bronze:** Raw ingested data (Parquet)
  - **Silver:** Cleansed, validated data (Parquet with partitions)
  - **Gold:** Business-ready aggregations (Parquet, queryable via Athena)

**Star Schema (Gold Layer):**
```
Dimension Tables:
- DimCustomer (customer_id, state, city, zip_code)
- DimProduct (product_id, category_name)
- DimSeller (seller_id, seller_state, seller_city)
- DimDate (date_id, year, quarter, month, day, day_of_week)

Fact Tables:
- FactSales (order_id, customer_id, product_id, seller_id, date_id,
             order_status, payment_value, freight_value, delivery_days)
- FactReviews (review_id, order_id, review_score, review_date)
```

**Technology:** AWS Glue Catalog, Athena DDL

### 3. ELT Pipeline ✅
**Requirement:** Transform raw data into star schema using dbt or alternatives  
**Implementation:**
- **Tool:** dbt (Data Build Tool) on AWS EC2 or local development
- **Alternative:** PySpark transformations orchestrated by Airflow
- **Data Cleaning:**
  - Remove duplicates
  - Handle null values (forward fill, default values)
  - Standardize timestamps (UTC)
  - Validate foreign keys
- **Derived Columns:**
  - `delivery_days` = `order_delivered_customer_date` - `order_purchase_timestamp`
  - `customer_lifetime_value` = SUM(payment_value) GROUP BY customer_id
  - `product_review_avg` = AVG(review_score) GROUP BY product_id

**Technology:** dbt, Apache Spark (PySpark), Airflow

### 4. Data Quality Testing ✅
**Requirement:** Validate data quality using Great Expectations or SQL  
**Implementation:**
- **Tool:** Great Expectations 0.18+ with Athena execution engine
- **Test Suite:**
  - **Null value checks:** customer_id, order_id, payment_value NOT NULL
  - **Duplicate detection:** UNIQUE constraint on order_id
  - **Referential integrity:** order_items.order_id EXISTS IN orders.order_id
  - **Business logic:** 
    - `delivery_date` > `purchase_date`
    - `payment_value` >= 0
    - `review_score` BETWEEN 1 AND 5
    - `freight_value` >= 0
  - **Schema validation:** Column types match expected schema

**Technology:** Great Expectations, AWS Athena, custom SQL checks

### 5. Data Analysis with Python ✅
**Requirement:** Connect to warehouse, perform EDA, calculate metrics  
**Implementation:**
- **Connection:** SQLAlchemy + PyAthena
- **Analysis Framework:** pandas, matplotlib, seaborn
- **Key Metrics:**
  1. **Monthly Sales Trends:**
     - Total revenue by month (2016-2018)
     - Order count by month
     - Average order value trend
  2. **Top-Selling Products:**
     - Top 20 products by revenue
     - Top categories by order volume
     - Product review correlation with sales
  3. **Customer Segmentation:**
     - RFM Analysis (Recency, Frequency, Monetary)
     - Geographic distribution (state-level heatmap)
     - High-value vs low-value customer cohorts

**Deliverables:**
- Jupyter notebooks (`analysis/exploratory_analysis.ipynb`)
- Executive-friendly visualizations (charts, KPI dashboards)

**Technology:** pandas, SQLAlchemy, PyAthena, matplotlib, seaborn

### 6. Pipeline Orchestration ✅
**Requirement:** Schedule regular ELT runs and data quality checks  
**Implementation:**
- **Tool:** Apache Airflow (Amazon MWAA or EC2-based)
- **DAGs:**
  1. `olist_daily_ingestion_dag` - Ingest new data (if streaming)
  2. `olist_silver_to_gold_dag` - Transform Silver → Gold
  3. `olist_data_quality_dag` - Run Great Expectations checks
  4. `olist_analytics_refresh_dag` - Update KPI materialized views
- **Schedule:** Daily at 2:00 AM UTC
- **Monitoring:** CloudWatch Logs, SNS alerts on failure

**Alternative (if Airflow is complex):** GitHub Actions CICD for scheduled runs

**Technology:** Apache Airflow, Amazon MWAA, GitHub Actions (optional)

### 7. Documentation ✅
**Requirement:** Code docs, data lineage, architecture diagrams, technical report  
**Implementation:**
- **Architecture Diagram:** Draw.io or Excalidraw
  - Data flow (Source → Bronze → Silver → Gold → Analytics)
  - AWS service interaction diagram
  - Star schema ERD
- **Data Lineage:** dbt docs (automatically generated)
- **Technical Report:** Markdown document covering:
  - Tool selection rationale (why Athena over Redshift)
  - Schema design justification (partitioning strategy)
  - Cost optimization decisions
  - Scalability considerations
- **Code Documentation:** Docstrings, inline comments, README

**Deliverables:**
- `docs/architecture_diagram.png`
- `docs/technical_report.md`
- `docs/schema_design_rationale.md`
- dbt docs site (auto-generated)

### 8. Executive Stakeholder Presentation ✅
**Requirement:** 10-minute presentation + 5-minute Q&A for mixed audience  
**Implementation:**
- **Slide Deck Structure:**
  1. Executive Summary (2 min) - Problem, solution, business impact
  2. Business Value (2 min) - Cost savings, efficiency gains, strategic insights
  3. Technical Solution (3 min) - Architecture overview, key decisions
  4. Key Findings (2 min) - Top 3 insights from data analysis
  5. Recommendations (1 min) - Actionable business decisions
  6. Risk & Mitigation (Optional, if time)
  7. Q&A (5 min)

**Visuals:**
- Executive-friendly charts (bar, line, pie charts)
- AWS architecture diagram (high-level, not overly technical)
- KPI dashboard mockup
- ROI/cost comparison (Athena vs Redshift)

**Technology:** Google Slides, PowerPoint, or Canva

---

## Technical Stack

### Data Storage & Lakehouse
- **S3:** Bronze, Silver, Gold buckets
- **Format:** Parquet (Snappy compression)
- **Partitioning:** year/month/day for cost optimization
- **Catalog:** AWS Glue Data Catalog

### Compute & Processing
- **Ingestion:** Python (pandas, pyarrow) or C++ (gRPC, Kafka)
- **Transformation:** dbt, PySpark, or pandas
- **Query Engine:** AWS Athena (serverless SQL)
- **Analytics:** Python (pandas, SQLAlchemy, matplotlib)

### Orchestration & Quality
- **Workflow:** Apache Airflow (Amazon MWAA preferred)
- **Data Quality:** Great Expectations
- **Monitoring:** CloudWatch, SNS alerts

### Infrastructure (AWS)
- **EC2:** Ubuntu 24.04 LTS (for Airflow, Python workers)
- **RDS:** PostgreSQL (for Airflow metadata, operational state)
- **MSK:** Managed Kafka (if using streaming ingestion)
- **IAM:** Roles and policies for service-to-service auth
- **VPC:** Private subnets for security

### Development Tools
- **Package Manager:** pnpm (for Node.js/TypeScript dashboards)
- **Version Control:** Git, GitHub
- **Python Env:** venv or conda
- **CI/CD:** GitHub Actions (optional)

---

## Implementation Phases

### Phase 1: Foundation (Week 1)
**Goal:** Setup AWS infrastructure and ingest raw data

**Tasks:**
1. ✅ Create GitHub repository (`keystone-nexus`)
2. ✅ Setup AWS account and IAM roles
3. ✅ Create S3 buckets (bronze, silver, gold, quarantine)
4. ⏳ Download Olist dataset (9 CSV files)
5. ⏳ Write Python ingestion script (`src/ingestion/ingest_to_bronze.py`)
6. ⏳ Upload CSV → Parquet to Bronze bucket
7. ⏳ Setup AWS Glue Catalog and Athena database

**Deliverables:**
- S3 bucket structure
- Bronze layer populated with Parquet files
- Athena database schema

### Phase 2: Data Warehouse Design (Week 1-2)
**Goal:** Transform Bronze → Silver → Gold with star schema

**Tasks:**
1. ⏳ Design star schema (dimension and fact tables)
2. ⏳ Write dbt models or PySpark transformations
3. ⏳ Implement data cleaning logic
4. ⏳ Create derived columns (delivery_days, customer_lifetime_value)
5. ⏳ Partition Gold tables by date
6. ⏳ Test queries in Athena

**Deliverables:**
- dbt project structure (`models/silver/`, `models/gold/`)
- Star schema implemented in Athena
- Documentation (`docs/schema_design_rationale.md`)

### Phase 3: Data Quality & Orchestration (Week 2)
**Goal:** Implement automated validation and pipeline scheduling

**Tasks:**
1. ⏳ Setup Great Expectations project
2. ⏳ Configure Athena execution engine
3. ⏳ Write data quality test suites
4. ⏳ Setup Apache Airflow (EC2 or MWAA)
5. ⏳ Create DAGs for ingestion, transformation, validation
6. ⏳ Implement quarantine routing logic
7. ⏳ Setup CloudWatch alarms and SNS notifications

**Deliverables:**
- Great Expectations checkpoint YAML files
- Airflow DAGs (`dags/olist_resilient_pipeline.py`)
- Monitoring dashboards

### Phase 4: Analytics & Insights (Week 3)
**Goal:** Perform EDA and generate business insights

**Tasks:**
1. ⏳ Setup Jupyter notebook environment
2. ⏳ Connect to Athena via SQLAlchemy
3. ⏳ Calculate monthly sales trends
4. ⏳ Identify top-selling products and categories
5. ⏳ Perform customer segmentation (RFM analysis)
6. ⏳ Create visualizations (charts, heatmaps)
7. ⏳ Document findings in notebook

**Deliverables:**
- `analysis/exploratory_analysis.ipynb`
- `analysis/key_insights.md`
- Executive-ready charts (saved as PNG/SVG)

### Phase 5: Documentation & Presentation (Week 3-4)
**Goal:** Prepare final deliverables and presentation

**Tasks:**
1. ⏳ Create architecture diagram (Draw.io)
2. ⏳ Write technical report (tool selection, schema design)
3. ⏳ Generate dbt docs site
4. ⏳ Create executive slide deck
5. ⏳ Rehearse presentation (10 min + 5 min Q&A)
6. ⏳ Push all code to GitHub (single main branch)

**Deliverables:**
- `docs/architecture_diagram.png`
- `docs/technical_report.md`
- `presentation/keystone_nexus_executive_summary.pptx`
- GitHub repository (all code, docs, notebooks)

---

## AWS Architecture

### High-Level Diagram

```
┌─────────────────┐
│  Olist Dataset  │ (CSV files)
│   (9 tables)    │
└────────┬────────┘
         │ Ingestion Script (Python)
         ▼
┌─────────────────────────────────────┐
│  S3 Bronze Bucket                   │
│  (Raw Parquet files)                │
└────────┬────────────────────────────┘
         │ dbt / PySpark Transformation
         ▼
┌─────────────────────────────────────┐
│  S3 Silver Bucket                   │
│  (Cleansed, partitioned Parquet)    │
│  year=YYYY/month=MM/day=DD          │
└────────┬────────────────────────────┘
         │ Great Expectations Validation
         ├────► ✅ PASS → Gold Layer
         └────► ❌ FAIL → Quarantine Bucket
         │
         ▼
┌─────────────────────────────────────┐
│  S3 Gold Bucket                     │
│  (Star Schema: Dim/Fact tables)     │
│  - DimCustomer, DimProduct          │
│  - FactSales, FactReviews           │
└────────┬────────────────────────────┘
         │ AWS Athena Queries
         ▼
┌─────────────────────────────────────┐
│  Python Analytics                   │
│  (Jupyter Notebooks)                │
│  - Monthly trends                   │
│  - Top products                     │
│  - Customer segmentation            │
└─────────────────────────────────────┘
```

### AWS Services Used

| Service | Purpose | Cost Estimate (Monthly) |
|---|---|---|
| **S3** | Data lake storage (Bronze/Silver/Gold) | $5-20 (100 GB @ $0.023/GB) |
| **Athena** | Serverless SQL queries | $5-50 ($5 per TB scanned) |
| **Glue** | Data catalog (schema metadata) | Free tier (1M objects) |
| **EC2** | Airflow server (t3.medium) | $30-50 (if using self-hosted) |
| **MWAA** | Managed Airflow (alternative to EC2) | $350+ (enterprise option) |
| **RDS** | PostgreSQL (Airflow metadata) | $15-30 (db.t3.micro) |
| **CloudWatch** | Logs and alarms | $5-10 |
| **SNS** | Alert notifications | <$1 |
| **Total (Self-hosted Airflow)** | | **~$60-160/month** |
| **Total (Managed MWAA)** | | **~$400-500/month** |

**Recommendation:** Start with self-hosted Airflow on EC2 for cost efficiency during development.

---

## Risk Assessment & Mitigation

### Risk 1: Schema Drift
**Description:** Olist dataset structure changes (new columns, renamed fields)  
**Impact:** Pipeline breaks, Athena queries fail  
**Mitigation:**
- AWS Glue Schema Registry integration
- Great Expectations schema validation tests
- Version control for dbt models

### Risk 2: Cost Overruns (Athena)
**Description:** Unoptimized queries scan entire dataset repeatedly  
**Impact:** $100s in Athena charges  
**Mitigation:**
- Mandatory partitioning (year/month/day)
- LIMIT clauses in exploratory queries
- CloudWatch budget alerts ($50 threshold)

### Risk 3: Data Quality Issues
**Description:** Missing values, duplicates, illogical timestamps  
**Impact:** Incorrect business insights, flawed KPIs  
**Mitigation:**
- Great Expectations validation gates
- Quarantine bucket for corrupted data
- Airflow alerts on validation failures

### Risk 4: Scalability Bottlenecks
**Description:** Single EC2 instance can't handle large data volumes  
**Impact:** Slow transformations, pipeline delays  
**Mitigation:**
- AWS Auto Scaling Groups (if traffic spikes)
- PySpark for distributed processing
- Serverless Athena for analytics (auto-scales)

### Risk 5: Knowledge Gap (Airflow/dbt)
**Description:** Team unfamiliar with Airflow orchestration  
**Impact:** Development delays, debugging challenges  
**Mitigation:**
- Start with simple DAGs (file sensor → Python operator)
- Use managed MWAA for production (reduce ops burden)
- Fallback: GitHub Actions for scheduled scripts

---

## Success Criteria

### Technical Metrics
- ✅ Data ingestion completes without errors (100% success rate)
- ✅ All Great Expectations tests pass (zero data quality failures)
- ✅ Athena queries return results in <5 seconds (90th percentile)
- ✅ Pipeline runs daily without manual intervention (automation)
- ✅ Cost stays within $100/month budget (AWS spend)

### Business Metrics
- ✅ Identify top 3 revenue-driving product categories
- ✅ Calculate customer lifetime value for segmentation
- ✅ Generate monthly sales trend report
- ✅ Provide actionable recommendations to executives

### Deliverable Checklist
- ✅ GitHub repository with all code (main branch)
- ✅ Jupyter notebooks with EDA and visualizations
- ✅ Technical documentation (architecture, schema design)
- ✅ Executive slide deck (10 min presentation)
- ✅ Q&A preparation (anticipated questions documented)

---

## Next Steps

**Immediate Actions:**
1. ⏳ Download Olist dataset (Kaggle)
2. ⏳ Setup AWS account (if not already configured)
3. ⏳ Create S3 buckets and IAM roles
4. ⏳ Write Python ingestion script (CSV → Parquet → Bronze)
5. ⏳ Test Athena query on Bronze data

**This Week:**
- Complete Phase 1 (Foundation)
- Start Phase 2 (Data Warehouse Design)

**Questions to Resolve:**
- Use self-hosted Airflow (EC2) or managed MWAA?
- Implement C++ gRPC layer or stick with Python ingestion?
- dbt vs PySpark for transformations?

---

**Status:** Ready to begin implementation  
**Last Updated:** 2026-02-27  
**Owner:** Jarvis (OpenClaw Agent) + Robin Wong
