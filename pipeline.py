import os
import time
from minio import Minio
from minio.error import S3Error
import pandas as pd
import duckdb
import pandera as pa
from pandera.typing import Series
from textblob import TextBlob
import io
import yfinance as yf

# Configuration
# Use 'minio' hostname if running in Docker (Airflow), else 'localhost'
MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT", "localhost:9000")
MINIO_ACCESS_KEY = os.getenv("MINIO_ACCESS_KEY", "minioadmin")
MINIO_SECRET_KEY = os.getenv("MINIO_SECRET_KEY", "minioadmin")
RAW_BUCKET = "raw-data"
PROCESSED_BUCKET = "processed-data"

def get_minio_client():
    return Minio(
        MINIO_ENDPOINT,
        access_key=MINIO_ACCESS_KEY,
        secret_key=MINIO_SECRET_KEY,
        secure=False
    )

def setup_infrastructure(client):
    """Create MinIO buckets if needed."""
    print("Setting up infrastructure...")
    for bucket in [RAW_BUCKET, PROCESSED_BUCKET]:
        if not client.bucket_exists(bucket):
            client.make_bucket(bucket)
            print(f"Created bucket: {bucket}")
        else:
            print(f"Bucket exists: {bucket}")

def upload_to_minio(client, file_path, bucket_name, object_name):
    """Helper to upload file to MinIO."""
    try:
        client.fput_object(bucket_name, object_name, file_path)
        print(f"Uploaded {file_path} to {bucket_name}/{object_name}")
    except S3Error as e:
        print(f"Error uploading {file_path}: {e}")

def extract_and_load(client):
    """Fetch data from Yahoo Finance and upload to MinIO."""
    print("\nStarting extraction...")
    
    # Fetch Stock Data
    print("Fetching AAPL data...")
    try:
        ticker = yf.Ticker("AAPL")
        # Fetch data from 2020 to present
        df_stock = ticker.history(start="2020-01-01")
        
        # Reset index to make Date a column and ensure standard format
        df_stock = df_stock.reset_index()
        df_stock['Date'] = df_stock['Date'].dt.date
        
        # Keep only necessary columns
        df_stock = df_stock[['Date', 'Close', 'Volume']]
        
        # Save to buffer
        csv_buffer = io.BytesIO()
        df_stock.to_csv(csv_buffer, index=False)
        csv_buffer.seek(0)
        
        # Upload to MinIO
        client.put_object(
            RAW_BUCKET, 
            "aapl_stock_prices.csv", 
            csv_buffer, 
            length=csv_buffer.getbuffer().nbytes,
            content_type="application/csv"
        )
        print(f"Uploaded live stock data to {RAW_BUCKET}/aapl_stock_prices.csv")
        
    except Exception as e:
        print(f"Error fetching stock data: {e}")

    # Upload News Data (using local CSV for now)
    local_news_file = "data/raw/aapl_news_full.csv"
    if os.path.exists(local_news_file):
        upload_to_minio(client, local_news_file, RAW_BUCKET, "aapl_news_full.csv")
    else:
        print(f"Warning: Local file {local_news_file} not found!")

def get_sentiment(text):
    if not isinstance(text, str):
        return 0.0
    return TextBlob(text).sentiment.polarity

def transform_sentiment(client):
    """Calculate sentiment scores from news headlines."""
    print("\nProcessing sentiment analysis...")
    
    # Read from MinIO
    try:
        obj = client.get_object(RAW_BUCKET, "aapl_news_full.csv")
        df = pd.read_csv(io.BytesIO(obj.read()))
    except Exception as e:
        print(f"Error reading news data: {e}")
        return

    # Calculate sentiment using 'headline' column
    print("Calculating sentiment scores...")
    df['sentiment_score'] = df['headline'].apply(get_sentiment)
    
    # Keep relevant columns and save
    result_df = df[['date', 'headline', 'sentiment_score']]
    
    # Save to buffer
    csv_buffer = io.BytesIO()
    result_df.to_csv(csv_buffer, index=False)
    csv_buffer.seek(0)
    
    # Upload to processed bucket
    try:
        client.put_object(
            PROCESSED_BUCKET, 
            "aapl_news_sentiment.csv", 
            csv_buffer, 
            length=csv_buffer.getbuffer().nbytes,
            content_type="application/csv"
        )
        print(f"Saved sentiment data to {PROCESSED_BUCKET}/aapl_news_sentiment.csv")
    except Exception as e:
        print(f"Error uploading processed data: {e}")

