import pandas as pd
import yfinance as yf
import numpy as np

# ─────────────────────────────────────────────
def fetch_etf_data(ticker: str) -> pd.DataFrame:
    try:
        df = yf.download(ticker, period="3mo", interval="1d", progress=False)
        if df.empty:
            print(f"❌ ไม่พบข้อมูลสำหรับ {ticker}")
            return pd.DataFrame()
        return df[["Close"]].dropna()
    except Exception as e:
        print(f"⚠️ Error fetching data for {ticker}: {e}")
        return pd.DataFrame()

# ─────────────────────────────────────────────
def calculate_technical_indicators(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return df

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

    # เติม NaN
    for col in ["Ema20", "Ema50", "Rsi", "Macd"]:
        df[col] = df[col].fillna(0)

    return df

# ─────────────────────────────────────────────
def generate_signals(df: pd.DataFrame, market_status: str = "Bullish") -> pd.DataFrame:
    if df.empty:
        return df

    df = df.copy()
    df["Signal"] = "HOLD"

    if market_status == "Unknown":
        market_status = "Neutral"

    try:
        buy = (
            (df["Close"] > df["Ema20"]) &
            (df["Rsi"] > 55) &
            (df["Macd"] > 0) &
            (market_status != "Bearish")
        )

        sell = (
            (df["Close"] < df["Ema20"]) &
            (df["Rsi"] < 45) &
            (df["Macd"] < 0)
        )

        df.loc[buy, "Signal"] = "BUY"
        df.loc[sell, "Signal"] = "SELL"
        return df

    except Exception as e:
        print(f"⚠️ Error in generate_signals: {str(e)}")
        return df

# ─────────────────────────────────────────────
def assess_market_condition(df: pd.DataFrame) -> str:
    try:
        if df.empty or len(df) < 20:
            print("⚠️ ข้อมูลไม่พอประเมินตลาด")
            return "Unknown"

        required = ["Rsi", "Ema20", "Ema50", "Macd"]
        if not all(col in df.columns for col in required):
            print(f"⚠️ ขาดคอลัมน์ที่จำเป็น: {required}")
            return "Unknown"

        df = df.copy()
        for col in required:
            df[col] = df[col].fillna(0)

        last = df.iloc[-1]

        cond = sum([
            last["Rsi"] > 55,
            last["Ema20"] > last["Ema50"],
            last["Macd"] > 0
        ])

        if cond >= 2: return "Bullish"
        if cond == 1: return "Neutral"
        return "Bearish"

    except Exception as e:
        print(f"⚠️ Market Filter Error: {e}")
        return "Unknown"
