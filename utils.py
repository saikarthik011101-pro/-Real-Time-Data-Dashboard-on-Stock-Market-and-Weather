# utils.py
import os
import requests
import pandas as pd
from tenacity import retry, stop_after_attempt, wait_exponential
from dotenv import load_dotenv

load_dotenv()
ALPHA_KEY = os.getenv("ALPHA_KEY")
WEATHER_KEY = os.getenv("WEATHER_KEY")

# Fetch stock data
@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
def fetch_alpha_intraday(symbol: str, interval: str = "5min"):
    url = (f"API LINK"
           f"&symbol={symbol}&interval={interval}&apikey={ALPHA_KEY}&outputsize=compact")
    r = requests.get(url, timeout=10)
    r.raise_for_status()
    data = r.json()
    if "Note" in data:
        raise Exception("Alpha Vantage rate limit hit. Try later.")
    return data

# Parse stock JSON
def parse_alpha_intraday_json(data):
    key = next((k for k in data if "Time Series" in k), None)
    if not key:
        return None
    df = pd.DataFrame(data[key]).T
    df = df.rename(columns={
        "1. open": "Open", "2. high": "High", "3. low": "Low",
        "4. close": "Close", "5. volume": "Volume"
    })
    df.index = pd.to_datetime(df.index)
    df = df.astype(float).sort_index()
    return df

# Fetch weather data
@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
def fetch_weather(city: str):
    url = f"API LINK"
    r = requests.get(url, timeout=10)
    r.raise_for_status()
    return r.json()
