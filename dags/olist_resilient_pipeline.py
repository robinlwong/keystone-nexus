from airflow import DAG
from airflow.operators.python import PythonOperator, BranchPythonOperator
from airflow.providers.amazon.aws.hooks.s3 import S3Hook
from airflow.utils.trigger_rule import TriggerRule
from datetime import datetime, timedelta
import logging

# ==========================================
# 1. CONFIGURATION
# ==========================================
default_args = {
    'owner': 'marvin',
    'depends_on_past': False,
    'start_date': datetime(2026, 3, 3),
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

SILVER_BUCKET = "olist-data-lake-silver"
QUARANTINE_BUCKET = "olist-data-lake-quarantine"
GOLD_BUCKET = "olist-data-lake-gold"

# ==========================================
# 2. CUSTOM RESILIENCE LOGIC
# ==========================================
def validate_and_route(**kwargs):
    """
    Simulates Great Expectations (GX) validation logic.
    Returns the task_id to follow based on validation success.
    """
    ti = kwargs['ti']
    # In production, pull actual validation results from XCom (GX Operator)
    # For this implementation, we check if the Silver file exists and is valid
    s3_hook = S3Hook(aws_conn_id='aws_default')
    object_key = 'cleansed/orders/latest.parquet'
    
    validation_passed = s3_hook.check_for_key(object_key, SILVER_BUCKET)
    
    if validation_passed:
        logging.info(f"✅ Validation PASSED for {object_key}. Routing to Gold aggregation.")
        return 'aggregate_to_gold'
    else:
        logging.warning(f"❌ Validation FAILED for {object_key}. Routing to Quarantine.")
        return 'move_to_quarantine'

def quarantine_data(bucket_name, quarantine_bucket, object_key, **kwargs):
    """
    Moves corrupted or invalid Parquet files to a dedicated quarantine bucket.
    Prevents the Silver bucket from becoming cluttered with rejected data.
    """
    s3_hook = S3Hook(aws_conn_id='aws_default')
    new_key = f"rejected/{datetime.now().strftime('%Y-%m-%d')}/{object_key.split('/')[-1]}"
    
    logging.info(f"🚀 Moving corrupted data: {object_key} -> {quarantine_bucket}/{new_key}")
    
    s3_hook.copy_object(
        source_bucket_key=object_key,
        dest_bucket_key=new_key,
        source_bucket_name=bucket_name,
        dest_bucket_name=quarantine_bucket
    )
    
    # After copy, delete from Silver to keep it clean
    s3_hook.delete_objects(bucket_name, [object_key])
    logging.info("🧹 Silver bucket cleansed of rejected data.")

# ==========================================
# 3. DAG DEFINITION
# ==========================================
with DAG(
    'olist_resilient_silver_to_gold',
    default_args=default_args,
    description='Medallion pipeline with Dead Letter Quarantine path',
    schedule_interval='@daily',
    catchup=False,
    tags=['medallion', 'resilience', 'quarantine'],
) as dag:

    # 1. Validation Step (Conceptual GX Integration)
    validate_step = BranchPythonOperator(
        task_id='validate_and_route_data',
        python_callable=validate_and_route,
        provide_context=True,
    )

    # 2. Success Path: Move to Gold
    aggregate_gold = PythonOperator(
        task_id='aggregate_to_gold',
        python_callable=lambda: logging.info("🏆 Transforming Silver to Gold Star Schema..."),
    )

    # 3. Failure Path: Dead Letter Quarantine
    quarantine_step = PythonOperator(
        task_id='move_to_quarantine',
        python_callable=quarantine_data,
        op_kwargs={
            'bucket_name': SILVER_BUCKET,
            'quarantine_bucket': QUARANTINE_BUCKET,
            'object_key': 'cleansed/orders/latest.parquet'
        },
    )

    # 4. Final Notification (Runs regardless of which path was taken)
    pipeline_summary = PythonOperator(
        task_id='pipeline_summary',
        python_callable=lambda: logging.info("📋 Daily Medallion Run Complete."),
        trigger_rule=TriggerRule.ALL_DONE
    )

    # DAG Dependency Graph
    validate_step >> [aggregate_gold, quarantine_step]
    [aggregate_gold, quarantine_step] >> pipeline_summary
