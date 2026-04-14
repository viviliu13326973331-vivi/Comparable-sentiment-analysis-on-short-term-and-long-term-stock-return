# -*- coding: utf-8 -*-


import requests
import pandas as pd
from datetime import datetime
import time

# Function to fetch data for a given symbol from Yahoo Finance
def fetch_data(symbol, start="2025-01-01", end="2025-12-31"):
    # Format URL with symbol and date range
    url = f"https://query2.finance.yahoo.com/v8/finance/chart/{symbol}?period1={int(datetime.strptime(start, '%Y-%m-%d').timestamp())}&period2={int(datetime.strptime(end, '%Y-%m-%d').timestamp())}&interval=0d&events=history"
    
    # Headers to mimic a browser
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}

    # Make the request
    response = requests.get(url, headers=headers)

    # Check if the request was successful
    if response.status_code == 200:
        # Parse the JSON data
        data = response.json()
        
        # Extract timestamps, close prices, and volume data
        timestamps = data['chart']['result'][0]['timestamp']
        close_prices = data['chart']['result'][0]['indicators']['quote'][0]['close']
        volumes = data['chart']['result'][0]['indicators']['quote'][0]['volume']
        
        # Convert timestamps to datetime and create DataFrame
        df = pd.DataFrame({
            'Date': [datetime.fromtimestamp(ts) for ts in timestamps],
            'Close': close_prices,
            'Volume': volumes
        })
        
        # Calculate daily return
        df['return'] = df['Close'].pct_change()

        # Calculate 10-day rolling volatility
        df['volatility'] = df['return'].rolling(10).std()

        # Add the symbol as a new column
        df['symbol'] = symbol

        return df
    else:
        print(f"Error: Received status code {response.status_code}")
        return None

# List of symbols to fetch data for
symbols = ["NVDA", "AMD", "AAPL", "MSFT", "TSLA", "JPM", "XOM", "KO", "META", "QQQ"]

all_data = []

# Loop through each symbol and fetch the data
for symbol in symbols:
    try:
        print(f"Downloading {symbol}...")
        df = fetch_data(symbol)
        if df is not None:
            all_data.append(df)
        # Wait to avoid rate limiting
        time.sleep(5)
    except Exception as e:
        print(f"Failed {symbol}: {e}")
        time.sleep(10)

# Concatenate all the DataFrames
final_df = pd.concat(all_data, ignore_index=True)

# Save the data to CSV
def save_to_csv(df, filename):
    df.to_csv(filename, index=False)  # Ensure index is not written to CSV
    print(f"Saved to {filename}")

# Save the final data to a CSV file
save_to_csv(final_df, r"D:\.anaconda\sentiment_analysis\yahoo_data_with_volume.csv")
