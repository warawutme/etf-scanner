import pandas as pd
import yfinance as yf
import numpy as np
import time
from typing import Union, Tuple

def fetch_etf_data(ticker: str, retries: int = 3, delay: int = 1) -> pd.DataFrame:
    """
    โหลดข้อมูล ETF จาก Yahoo Finance พร้อม retry และ delay
    """
    for attempt in range(retries):
        try:
            # เพิ่ม delay เพื่อป้องกัน rate limiting
            if attempt > 0:
                time.sleep(delay * attempt)  # เพิ่ม delay ตามจำนวนครั้งที่ retry
            
            print(f"กำลังโหลดข้อมูล {ticker} (ครั้งที่ {attempt+1}/{retries})")
            df = yf.download(ticker, period="3mo", interval="1d", progress=False, timeout=10)
            
            if df.empty:
                print(f"ไม่พบข้อมูลสำหรับ {ticker} ในครั้งที่ {attempt+1}")
                continue
                
            # ตรวจสอบว่าข้อมูลสมบูรณ์หรือไม่
            if len(df) < 5:  # ต้องมีข้อมูลอย่างน้อย 5 แถว
                print(f"ข้อมูล {ticker} ไม่เพียงพอ ({len(df)} แถว)")
                continue
                
            print(f"โหลดข้อมูล {ticker} สำเร็จ: {len(df)} แถว")
            return df  # คืนค่า DataFrame เต็มรูปแบบไม่เฉพาะ Close
            
        except Exception as e:
            print(f"เกิดข้อผิดพลาดในการโหลด {ticker} ครั้งที่ {attempt+1}: {str(e)}")
            
    print(f"ไม่สามารถโหลดข้อมูล {ticker} ได้หลังจากพยายาม {retries} ครั้ง")
    return pd.DataFrame()  # คืนค่า DataFrame ว่างถ้าล้มเหลวทุกครั้ง

def calculate_technical_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """
    คำนวณตัวชี้วัดทางเทคนิคสำหรับ ETF
    """
    if df.empty:
        return df
        
    # ทำงานกับสำเนาของ DataFrame
    df = df.copy()
    
    # ตรวจสอบว่ามีคอลัมน์ Close หรือไม่
    if "Close" not in df.columns:
        print("ไม่พบคอลัมน์ Close ในข้อมูล")
        return df
        
    # คำนวณ EMA
    df["Ema20"] = df["Close"].ewm(span=20, adjust=False).mean()
    df["Ema50"] = df["Close"].ewm(span=50, adjust=False).mean()
    
    # คำนวณ RSI
    delta = df["Close"].diff()
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)
    avg_gain = gain.rolling(window=14).mean()
    avg_loss = loss.rolling(window=14).mean()
    
    # ป้องกันการหารด้วย 0
    avg_loss = avg_loss.replace(0, np.nan)
    rs = avg_gain / avg_loss
    df["Rsi"] = 100 - (100 / (1 + rs))
    
    # คำนวณ MACD
    ema12 = df["Close"].ewm(span=12, adjust=False).mean()
    ema26 = df["Close"].ewm(span=26, adjust=False).mean()
    df["Macd"] = ema12 - ema26
    
    # จัดการค่า NaN ที่เกิดจากการคำนวณ
    # เก็บเฉพาะแถวที่มีข้อมูลเพียงพอสำหรับการคำนวณ (ตัด NaN ออก)
    return df

def assess_market_condition(df: pd.DataFrame) -> str:
    """
    ประเมินสภาวะตลาดจากข้อมูลทางเทคนิค
    """
    required_columns = ["Rsi", "Ema20", "Ema50", "Macd", "Close"]
    
    # ตรวจสอบคอลัมน์ที่จำเป็น
    if not all(col in df.columns for col in required_columns):
        missing = [col for col in required_columns if col not in df.columns]
        print(f"คอลัมน์ที่จำเป็นไม่ครบ: {missing}")
        return "Unknown"
    
    # ลบแถวที่มีค่า NaN และทำงานกับสำเนา
    df_clean = df.dropna(subset=required_columns).copy()
    
    if df_clean.empty:
        print("ไม่มีข้อมูลเพียงพอสำหรับประเมินตลาด")
        return "Unknown"
    
    # ใช้ข้อมูลล่าสุดในการประเมิน
    recent = df_clean.iloc[-1]
    
    # ตัวชี้วัดต่างๆ
    rsi_pass = recent["Rsi"] > 55
    ema_pass = recent["Ema20"] > recent["Ema50"]
    macd_pass = recent["Macd"] > 0
    
    # คะแนนรวม
    score = sum([rsi_pass, ema_pass, macd_pass])
    
    if score >= 2:
        return "Bullish"
    elif score == 1:
        return "Neutral"
    else:
        return "Bearish"

def generate_signals(df: pd.DataFrame, market_status: str = "Bullish") -> pd.DataFrame:
    """
    สร้างสัญญาณซื้อขายตามเงื่อนไขทางเทคนิคและสภาวะตลาด
    """
    if df.empty:
        return df
        
    # ตรวจสอบคอลัมน์ที่จำเป็น
    required_columns = ["Close", "Ema20", "Rsi", "Macd"]
    if not all(col in df.columns for col in required_columns):
        missing = [col for col in required_columns if col not in df.columns]
        print(f"คอลัมน์ที่จำเป็นสำหรับสัญญาณไม่ครบ: {missing}")
        return df
    
    # ลบแถวที่มีค่า NaN และทำงานกับสำเนา
    df_clean = df.dropna(subset=required_columns).copy()
    
    if df_clean.empty:
        print("ไม่มีข้อมูลเพียงพอสำหรับสร้างสัญญาณ")
        return df
    
    # สร้างคอลัมน์สัญญาณ
    df_clean["Signal"] = "HOLD"
    
    # กำหนดเงื่อนไขซื้อขาย
    buy_condition = (df_clean["Close"] > df_clean["Ema20"]) & \
                    (df_clean["Rsi"] > 55) & \
                    (df_clean["Macd"] > 0)
                    
    sell_condition = (df_clean["Close"] < df_clean["Ema20"]) & \
                     (df_clean["Rsi"] < 45) & \
                     (df_clean["Macd"] < 0)
    
    # ปรับตามสภาวะตลาด
    if market_status == "Bearish":
        buy_condition = pd.Series(False, index=df_clean.index)
    
    # กำหนดสัญญาณ
    df_clean.loc[buy_condition, "Signal"] = "BUY"
    df_clean.loc[sell_condition, "Signal"] = "SELL"
    
    # คืนค่า DataFrame พร้อมสัญญาณ (รักษา index ดั้งเดิม)
    df_merged = df.copy()
    df_merged["Signal"] = "HOLD"  # default สำหรับทุกแถว
    df_merged.update(df_clean[["Signal"]])
    
    return df_merged
