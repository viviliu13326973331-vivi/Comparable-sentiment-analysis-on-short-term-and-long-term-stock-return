# -*- coding: utf-8 -*-


import pandas as pd

df1=pd.read_csv(r"D:\.anaconda\sentiment_analysis\stocktwits_1_2.csv")
df2=pd.read_csv(r"D:\.anaconda\sentiment_analysis\stocktwits_35.csv")
df3=pd.read_csv(r"D:\.anaconda\sentiment_analysis\stocktwits_68.csv")
df4=pd.read_csv(r"D:\.anaconda\sentiment_analysis\stocktwits_911.csv")
df5=pd.read_csv(r"D:\.anaconda\sentiment_analysis\stocktwits_12.csv")

final_df = pd.concat([df1, df2, df3, df4, df5], ignore_index=True)

final_df.to_csv(r"D:\.anaconda\sentiment_analysis\merged_stocktwits.csv", index=False)

import re
import html
import nltk
nltk.download('vader_lexicon')

def clean_text(text):
    if pd.isna(text):
        return ""

    #decode html
    text = html.unescape(text)

    #get rid of URL
    text = re.sub(r"http\S+|www\S+", "", text)

    # delete ticker
    text = re.sub(r"\$\w+", "", text)

    # delete emoji
    text = text.encode("ascii", "ignore").decode()

    # delete special character
    text = re.sub(r"[^a-zA-Z\s]", "", text)

    # lowercase
    text = text.lower()

    # delete space
    text = re.sub(r"\s+", " ", text).strip()

    return text

# cleaning
final_df["clean_text"] = final_df["message"].apply(clean_text)
final_df = final_df[final_df["clean_text"].str.len() > 10]

# sentiment analysis
from nltk.sentiment import SentimentIntensityAnalyzer
sia = SentimentIntensityAnalyzer()

final_df["sentiment"] = final_df["clean_text"].apply(lambda x: sia.polarity_scores(x)["compound"])


final_df["created_at"] = pd.to_datetime(final_df["created_at"])
final_df["date"] = final_df["created_at"].dt.date

daily = final_df.groupby(["symbol", "date"]).agg({
    "sentiment": "mean"
}).reset_index()

daily.to_csv(r"D:\.anaconda\sentiment_analysis\daily__symbol_sentiment.csv", index=False)



# Yahoo data

df1 = pd.read_csv(r"D:\.anaconda\sentiment_analysis\yahoo_data_with_volume.csv")

df1.columns = df1.columns.str.strip()

df1["symbol"] = df1["symbol"].str.strip().str.upper()
df1["date"] = pd.to_datetime(df1["Date"], errors="coerce").dt.date


# sentiment data

df2 = daily

df2.columns = df2.columns.str.strip()

df2["symbol"] = df2["symbol"].str.strip().str.upper()
df2["date"] = pd.to_datetime(df2["date"], errors="coerce").dt.date



# merge

merged = pd.merge(
    df1,
    df2,
    on=["symbol", "date"],
    how="left"
)

merged.drop(columns=["Date"], inplace=True)

merged.to_csv(
    r"D:\.anaconda\sentiment_analysis\merged_data.csv",
    index=False
)


