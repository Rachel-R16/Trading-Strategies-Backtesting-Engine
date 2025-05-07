# backtest_engine.py
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go

# 1. Fetch historical data
def fetch_data(ticker, start, end):
    df = yf.download(ticker, start=start, end=end)
    if df.empty:
        print(f"Error: No data found for {ticker} between {start} and {end}")
        return pd.DataFrame()  # Return empty DataFrame if no data
    
    df = df[['Open', 'High', 'Low', 'Close', 'Volume']]
    df.dropna(inplace=True)
    return df

# 2. Define moving average crossover strategy
def ma_strategy(df, short_window=50, long_window=200):
    # Calculate moving averages
    df['MA_Short'] = df['Close'].rolling(short_window).mean()
    df['MA_Long'] = df['Close'].rolling(long_window).mean()

    # Initialize 'Signal' column to 0
    df['Signal'] = 0

    # Apply the strategy: Buy when short MA is above long MA, Sell when it's below
    df.loc[df['MA_Short'] > df['MA_Long'], 'Signal'] = 1
    df.loc[df['MA_Short'] < df['MA_Long'], 'Signal'] = -1

    # Ensure no NaN values in 'Signal' column before dropping rows
    if 'Signal' not in df.columns:
        print("Error: 'Signal' column is missing.")
    else:
        print(df['Signal'].head())  # Debugging: print the first few values of 'Signal'

    # Drop rows where 'Signal' is NaN (if any)
    df.dropna(subset=['Signal'], inplace=True)

    return df

# 3. Backtest logic
def backtest(df, initial_cash=10000):
    cash = initial_cash
    position = 0.0
    portfolio_values = []

    for i in range(1, len(df)):
        price = df['Close'].iloc[i]
        signal = df['Signal'].iloc[i]

        if pd.isna(signal):
            continue

        signal = int(signal)

        if signal == 1 and position == 0.0:
            position = cash / price
            cash = 0.0
        elif signal == -1 and position > 0.0:
            cash = position * price
            position = 0.0

        total_value = cash + position * price
        portfolio_values.append(total_value)

    if len(portfolio_values) == 0:
        print("Warning: No portfolio values generated!")
        return df  # Return early if no portfolio values are generated

    df = df.iloc[1:].copy()
    df['Portfolio Value'] = portfolio_values
    return df

# 4. Performance metrics
def performance(df):
    if df.empty or 'Portfolio Value' not in df.columns:
        return {'Total Return': 0, 'Sharpe Ratio': 0}
    
    total_return = df['Portfolio Value'].iloc[-1] / df['Portfolio Value'].iloc[0] - 1
    daily_returns = df['Portfolio Value'].pct_change().dropna()
    sharpe_ratio = daily_returns.mean() / daily_returns.std() * np.sqrt(252)
    return {
        'Total Return': total_return,
        'Sharpe Ratio': sharpe_ratio
    }

# 5. Plotting function
def plot(df):
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df.index, y=df['Close'], name='Close Price'))
    fig.add_trace(go.Scatter(x=df.index, y=df['Portfolio Value'], name='Portfolio Value'))
    fig.update_layout(title='Backtest Results', xaxis_title='Date', yaxis_title='Value')
    fig.show()

# 6. Main example
if __name__ == '__main__':
    df = fetch_data("AAPL", "2020-01-01", "2023-01-01")
    df = ma_strategy(df)
    df = backtest(df)
    print(performance(df))
    plot(df)
