import pandas as pd
import yfinance as yf

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
    if df.empty:
        return df.copy()

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

    df.fillna(0, inplace=True)
    return df

def generate_signals(df: pd.DataFrame, market_status: str = "Bullish") -> pd.DataFrame:
    if df.empty:
        return df.copy()

    df = df.copy()
    df.fillna(0, inplace=True)
    df["Signal"] = "HOLD"

    buy_condition = (df["Close"] > df["Ema20"]) & (df["Rsi"] > 55) & (df["Macd"] > 0)
    sell_condition = (df["Close"] < df["Ema20"]) & (df["Rsi"] < 45) & (df["Macd"] < 0)

    # 🛡️ ป้องกันตลาดขาลง ไม่ให้เข้า BUY
    if market_status == "Bearish":
        buy_condition[:] = False

    df.loc[buy_condition, "Signal"] = "BUY"
    df.loc[sell_condition, "Signal"] = "SELL"
    return df

def assess_market_condition(df: pd.DataFrame) -> str:
    try:
        if df.empty or len(df) < 20:
            return "Unknown"

        required = ["Rsi", "Ema20", "Ema50", "Macd"]
        for col in required:
            if col not in df.columns:
                return "Unknown"

        df = df.fillna(0)
        recent = df.iloc[-1]

        cond = sum([
            recent["Rsi"] > 55,
            recent["Ema20"] > recent["Ema50"],
            recent["Macd"] > 0,
        ])

        if cond >= 2: return "Bullish"
        elif cond == 1: return "Neutral"
        else: return "Bearish"
    except Exception as e:
        print(f"Market Filter Error: {e}")
        return "Unknown"
