# Keystone Nexus

![Build Status](https://img.shields.io/badge/build-passing-brightgreen)
![License](https://img.shields.io/badge/license-MIT-blue)
![dbt](https://img.shields.io/badge/dbt-1.7.0-orange)

## 📋 Project Overview
Keystone Nexus is a comprehensive data engineering project developed for the **NTU M2G6 Data Engineering** group project. The system implements a modern data lakehouse architecture using the **Medallion Architecture** (Bronze, Silver, Gold layers) to process and analyze the Brazilian E-Commerce dataset (Olist).

The project focuses on building a scalable, automated ELT pipeline that transforms raw transactional data into business-ready insights while ensuring high data quality through automated validation frameworks.

### Tech Stack
- **Infrastructure:** AWS S3, AWS Athena
- **Orchestration:** Apache Airflow
- **Transformation:** dbt (Data Build Tool)
- **Data Quality:** Great Expectations & `dbt-expectations`
- **Data Source:** Olist Brazilian E-Commerce (CSV/Parquet)

## 🏗️ Architecture

### Medallion Architecture Flow
1.  **Bronze (Raw):** 1:1 ingestion from CSV to Parquet on S3. No cleaning or transformation.
2.  **Silver (Cleansed):** Data is cleaned, typed, and partitioned. **Great Expectations** validates schema and business rules here.
3.  **Gold (Curated):** Star schema implementation (Fact and Dimension tables) optimized for BI and analytics.

### Data Flow Diagram
`Source CSV` ➔ `Airflow DAG` ➔ `S3 Bronze` ➔ `dbt Transformation (Silver)` ➔ `dbt Marts (Gold)` ➔ `Athena / BI`

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- AWS CLI (configured with appropriate IAM permissions)
- dbt Core (with Athena adapter)
- Apache Airflow

### Setup Instructions
1.  **Clone the Repository:**
    ```bash
    git clone https://github.com/robinlwong/keystone-nexus.git
    cd keystone-nexus
    ```
2.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
3.  **Initialize dbt:**
    ```bash
    cd dbt
    dbt deps
    ```

### Running the Pipeline
- **Ingestion:** Run the Airflow DAG or manual ingestion script:
    ```bash
    python src/ingestion/ingest_to_bronze.py
    ```
- **Transformations:** Execute the Medallion pipeline:
    ```bash
    dbt run
    ```
- **Validation:** Run data quality tests:
    ```bash
    dbt test
    ```

## 📊 Data Quality
Data quality is enforced at every layer:
- **Great Expectations:** Used for complex cross-column validation and generating Data Docs.
- **dbt-expectations:** Integrated directly into the dbt models for real-time schema and value constraints validation.

## 📁 Project Structure
- `dbt/`: dbt project configuration, models, and tests.
- `src/`: Ingestion and validation source code.
- `dags/`: Airflow DAG definitions for orchestration.
- `docs/`: Architectural documentation and design decisions.

## 🤝 Contributors
- **NTU M2G6 Team**

## 📄 License
This project is licensed under the MIT License.
