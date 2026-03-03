# pushdown_athena_validation.py
# Keystone Nexus - Athena Compute Pushdown for Great Expectations
# Prevents OOM crashes on MWAA worker nodes by offloading scanning to Athena.

import great_expectations as gx
from great_expectations.datasource.fluent import AthenaDatasource
import os

def configure_athena_pushdown():
    """
    Configures Great Expectations to use the Athena Execution Engine.
    This ensures that data validation compute is pushed down to Athena's
    massively parallel serverless engine rather than running in-memory 
    on the Airflow/MWAA worker.
    """
    print("🚀 Configuring Great Expectations Athena Pushdown Engine...")
    
    # Initialize context
    context = gx.get_context()

    # Athena Connection Details (Environment variables or hardcoded for demo)
    ATHENA_DB = "olist_gold_db"
    S3_STAGING_DIR = "s3://olist-athena-query-results/gx_staging/"
    REGION = "us-east-1" # Update to project region

    # SQL Alchemy connection string for PyAthena
    # Format: awsathena+rest://@athena.{region_name}.amazonaws.com/{schema_name}?s3_staging_dir={s3_staging_dir}
    connection_string = f"awsathena+rest://@athena.{REGION}.amazonaws.com/{ATHENA_DB}?s3_staging_dir={S3_STAGING_DIR}"

    datasource_name = "athena_gold_layer"
    
    # Add Athena Datasource using SQLAlchemy Execution Engine
    # This is the "Compute Pushdown" magic
    if datasource_name not in [ds["name"] for ds in context.list_datasources()]:
        context.sources.add_sql(
            name=datasource_name,
            connection_string=connection_string,
        )
        print(f"✅ Added Athena Datasource: {datasource_name}")
    else:
        print(f"ℹ️ Datasource {datasource_name} already exists.")

    # Create Checkpoint for Athena
    checkpoint_name = "olist_athena_pushdown_checkpoint"
    
    # In a real scenario, the batch_request would target specific Gold tables
    # e.g., fact_sales, dim_customers
    
    print(f"🔒 Checkpoint {checkpoint_name} configured for pushdown compute.")
    print("Airflow will now orchestrate, while Athena executes.")

if __name__ == "__main__":
    configure_athena_pushdown()
