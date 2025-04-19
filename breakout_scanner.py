
import pandas as pd
import yfinance as yf
import numpy as np
import time

def fetch_etf_data(ticker: str, retries: int = 3, delay: int = 1) -> pd.DataFrame:
    for attempt in range(retries):
        try:
            if attempt > 0:
                time.sleep(delay * attempt)
            df = yf.download(ticker, period="3mo", interval="1d", progress=False, timeout=10)
            if df.empty or len(df) < 5:
                continue
            return df
        except Exception as e:
            print(f"เกิดข้อผิดพลาดในการโหลด {ticker}: {str(e)}")
    return pd.DataFrame()

def calculate_technical_indicators(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty or "Close" not in df.columns:
        return df
    df = df.copy()
    df["Ema20"] = df["Close"].ewm(span=20, adjust=False).mean()
    df["Ema50"] = df["Close"].ewm(span=50, adjust=False).mean()
    delta = df["Close"].diff()
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)
    avg_gain = gain.rolling(window=14).mean()
    avg_loss = loss.rolling(window=14).mean().replace(0, np.nan)
    rs = avg_gain / avg_loss
    df["Rsi"] = 100 - (100 / (1 + rs))
    ema12 = df["Close"].ewm(span=12, adjust=False).mean()
    ema26 = df["Close"].ewm(span=26, adjust=False).mean()
    df["Macd"] = ema12 - ema26
    return df

def assess_market_condition(df: pd.DataFrame) -> str:
    required_columns = ["Rsi", "Ema20", "Ema50", "Macd", "Close"]
    if not all(col in df.columns for col in required_columns):
        return "Unknown"
    df_clean = df.dropna(subset=required_columns).copy()
    if df_clean.empty:
        return "Unknown"
    recent = df_clean.iloc[-1]
    rsi_pass = recent["Rsi"] > 55
    ema_pass = recent["Ema20"] > recent["Ema50"]
    macd_pass = recent["Macd"] > 0
    score = sum([rsi_pass, ema_pass, macd_pass])
    if score >= 2:
        return "Bullish"
    elif score == 1:
        return "Neutral"
    else:
        return "Bearish"

def generate_signals(df: pd.DataFrame, market_status: str = "Bullish") -> pd.DataFrame:
    if df.empty:
        return df
    required_columns = ["Close", "Ema20", "Rsi", "Macd"]
    if not all(col in df.columns for col in required_columns):
        return df
    df_clean = df.dropna(subset=required_columns).copy()
    if df_clean.empty:
        return df
    df_clean["Signal"] = "HOLD"
    buy_condition = (df_clean["Close"] > df_clean["Ema20"]) &                     (df_clean["Rsi"] > 55) &                     (df_clean["Macd"] > 0)
    sell_condition = (df_clean["Close"] < df_clean["Ema20"]) &                      (df_clean["Rsi"] < 45) &                      (df_clean["Macd"] < 0)
    if market_status == "Bearish":
        buy_condition = pd.Series(False, index=df_clean.index)
    df_clean.loc[buy_condition, "Signal"] = "BUY"
    df_clean.loc[sell_condition, "Signal"] = "SELL"
    df_merged = df.copy()
    df_merged["Signal"] = "HOLD"
    df_merged.update(df_clean[["Signal"]])
    return df_merged
