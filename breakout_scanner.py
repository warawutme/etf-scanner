import pandas as pd
import yfinance as yf
import numpy as np
import time

def fetch_etf_data(ticker: str, retries: int = 3, delay: int = 1) -> pd.DataFrame:
    for attempt in range(retries):
        try:
            if attempt > 0:
                time.sleep(delay * attempt)
            print(f"📥 กำลังโหลด {ticker} (ครั้งที่ {attempt+1})")
            df = yf.download(ticker, period="3mo", interval="1d", progress=False, timeout=10)
            if df.empty or len(df) < 5:
                print(f"⚠️ ข้อมูล {ticker} ไม่เพียงพอ")
                continue
            return df
        except Exception as e:
            print(f"❌ Error: {e}")
    return pd.DataFrame()

def calculate_technical_indicators(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        print("⚠️ DataFrame ว่าง")
        return df

    if "Close" not in df.columns:
        print("❌ ไม่พบคอลัมน์ 'Close'")
        print("คอลัมน์ทั้งหมด:", df.columns.tolist())
        return df

    # แปลง df["Close"] ให้เป็น Series ที่ถูกต้อง
    try:
        close_col = df["Close"]
        if isinstance(close_col, pd.DataFrame):
            close_col = close_col.iloc[:, 0]
        df["Close"] = pd.to_numeric(close_col.values, errors="coerce")
    except Exception as e:
        print("❌ แปลง 'Close' ไม่ได้:", e)
        return pd.DataFrame()

    df = df.dropna(subset=["Close"]).copy()

    print("✅ เริ่มคำนวณ EMA / RSI / MACD")
    print("📊 ข้อมูลล่าสุด:", df.tail(3))
    print("📈 dtype ของ Close:", df["Close"].dtype)

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

    expected_cols = ["Ema20", "Ema50", "Rsi", "Macd"]
    for col in expected_cols:
        if col not in df.columns:
            print(f"⚠️ คอลัมน์ {col} ไม่ถูกสร้าง")

    print("✅ คำนวณเสร็จสิ้น: columns =", df.columns.tolist())
    return df

def assess_market_condition(df: pd.DataFrame) -> str:
    required_columns = ["Rsi", "Ema20", "Ema50", "Macd", "Close"]
    if not all(col in df.columns for col in required_columns):
        missing = [col for col in required_columns if col not in df.columns]
        print(f"⚠️ คอลัมน์ที่ขาดสำหรับประเมินตลาด: {missing}")
        return "Unknown"
    df_clean = df.dropna(subset=required_columns).copy()
    if df_clean.empty:
        print("⚠️ ไม่มีข้อมูลเพียงพอสำหรับประเมินตลาด")
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
        print("⚠️ ข้อมูลไม่ครบสำหรับสร้างสัญญาณ")
        return df

    df_clean = df.dropna(subset=required_columns).copy()
    if df_clean.empty:
        print("⚠️ ข้อมูลว่างหลังกรอง NaN")
        return df

    df_clean["Signal"] = "HOLD"

    buy_condition = (df_clean["Close"] > df_clean["Ema20"]) & \
                    (df_clean["Rsi"] > 55) & \
                    (df_clean["Macd"] > 0)

    sell_condition = (df_clean["Close"] < df_clean["Ema20"]) & \
                     (df_clean["Rsi"] < 45) & \
                     (df_clean["Macd"] < 0)

    if market_status == "Bearish":
        buy_condition = pd.Series(False, index=df_clean.index)

    df_clean.loc[buy_condition, "Signal"] = "BUY"
    df_clean.loc[sell_condition, "Signal"] = "SELL"

    df_merged = df.copy()
    df_merged["Signal"] = "HOLD"
    df_merged.update(df_clean[["Signal"]])
    return df_merged

