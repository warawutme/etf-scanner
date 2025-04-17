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

    return df

def generate_signals(df: pd.DataFrame, market_status: str = "Bullish") -> pd.DataFrame:
    if df.empty:
        return df

    df = df.copy()

    # 🔧 แก้จุดพัง: จัด index ให้ตรงกันทุก column
    df = df.dropna(subset=["Ema20", "Rsi", "Macd"])

    df["Signal"] = "HOLD"
    if market_status == "Unknown":
        market_status = "Neutral"

    try:
        buy_condition = (df["Close"] > df["Ema20"]) & (df["Rsi"] > 55) & (df["Macd"] > 0)
        sell_condition = (df["Close"] < df["Ema20"]) & (df["Rsi"] < 45) & (df["Macd"] < 0)

        if market_status != "Bearish":
            df.loc[buy_condition, "Signal"] = "BUY"
        df.loc[sell_condition, "Signal"] = "SELL"

        return df
    except Exception as e:
        print(f"Error in generate_signals: {str(e)}")
        raise e

def assess_market_condition(df: pd.DataFrame) -> str:
    try:
        if df.empty or len(df) < 20:
            print("ข้อมูลไม่เพียงพอสำหรับการประเมินตลาด")
            return "Unknown"

        required_columns = ["Rsi", "Ema20", "Ema50", "Macd"]
        if not all(col in df.columns for col in required_columns):
            missing = [col for col in required_columns if col not in df.columns]
            print(f"Missing columns for market condition assessment: {missing}")
            return "Unknown"

        df_clean = df.dropna(subset=required_columns)
        recent = df_clean.iloc[-1]

        rsi_pass = bool(recent["Rsi"] > 55)
        ema_pass = bool(recent["Ema20"] > recent["Ema50"])
        macd_pass = bool(recent["Macd"] > 0)

        cond = sum([rsi_pass, ema_pass, macd_pass])
        if cond >= 2: return "Bullish"
        if cond == 1: return "Neutral"
        return "Bearish"
    except Exception as e:
        print("Market Filter Error:", e)
        return "Unknown"

