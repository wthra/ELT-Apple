from flask import Flask, jsonify
import duckdb
import os
import time

app = Flask(__name__)

# Database path
DB_PATH = "data/results/aapl_warehouse.db"

def get_db_connection():
    max_retries = 5
    retry_delay = 0.5
    
    for attempt in range(max_retries):
        try:
            # Connect in read-only mode to avoid locking issues
            con = duckdb.connect(DB_PATH, read_only=True)
            return con
        except Exception as e:
            if attempt < max_retries - 1:
                time.sleep(retry_delay)
                continue
            raise e

@app.route('/api/v1/stock_summary', methods=['GET'])
def get_stock_summary():
    """Get last 7 days of stock data."""
    try:
        con = get_db_connection()
        query = """
            SELECT date, close_price, volume 
            FROM aapl_analysis 
            ORDER BY date DESC 
            LIMIT 7
        """
        df = con.execute(query).df()
        # Convert Date to string for JSON serialization
        df['date'] = df['date'].astype(str)
        result = df.to_dict(orient='records')
        con.close()
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/v1/sentiment_vs_price', methods=['GET'])
def get_sentiment_vs_price():
    """Get joined data for correlation analysis."""
    try:
        con = get_db_connection()
        query = """
            SELECT date, close_price, daily_sentiment 
            FROM aapl_analysis 
            ORDER BY date
        """
        df = con.execute(query).df()
        df['date'] = df['date'].astype(str)
        result = df.to_dict(orient='records')
        con.close()
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
