# breakout_scanner.py
import pandas as pd
import yfinance as yf

def fetch_etf_data(ticker: str) -> pd.DataFrame:
    """
    ดึง Close price ของ ticker มา 3 เดือน พร้อม DatetimeIndex
    """
    df = yf.download(ticker, period="3mo", interval="1d", progress=False)
    return df[["Close"]].dropna()

def calculate_technical_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["Ema20"] = df["Close"].ewm(span=20, adjust=False).mean()
    df["Ema50"] = df["Close"].ewm(span=50, adjust=False).mean()

    delta = df["Close"].diff()
    gain  = delta.where(delta > 0, 0)
    loss  = -delta.where(delta < 0, 0)
    avg_gain = gain.rolling(14).mean()
    avg_loss = loss.rolling(14).mean()
    rs = avg_gain / avg_loss
    df["Rsi"] = 100 - (100 / (1 + rs))

    ema12 = df["Close"].ewm(span=12, adjust=False).mean()
    ema26 = df["Close"].ewm(span=26, adjust=False).mean()
    df["Macd"] = ema12 - ema26

    return df.dropna()

def generate_signals(df: pd.DataFrame, market_status: str = "Bullish") -> pd.DataFrame:
    df = df.copy()
    df["Signal"] = "HOLD"
    buy  = (df["Close"] > df["Ema20"]) & (df["Rsi"] > 55) & (df["Macd"] > 0) & (market_status != "Bearish")
    sell = (df["Close"] < df["Ema20"]) & (df["Rsi"] < 45) & (df["Macd"] < 0)
    df.loc[buy,  "Signal"] = "BUY"
    df.loc[sell, "Signal"] = "SELL"
    return df

def assess_market_condition(df: pd.DataFrame) -> str:
    recent = df.iloc[-1]
    cond = sum([
        recent["Rsi"]   > 55,
        recent["Ema20"] > recent["Ema50"],
        recent["Macd"]  > 0,
    ])
    if cond >= 2: return "Bullish"
    if cond == 1: return "Neutral"
    return "Bearish"