def transform_duckdb_join():
    """Join stock and sentiment data using DuckDB."""
    print("\nJoining data...")
    
    con = duckdb.connect()
    
    # Install and load httpfs extension for S3/MinIO support
    con.execute("INSTALL httpfs;")
    con.execute("LOAD httpfs;")
    
    # Configure S3/MinIO access
    con.execute(f"SET s3_endpoint='{MINIO_ENDPOINT}';")
    con.execute(f"SET s3_access_key_id='{MINIO_ACCESS_KEY}';")
    con.execute(f"SET s3_secret_access_key='{MINIO_SECRET_KEY}';")
    con.execute("SET s3_use_ssl=false;")
    con.execute("SET s3_url_style='path';")
    
    query = f"""
    WITH sentiment_daily AS (
        SELECT 
            CAST(date AS DATE) as date,
            AVG(sentiment_score) as daily_sentiment
        FROM read_csv_auto('s3://{PROCESSED_BUCKET}/aapl_news_sentiment.csv')
        GROUP BY 1
    ),
    stock_daily AS (
        SELECT 
            CAST(Date AS DATE) as date,
            CAST(Close AS DOUBLE) as close_price,
            CAST(Volume AS DOUBLE) as volume
        FROM read_csv_auto('s3://{RAW_BUCKET}/aapl_stock_prices.csv')
    )
    SELECT 
        s.date,
        s.close_price,
        s.volume,
        COALESCE(n.daily_sentiment, 0) as daily_sentiment
    FROM stock_daily s
    LEFT JOIN sentiment_daily n ON s.date = n.date
    ORDER BY s.date
    """
    
    try:
        result_df = con.execute(query).df()
        print(f"Joined data shape: {result_df.shape}")
        return result_df
    except Exception as e:
        print(f"Error in DuckDB query: {e}")
        return None

def validate_data(df):
    """Validate data quality with Pandera."""
    print("\nValidating data...")
    
    schema = pa.DataFrameSchema({
        "date": pa.Column(pa.DateTime),
        "close_price": pa.Column(float, checks=pa.Check.ge(0)),
        "volume": pa.Column(float, checks=pa.Check.ge(0)),
        "daily_sentiment": pa.Column(float, checks=pa.Check.in_range(-1.0, 1.0)),
    })
    
    try:
        validated_df = schema.validate(df)
        print("Data validation passed!")
        return validated_df
    except pa.errors.SchemaError as e:
        print(f"Data validation failed: {e}")
        return None

def load_to_warehouse(df):
    """Save results to DuckDB warehouse."""
    print("\nLoading to warehouse...")
    
    db_file = "data/results/aapl_warehouse.db"
    con = duckdb.connect(db_file)
    
    try:
        con.execute("CREATE OR REPLACE TABLE aapl_analysis AS SELECT * FROM df")
        print(f"Data saved to {db_file} table 'aapl_analysis'")
        
        # Verify
        count = con.execute("SELECT COUNT(*) FROM aapl_analysis").fetchone()[0]
        print(f"Total rows in warehouse: {count}")
        
    except Exception as e:
        print(f"Error saving to warehouse: {e}")
    finally:
        con.close()

def main():
    client = get_minio_client()
    
    # Run pipeline steps
    setup_infrastructure(client)
    extract_and_load(client)
    transform_sentiment(client)
    
    df = transform_duckdb_join()
    
    if df is not None:
        validated_df = validate_data(df)
        
        if validated_df is not None:
            load_to_warehouse(validated_df)

if __name__ == "__main__":
    main()
