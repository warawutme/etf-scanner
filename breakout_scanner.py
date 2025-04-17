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
    if df.empty:
        return df
        
    df = df.copy()
    
    # คำนวณ EMA
    df["Ema20"] = df["Close"].ewm(span=20, adjust=False).mean()
    df["Ema50"] = df["Close"].ewm(span=50, adjust=False).mean()
    
    # คำนวณ RSI
    delta = df["Close"].diff()
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)
    avg_gain = gain.rolling(14).mean()
    avg_loss = loss.rolling(14).mean()
    rs = avg_gain / avg_loss
    df["Rsi"] = 100 - (100 / (1 + rs))
    
    # คำนวณ MACD
    ema12 = df["Close"].ewm(span=12, adjust=False).mean()
    ema26 = df["Close"].ewm(span=26, adjust=False).mean()
    df["Macd"] = ema12 - ema26
    
    # ใช้ fillna เพื่อเติมค่า NaN ด้วยค่าที่เหมาะสม
    for col in ["Ema20", "Ema50", "Rsi", "Macd"]:
        df[col] = df[col].fillna(0)
    
    return df

def generate_signals(df: pd.DataFrame, market_status: str = "Bullish") -> pd.DataFrame:
    if df.empty:
        return df
    
    # สร้าง copy
    df = df.copy()
    
    # เติมค่า NaN ทั้งหมดเพื่อแก้ปัญหา alignment
    for col in df.columns:
        if df[col].isna().any():
            df[col] = df[col].fillna(0)
    
    # กำหนดค่าเริ่มต้น
    df["Signal"] = "HOLD"
    
    # จัดการกับค่า Unknown
    if market_status == "Unknown":
        market_status = "Neutral"
    
    try:
        # วิธีที่ปลอดภัยที่สุดคือแปลงเงื่อนไขเป็น numpy array แล้วค่อยนำกลับมาใช้
        # สร้างเงื่อนไขพื้นฐาน
        close_gt_ema20 = np.array(df["Close"] > df["Ema20"])
        rsi_gt_55 = np.array(df["Rsi"] > 55)
        macd_gt_0 = np.array(df["Macd"] > 0)
        
        close_lt_ema20 = np.array(df["Close"] < df["Ema20"])
        rsi_lt_45 = np.array(df["Rsi"] < 45)
        macd_lt_0 = np.array(df["Macd"] < 0)
        
        # รวมเงื่อนไข
        buy_indices = np.where(close_gt_ema20 & rsi_gt_55 & macd_gt_0)[0]
        sell_indices = np.where(close_lt_ema20 & rsi_lt_45 & macd_lt_0)[0]
        
        # ถ้าตลาดเป็น Bearish ไม่มีสัญญาณซื้อ
        if market_status == "Bearish":
            buy_indices = np.array([])
        
        # ใส่สัญญาณ
        if len(buy_indices) > 0:
            df.iloc[buy_indices, df.columns.get_loc("Signal")] = "BUY"
        if len(sell_indices) > 0:
            df.iloc[sell_indices, df.columns.get_loc("Signal")] = "SELL"
        
        return df
    
    except Exception as e:
        print(f"Error in generate_signals: {str(e)}")
        raise e

def assess_market_condition(df: pd.DataFrame) -> str:
    try:
        # ตรวจสอบว่ามีข้อมูลเพียงพอหรือไม่
        if df.empty or len(df) < 20:  # ต้องมีข้อมูลอย่างน้อย 20 วัน
            print("ข้อมูลไม่เพียงพอสำหรับการประเมินตลาด")
            return "Unknown"
            
        # ตรวจสอบว่าคอลัมน์ที่จำเป็นมีหรือไม่
        required_columns = ["Rsi", "Ema20", "Ema50", "Macd"]
        if not all(col in df.columns for col in required_columns):
            missing = [col for col in required_columns if col not in df.columns]
            print(f"Missing columns for market condition assessment: {missing}")
            return "Unknown"
        
        # เติมค่า NaN เพื่อป้องกันปัญหา
        df_clean = df.copy()
        for col in required_columns:
            df_clean[col] = df_clean[col].fillna(0)
        
        recent = df_clean.iloc[-1]
        
        # คำนวณสถานะตลาด
        rsi_pass = bool(recent["Rsi"] > 55)
        ema_pass = bool(recent["Ema20"] > recent["Ema50"])
        macd_pass = bool(recent["Macd"] > 0)
        
        cond = sum([rsi_pass, ema_pass, macd_pass])
        
        if cond >= 2: 
            return "Bullish"
        elif cond == 1: 
            return "Neutral"
        else: 
            return "Bearish"
    except Exception as e:
        print("Market Filter Error:", e)
        return "Unknown"
