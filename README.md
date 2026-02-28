# Keystone Nexus

![Build Status](https://img.shields.io/badge/build-passing-brightgreen)
![License](https://img.shields.io/badge/license-MIT-blue)
![dbt](https://img.shields.io/badge/dbt-1.7.0-orange)
![AWS MSK](https://img.shields.io/badge/AWS-MSK-red)

## 📋 Project Overview
Keystone Nexus is a comprehensive data engineering project developed for the **NTU M2G6 Data Engineering** group project. The system implements a modern data lakehouse architecture using the **Medallion Architecture** (Bronze, Silver, Gold layers) to process and analyze the Brazilian E-Commerce dataset (Olist).

Recently, the project pivoted from a batch-centric model to a **real-time streaming architecture** leveraging **AWS MSK**.

### Tech Stack
- **Infrastructure:** AWS S3, AWS Athena, **AWS MSK (Kafka)**
- **Orchestration:** Apache Airflow
- **Transformation:** dbt (Data Build Tool)
- **Data Quality:** Great Expectations & `dbt-expectations`
- **Data Source:** Olist Brazilian E-Commerce (CSV/Parquet/Streams)

## 🏗️ Architecture

### Medallion Architecture Flow
1.  **Bronze (Raw):** 1:1 ingestion via **AWS MSK Connect** (Stream) or Python Ingestion (Batch) to S3.
2.  **Silver (Cleansed):** Cleaned, typed, and partitioned data. **Great Expectations** validates rules here.
3.  **Gold (Curated):** Star schema implementation (Fact and Dimension tables) optimized for BI.

### Data Flow Diagram
`Producer` ➔ `AWS MSK` ➔ `MSK Connect` ➔ `S3 Bronze` ➔ `dbt Transformation` ➔ `Athena / BI`

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- AWS CLI
- dbt Core (Athena adapter)
- Kafka Python client (`pip install kafka-python`)

### Setup Instructions
1.  **Clone the Repository:**
    ```bash
    git clone https://github.com/robinlwong/keystone-nexus.git
    cd keystone-nexus
    ```
2.  **Initialize dbt:**
    ```bash
    cd dbt && dbt deps
    ```

### Running the Pipeline
- **Streaming:** Start the MSK producer:
    ```bash
    python src/streaming/msk_producer.py
    ```
- **Ingestion (Batch):** 
    ```bash
    python src/ingestion/ingest_to_bronze.py
    ```
- **Transformations:** 
    ```bash
    dbt run
    ```

## 📊 Data Quality
Data quality is enforced via **Great Expectations** for complex validation and **dbt-expectations** for model-level constraints.

## 📁 Project Structure
- `dbt/`: dbt project configuration and models.
- `src/`: Ingestion, **streaming producers**, and validation code.
- `infra/`: **AWS MSK cluster configurations**.
- `docs/`: Architecture docs, including the **MSK Pivot strategy**.

## 🤝 Contributors
- **NTU M2G6 Team**
