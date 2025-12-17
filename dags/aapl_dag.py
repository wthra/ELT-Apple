from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import sys
import os

# Add project root to path so we can import pipeline
sys.path.append('/opt/airflow/project')

try:
    import pipeline
except ImportError:
    # Fallback for local testing if not in container
    sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
    import pipeline

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

def run_extract_load():
    client = pipeline.get_minio_client()
    # Ensure buckets exist
    pipeline.setup_infrastructure(client)
    pipeline.extract_and_load(client)

def run_transform_sentiment():
    client = pipeline.get_minio_client()
    pipeline.transform_sentiment(client)

def run_join_validate():
    df = pipeline.transform_duckdb_join()
    if df is not None:
        validated_df = pipeline.validate_data(df)
        if validated_df is None:
            raise ValueError("Data validation failed")
        # Save validated data to warehouse
        pipeline.load_to_warehouse(validated_df)
    else:
        raise ValueError("Transformation failed")

with DAG(
    'aapl_elt_pipeline',
    default_args=default_args,
    description='ELT pipeline for AAPL stock and sentiment analysis',
    schedule_interval='0 1 * * *', # Run daily at 1 AM
    start_date=datetime(2023, 1, 1),
    catchup=False,
) as dag:

    t1 = PythonOperator(
        task_id='extract_load',
        python_callable=run_extract_load,
    )

    t2 = PythonOperator(
        task_id='transform_sentiment',
        python_callable=run_transform_sentiment,
    )

    t3 = PythonOperator(
        task_id='join_validate_load',
        python_callable=run_join_validate,
    )

    t1 >> t2 >> t3
