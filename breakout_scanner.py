# breakout_scanner.py
import pandas as pd
import yfinance as yf
import numpy as np

def fetch_etf_data(ticker: str) -> pd.DataFrame:
    try:
        df = yf.download(ticker, period="3mo", interval="1d", progress=False)
        if df.empty:
            print(f"ไม่พบข้อมูลสำหรับ {ticker}")
            return pd.DataFrame()
        return df[["Close"]].dropna()
    except Exception as e:
        print(f"Error fetching data for {ticker}: {e}")
        return pd.DataFrame()

def calculate_technical_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["Ema20"] = df["Close"].ewm(span=20, adjust=False).mean()
    df["Ema50"] = df["Close"].ewm(span=50, adjust=False).mean()
    delta = df["Close"].diff()
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)
    avg_gain = gain.rolling(14).mean()
    avg_loss = loss.rolling(14).mean()
    rs = avg_gain / avg_loss
    df["Rsi"] = 100 - (100 / (1 + rs))
    ema12 = df["Close"].ewm(span=12, adjust=False).mean()
    ema26 = df["Close"].ewm(span=26, adjust=False).mean()
    df["Macd"] = ema12 - ema26
    return df.fillna(0)

def assess_market_condition(df: pd.DataFrame) -> str:
    if df.empty or df.shape[0] < 20:
        return "Unknown"
    recent = df.iloc[-1]
    rsi_pass = recent["Rsi"] > 55
    ema_pass = recent["Ema20"] > recent["Ema50"]
    macd_pass = recent["Macd"] > 0
    cond = sum([rsi_pass, ema_pass, macd_pass])
    return "Bullish" if cond >= 2 else "Neutral" if cond == 1 else "Bearish"

def generate_signals(df: pd.DataFrame, market_status: str = "Bullish") -> pd.DataFrame:
    df = df.copy()
    df["Signal"] = "HOLD"
    if market_status == "Bearish":
        buy_condition = df["Close"] > 1e9  # ทำให้ FALSE
    else:
        buy_condition = (df["Close"] > df["Ema20"]) & (df["Rsi"] > 55) & (df["Macd"] > 0)
    sell_condition = (df["Close"] < df["Ema20"]) & (df["Rsi"] < 45) & (df["Macd"] < 0)
    df.loc[buy_condition, "Signal"] = "BUY"
    df.loc[sell_condition, "Signal"] = "SELL"
    return df
