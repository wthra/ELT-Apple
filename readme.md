# 📈 AAPL Stock & Sentiment Analysis: End-to-End ELT Pipeline

An automated **ELT (Extract, Load, Transform)** data pipeline ensuring data quality and serving analytics via API and Interactive Dashboard. This project correlates Apple Inc. (AAPL) stock prices with news sentiment using a modern Data Engineering stack.

![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![Apache Airflow](https://img.shields.io/badge/Apache%20Airflow-2.7-green)
![Docker](https://img.shields.io/badge/Docker-Compose-2496ED)
![MinIO](https://img.shields.io/badge/MinIO-Data%20Lake-c72c48)
![Streamlit](https://img.shields.io/badge/Streamlit-Dashboard-FF4B4B)

## 🏗 Architecture

The system follows a Local Data Stack architecture designed for reproducibility, security, and automation:

1.  **Orchestration:** **Apache Airflow** (Dockerized) schedules the workflow daily at 1 AM.
2.  **Data Lake:** **MinIO** (S3-compatible) stores raw CSVs and processed Parquet/CSV files.
3.  **Extraction:**
    *   **Stock Data:** Fetched real-time from **Yahoo Finance (`yfinance`)**.
    *   **News Data:** Ingested from local CSVs (simulating a news feed).
4.  **Transformation:**
    *   **Pandas & TextBlob:** For News Sentiment Analysis.
    *   **DuckDB:** For high-performance SQL joins and aggregations.
5.  **Validation:** **Pandera** enforces strict schema and data quality checks.
6.  **Serving:**
    *   **Flask API:** Provides JSON endpoints with retry logic for robustness.
    *   **Streamlit Dashboard:** Interactive frontend for data visualization.

## 📂 Project Structure

```bash
├── dags/
│   ├── aapl_dag.py          # Airflow DAG definition
│   └── pipeline.py          # Core ELT logic (Extract, Transform, Load)
├── data/
│   ├── raw/                 # Raw input files (News CSV)
│   ├── processed/           # Intermediate files (Sentiment CSV)
│   └── results/             # Final Warehouse (DuckDB) & Reports
├── docker-compose.yaml      # Infrastructure setup (Airflow + MinIO + Postgres)
├── Dockerfile.airflow       # Custom Airflow image with dependencies
├── requirements.txt         # Python dependencies
├── .env                     # Environment variables (Secrets)
├── api.py                   # Flask API for data consumption
├── dashboard.py             # Streamlit Interactive Dashboard
├── visualization.py         # Static graph generator
└── README.md                # Project documentation
```

## 🚀 Getting Started

### Prerequisites
*   Docker & Docker Compose
*   Python 3.8+

### Installation

1.  **Clone the repository**
    ```bash
    git clone <repository-url>
    cd <repository-folder>
    ```

2.  **Install Local Dependencies** (for Dashboard/API)
    ```bash
    pip install -r requirements.txt
    ```

3.  **Configure Environment**
    Ensure the `.env` file exists with MinIO credentials (default provided for local dev).

## ▶️ Usage

### 1. Start Infrastructure
Launch Airflow and MinIO containers. This will build the custom image with `yfinance` support.
```bash
docker-compose up -d --build
```

### 2. Run the Pipeline (Airflow)
1.  Open Airflow UI: [http://localhost:8080](http://localhost:8080) (User/Pass: `admin`/`admin`)
2.  Find DAG `aapl_elt_pipeline`.
3.  Toggle the **Unpause** switch (ON).
4.  The pipeline runs automatically at **01:00 AM** daily, or you can trigger it manually.

### 3. Interactive Dashboard (Streamlit) **[NEW]**
Launch the dashboard to visualize live data and control the pipeline.
```bash
streamlit run dashboard.py
```
*   **Features:**
    *   Real-time Stock Price vs. Sentiment Graph.
    *   **"Run Pipeline" Button:** Trigger a fresh data fetch and update immediately.
    *   Date Range Filters & Correlation Metrics.

### 4. Access Data (Flask API)
Start the API server to serve the processed data via JSON.
```bash
python api.py
```
*   **Stock Summary**: [http://localhost:5000/api/v1/stock_summary](http://localhost:5000/api/v1/stock_summary)
*   **Correlation Data**: [http://localhost:5000/api/v1/sentiment_vs_price](http://localhost:5000/api/v1/sentiment_vs_price)

## 📊 Results

*   **Live Data**: The system now fetches stock prices up to the current date.
*   **Correlation**: Automatically calculated based on the selected date range in the dashboard.
*   **Data Quality**: Validated by Pandera (checks for negative prices, invalid dates, etc.).