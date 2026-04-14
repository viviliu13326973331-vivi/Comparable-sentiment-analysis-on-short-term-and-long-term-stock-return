# -*- coding: utf-8 -*-


import requests
import pandas as pd

def fetch_stocktwits_messages(symbol, api_key, start=None, end=None, max_pages=3):
    base_url = "https://api.stocktwitsapi.com/v1/messages"
    headers = {"x-api-key": api_key}
    
    url = f"{base_url}?symbol={symbol}&primaryOnly=true"
    
    if start and end:
        url += f"&start={start}&end={end}"
    
    all_data = []
    page = 0

    while url and page < max_pages:
        response = requests.get(url, headers=headers)
        
        if response.status_code == 429:
            print("Rate limited (429). Sleeping 60 seconds...")
            time.sleep(60)
            continue
        
        if response.status_code==500:
            time.sleep(120)
            continue
        
        if response.status_code != 200:
            print("Error:", response.status_code)
            break
        
        data = response.json()
        
       
            
        for message in data["messages"]:
            if not message["symbols"]:
                    continue  
            
            if message.get("user") is not None:
                user = message["user"].get("username", "Unknown")  
            else:
                user = "Unknown" 
            
            symbol = message["symbols"][0]["symbol"]
            
            all_data.append({
                "symbol":symbol,
                "user": user,
                "message": message["body"],
                "created_at": message["created_at"]
            })
        
        # Next Page 
        url = data.get("cursor", {}).get("next")
        page += 1
    
    return pd.DataFrame(all_data)


def save_to_csv(df, filename):
    df.to_csv(filename, index=False)
    print(f"Saved to {filename}")



api_key = "stw_62b819896193e347452861b97c916a49189755370a23511c63901b3f11cb1711"


symbols = ["NVDA", "AMD", "AAPL", "MSFT",
           "TSLA", "JPM", "XOM", "KO", "META","GOOGL","QQQ"]

all_dfs = []

import time


for symbol in symbols:
    print(f"Fetching {symbol}...")

    df = fetch_stocktwits_messages(
        symbol=symbol,
        api_key=api_key,
        start="2025-01-01",
        end="2025-02-28",
        max_pages=3
    )

    time.sleep(60) 
    all_dfs.append(df)


final_df = pd.concat(all_dfs, ignore_index=True)


save_to_csv(final_df, r"D:\.anaconda\sentiment_analysis\stocktwits_1_2.csv")
