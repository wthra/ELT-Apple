import streamlit as st
import duckdb
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os
import pipeline

# Page Config
st.set_page_config(
    page_title="AAPL Sentiment & Stock Dashboard",
    page_icon="📈",
    layout="wide"
)

# Database
DB_PATH = "data/results/aapl_warehouse.db"

@st.cache_data(ttl=600)
def load_data():
    if not os.path.exists(DB_PATH):
        return None
    
    try:
        con = duckdb.connect(DB_PATH, read_only=True)
        query = """
            SELECT 
                date, 
                close_price, 
                volume, 
                daily_sentiment 
            FROM aapl_analysis 
            ORDER BY date
        """
        df = con.execute(query).df()
        con.close()
        return df
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return None

# Main App
def main():
    st.title("🍎 AAPL Stock Price vs. News Sentiment")
    st.markdown("Analyze how news sentiment correlates with Apple Inc. stock performance.")

    # Sidebar Actions
    st.sidebar.header("Actions")
    if st.sidebar.button("🔄 Run Pipeline & Refresh Data"):
        with st.spinner("Running ELT Pipeline... (This may take a moment)"):
            try:
                # Run the full pipeline
                pipeline.main()
                # Clear cache to force reload
                load_data.clear()
                st.success("Pipeline finished successfully! Reloading data...")
                st.rerun()
            except Exception as e:
                st.error(f"Pipeline failed: {e}")

    df = load_data()

    if df is None:
        st.warning("Data not found. Please run the pipeline first.")
        return

    # Sidebar Filters
    st.sidebar.header("Filters")
    min_date = df['date'].min()
    max_date = df['date'].max()
    
    start_date, end_date = st.sidebar.date_input(
        "Date Range",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date
    )

    # Filter Data
    mask = (df['date'] >= pd.to_datetime(start_date)) & (df['date'] <= pd.to_datetime(end_date))
    filtered_df = df.loc[mask]

    # Key Metrics
    col1, col2, col3, col4 = st.columns(4)
    
    latest_data = filtered_df.iloc[-1] if not filtered_df.empty else None
    
    if latest_data is not None:
        col1.metric("Latest Close Price", f"${latest_data['close_price']:.2f}")
        col2.metric("Latest Volume", f"{latest_data['volume']:,.0f}")
        col3.metric("Avg Sentiment (Selected)", f"{filtered_df['daily_sentiment'].mean():.4f}")
        
        correlation = filtered_df['close_price'].corr(filtered_df['daily_sentiment'])
        col4.metric("Correlation (Price vs Sentiment)", f"{correlation:.4f}")

    # Charts
    st.subheader("Price vs. Sentiment Over Time")
    
    # Dual Axis Chart
    fig = go.Figure()

    # Stock Price Line
    fig.add_trace(go.Scatter(
        x=filtered_df['date'], 
        y=filtered_df['close_price'],
        name="Stock Price ($)",
        mode='lines',
        line=dict(color='#007AFF', width=2)
    ))

    # Sentiment Bar (Secondary Axis)
    fig.add_trace(go.Bar(
        x=filtered_df['date'], 
        y=filtered_df['daily_sentiment'],
        name="Sentiment Score",
        yaxis='y2',
        marker_color=filtered_df['daily_sentiment'].apply(lambda x: '#34C759' if x >= 0 else '#FF3B30'),
        opacity=0.5
    ))

    # Layout
    fig.update_layout(
        xaxis_title="Date",
        yaxis=dict(title="Stock Price ($)", side="left"),
        yaxis2=dict(title="Sentiment Score", side="right", overlaying="y", range=[-1, 1]),
        hovermode="x unified",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )

    st.plotly_chart(fig, use_container_width=True)

    # Volume Chart
    st.subheader("Trading Volume")
    fig_vol = px.bar(filtered_df, x='date', y='volume', color_discrete_sequence=['#5856D6'])
    st.plotly_chart(fig_vol, use_container_width=True)

    # Raw Data
    with st.expander("View Raw Data"):
        st.dataframe(filtered_df.sort_values(by='date', ascending=False))

if __name__ == "__main__":
    main()
