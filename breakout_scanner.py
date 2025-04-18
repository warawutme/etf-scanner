import pandas as pd
import numpy as np
import yfinance as yf

def fetch_data(ticker: str, period: str = "1y"):
    """
    ดึงข้อมูลราคาย้อนหลังของ ETF ตามระยะเวลาที่กำหนดจาก Yahoo Finance.
    คืนค่า DataFrame ของราคาย้อนหลัง หรือ None หากไม่พบข้อมูล.
    """
    try:
        df = yf.download(ticker, period=period, progress=False)
    except Exception as e:
        print(f"[Error] Cannot fetch data for {ticker}: {e}")
        return None
    if df is None or df.empty:
        # กรณีไม่ได้ข้อมูล
        print(f"[Warning] No data found for {ticker}")
        return None
    # ทำให้แน่ใจว่า index เป็นชนิด DateTime (เผื่อกรณีได้ index เป็น string)
    df.index = pd.to_datetime(df.index)
    # จัดให้มีคอลัมน์ชื่อมาตรฐาน (กรณี yfinance ส่งคืน multi-index เราจะเลือกใช้ Adj Close หรือ Close)
    if "Adj Close" in df.columns:
        # บางครั้ง Adj Close มีความสำคัญสำหรับการลงทุน (ปรับปรุง dividend) แต่ที่นี่ใช้ Close ก็พอ
        # หาก Close ไม่มี (บาง ETF อาจไม่มี Adj Close) ก็ใช้ Close
        pass
    return df

def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """
    เพิ่มคอลัมน์อินดิเคเตอร์ EMA20, EMA50, RSI14, MACD (Line & Signal) ใน DataFrame.
    จัดการ NaN ที่เกิดขึ้นจากการคำนวณเพื่อความปลอดภัย.
    """
    # ต้องมีคอลัมน์ 'Close' ใน df
    if "Close" not in df.columns:
        raise KeyError("DataFrame must contain 'Close' column for indicator calculations")
    # คำนวณ EMA20 และ EMA50
    df["EMA20"] = df["Close"].ewm(span=20, adjust=False).mean()
    df["EMA50"] = df["Close"].ewm(span=50, adjust=False).mean()
    # คำนวณ RSI 14 วัน
    window_length = 14
    # เปลี่ยนแปลงของราคา (delta)
    delta = df["Close"].diff()
    # กำไร (up) และ ขาดทุน (down)
    up = delta.clip(lower=0)
    down = -1 * delta.clip(upper=0)
    # ค่าเฉลี่ย gain/loss ในช่วง 14 วัน (ใช้ rolling mean)
    # min_periods=14 เพื่อไม่คำนวณค่าในช่วงที่ข้อมูลไม่ครบ 14 วันแรก
    avg_gain = up.rolling(window=window_length, min_periods=window_length).mean()
    avg_loss = down.rolling(window=window_length, min_periods=window_length).mean()
    # คำนวณ RSI
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    # จัดการค่า RSI ที่เป็น NaN หรือ infinite
    # ถ้า avg_loss เป็น 0 -> rs = infinite -> RSI = 100, ถ้า avg_gain เป็น 0 -> RSI = 0
    rsi = rsi.fillna(0)  # เบื้องต้นแทน NaN ด้วย 0 (สำหรับกรณีช่วงแรกที่ยังไม่มีค่า)
    rsi[np.isinf(rsi)] = 100  # ถ้ามีค่าที่เป็น infinite ให้แทนด้วย 100
    # กรณีไม่มีการเปลี่ยนแปลงราคาเลยในช่วง 14 วัน (avg_gain=0 และ avg_loss=0) -> RSI ควรจะเป็น 50
    rsi = rsi.replace(to_replace=0, value=50) if (avg_gain.iloc[window_length-1] == 0 and avg_loss.iloc[window_length-1] == 0) else rsi
    df["RSI"] = rsi
    # คำนวณ MACD line และ Signal line
    ema12 = df["Close"].ewm(span=12, adjust=False).mean()
    ema26 = df["Close"].ewm(span=26, adjust=False).mean()
    df["MACD_line"] = ema12 - ema26
    df["MACD_signal"] = df["MACD_line"].ewm(span=9, adjust=False).mean()
    # เติม NaN ที่อาจเหลือ (เช่น RSI ช่วงแรก) ด้วยค่าเหมาะสม (RSI เติม 50 สำหรับช่วงแรกที่ไม่มีข้อมูลเพียงพอ)
    df["RSI"].fillna(50, inplace=True)
    df.fillna(method="ffill", inplace=True)  # เติม NaN อื่น ๆ (ถ้ามี) ด้วยค่าล่าสุดก่อนหน้า
    df.fillna(method="bfill", inplace=True)  # กรณีต้นชุดข้อมูลมี NaN ก็เติมด้วยค่าถัดไป
    return df

