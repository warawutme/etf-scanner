# ✅ breakout_scanner.py (เวอร์ชันเสถียร พร้อม Market Filter)
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
    if df.empty:
        return df

    df["Ema20"] = df["Close"].ewm(span=20, adjust=False).mean()
    df["Ema50"] = df["Close"].ewm(span=50, adjust=False).mean()

    delta = df["Close"].diff()
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)
    avg_gain = gain.rolling(14).mean()
    avg_loss = loss.rolling(14).mean()

    # แก้บั๊ก RSI
    rs = avg_gain / avg_loss
    rs = rs.replace([np.inf, -np.inf], 0).fillna(0)
    df["Rsi"] = 100 - (100 / (1 + rs))

    ema12 = df["Close"].ewm(span=12, adjust=False).mean()
    ema26 = df["Close"].ewm(span=26, adjust=False).mean()
    df["Macd"] = ema12 - ema26

    df = df.fillna(0)
    return df

def assess_market_condition(df: pd.DataFrame) -> str:
    if df.empty or len(df) < 20:
        return "Unknown"

    last = df.iloc[-1]
    try:
        conditions = [
            last["Rsi"] > 55,
            last["Ema20"] > last["Ema50"],
            last["Macd"] > 0
        ]
        score = sum(conditions)
        if score >= 2:
            return "Bullish"
        elif score == 1:
            return "Neutral"
        else:
            return "Bearish"
    except Exception as e:
        print("Market filter error:", e)
        return "Unknown"

def generate_signals(df: pd.DataFrame, market_status: str = "Bullish") -> pd.DataFrame:
    df = df.copy()
    df["Signal"] = "HOLD"

    if not all(col in df.columns for col in ["Close", "Ema20", "Rsi", "Macd"]):
        return df

    buy_cond = (df["Close"] > df["Ema20"]) & (df["Rsi"] > 55) & (df["Macd"] > 0)
    sell_cond = (df["Close"] < df["Ema20"]) & (df["Rsi"] < 45) & (df["Macd"] < 0)

    if market_status == "Bearish":
        buy_cond[:] = False

    df.loc[buy_cond, "Signal"] = "BUY"
    df.loc[sell_cond, "Signal"] = "SELL"
    return df
