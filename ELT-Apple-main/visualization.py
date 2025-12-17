import duckdb
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Connect to DB
con = duckdb.connect("data/results/aapl_warehouse.db", read_only=True)

# Query data
query = """
    SELECT 
        date, 
        close_price, 
        daily_sentiment
    FROM aapl_analysis 
    ORDER BY date
"""
df = con.execute(query).df()
con.close()

# Convert date to datetime
df['date'] = pd.to_datetime(df['date'])

# Plotting
plt.figure(figsize=(14, 7))
sns.set_style("whitegrid")

# Plot Stock Price
ax1 = plt.gca()
sns.lineplot(data=df, x='date', y='close_price', ax=ax1, color='blue', label='Stock Price')
ax1.set_ylabel('Stock Price (USD)', color='blue')
ax1.tick_params(axis='y', labelcolor='blue')

# Plot Sentiment
ax2 = ax1.twinx()
sns.lineplot(data=df, x='date', y='daily_sentiment', ax=ax2, color='orange', alpha=0.6, label='Sentiment Score')
ax2.set_ylabel('Daily Sentiment Score', color='orange')
ax2.tick_params(axis='y', labelcolor='orange')
ax2.set_ylim(-1, 1)  # Sentiment range

# Title and Layout
plt.title('AAPL Stock Price vs. News Sentiment', fontsize=16)
plt.tight_layout()

# Save plot
plt.savefig('data/results/aapl_sentiment_analysis.png')
print("Visualization saved as 'data/results/aapl_sentiment_analysis.png'")

# Calculate Correlation
correlation = df['close_price'].corr(df['daily_sentiment'])
print(f"Correlation between Stock Price and Sentiment: {correlation:.4f}")