def generate_signals(df: pd.DataFrame) -> pd.DataFrame:
    """
    สร้างคอลัมน์ 'Signal' ใน DataFrame ตามเงื่อนไข BUY/SELL/HOLD.
    """
    # แน่ใจว่าคอลัมน์อินดิเคเตอร์ที่ต้องใช้มีครบ
    required_cols = ["Close", "EMA20", "EMA50", "RSI", "MACD_line", "MACD_signal"]
    for col in required_cols:
        if col not in df.columns:
            raise KeyError(f"Missing required indicator column: {col}")
    # เริ่มต้นให้ทุกสถานะเป็น HOLD
    df["Signal"] = "HOLD"
    # เงื่อนไขสำหรับ BUY
    buy_condition = (
        (df["Close"] > df["EMA20"]) & 
        (df["Close"] > df["EMA50"]) & 
        (df["EMA20"] > df["EMA50"]) & 
        (df["RSI"] > 50) & 
        (df["MACD_line"] > df["MACD_signal"])
    )
    # เงื่อนไขสำหรับ SELL
    sell_condition = (
        (df["Close"] < df["EMA20"]) & 
        (df["Close"] < df["EMA50"]) & 
        (df["EMA20"] < df["EMA50"]) & 
        (df["RSI"] < 50) & 
        (df["MACD_line"] < df["MACD_signal"])
    )
    df.loc[buy_condition, "Signal"] = "BUY"
    df.loc[sell_condition, "Signal"] = "SELL"
    return df

def analyze_ticker(ticker: str, period: str = "1y") -> pd.DataFrame:
    """
    ดึงข้อมูลราคาของ ticker ที่ระบุ และคำนวณอินดิเคเตอร์พร้อมสัญญาณ, คืนค่า DataFrame ที่ได้.
    """
    df = fetch_data(ticker, period)
    if df is None:
        return None
    df = add_indicators(df)
    df = generate_signals(df)
    return df

def evaluate_market(market_df: pd.DataFrame) -> str:
    """
    ประเมินสถานะตลาด (Bullish, Bearish, Neutral) จากข้อมูลตลาดรวม (เช่น SPY หรือ QQQ).
    ใช้ค่า EMA20 และ EMA50 ล่าสุดในการตัดสิน.
    """
    if market_df is None or market_df.empty:
        return "Unknown"
    # ใช้ข้อมูลวันล่าสุด
    last_close = market_df["Close"].iloc[-1]
    last_ema20 = market_df["EMA20"].iloc[-1]
    last_ema50 = market_df["EMA50"].iloc[-1]
    status = "Neutral"
    # กำหนดเงื่อนไข Bullish/Bearish
    if last_close > last_ema50 and last_ema20 > last_ema50:
        status = "Bullish"
    elif last_close < last_ema50 and last_ema20 < last_ema50:
        status = "Bearish"
    else:
        status = "Neutral"
    return status
