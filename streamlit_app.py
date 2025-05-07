# streamlit_app.py
import streamlit as st
import pandas as pd
from backtesting import fetch_data, ma_strategy, backtest, performance, plot

st.title("📈 Backtesting Engine for Trading Strategies")

# User inputs
ticker = st.text_input("Enter Ticker", "AAPL")
start_date = st.date_input("Start Date", value=pd.to_datetime("2020-01-01"))
end_date = st.date_input("End Date", value=pd.to_datetime("2023-01-01"))
short_ma = st.number_input("Short Moving Average (e.g., 50)", value=50)
long_ma = st.number_input("Long Moving Average (e.g., 200)", value=200)
initial_cash = st.number_input("Initial Cash", value=10000)

# Run backtest
if st.button("Run Backtest"):
    df = fetch_data(ticker, str(start_date), str(end_date))
    df = ma_strategy(df, short_window=short_ma, long_window=long_ma)
    df = backtest(df, initial_cash=initial_cash)
    metrics = performance(df)

    st.subheader("Performance Metrics")
    st.write(f"**Total Return**: {metrics['Total Return']:.2%}")
    st.write(f"**Sharpe Ratio**: {metrics['Sharpe Ratio']:.2f}")
    
    st.subheader("Strategy Visualization")
    plot(df)  # Plotly chart opens in a new tab or pane
