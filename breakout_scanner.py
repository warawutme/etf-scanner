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
    # ดึงคอลัมน์ Close ออกมาก่อนเพื่อป้องกันปัญหา
    close = df["Close"]
    
    # คำนวณ EMA
    df["Ema20"] = close.ewm(span=20, adjust=False).mean()
    df["Ema50"] = close.ewm(span=50, adjust=False).mean()
    
    # คำนวณ RSI
    delta = close.diff()
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)
    avg_gain = gain.rolling(14).mean()
    avg_loss = loss.rolling(14).mean()
    rs = avg_gain / avg_loss
    df["Rsi"] = 100 - (100 / (1 + rs))
    
    # คำนวณ MACD
    ema12 = close.ewm(span=12, adjust=False).mean()
    ema26 = close.ewm(span=26, adjust=False).mean()
    df["Macd"] = ema12 - ema26
    
    # ลบแถวที่มี NaN ออกไปก่อนส่งผลลัพธ์ (ป้องกันปัญหา alignment)
    df = df.dropna()
    
    return df

def generate_signals(df: pd.DataFrame, market_status: str = "Bullish") -> pd.DataFrame:
    if df.empty:
        return df
    
    # สร้าง copy และตรวจสอบให้แน่ใจว่าไม่มี NaN 
    df = df.copy().dropna()
    
    # กำหนดค่าเริ่มต้น
    df["Signal"] = "HOLD"
    
    # จัดการกับค่า Unknown
    if market_status == "Unknown":
        market_status = "Neutral"
    
    try:
        # สร้างเงื่อนไขพื้นฐาน ใช้ method .align() เพื่อจัดการปัญหา index alignment
        close_col, ema20_col = df["Close"].align(df["Ema20"])
        close_col, rsi_col = df["Close"].align(df["Rsi"])
        close_col, macd_col = df["Close"].align(df["Macd"])
        
        # ตรวจสอบขนาดของข้อมูลว่าตรงกันหรือไม่
        if len(close_col) != len(ema20_col) or len(close_col) != len(rsi_col) or len(close_col) != len(macd_col):
            print("Warning: Data lengths don't match after alignment")
            print(f"Close: {len(close_col)}, EMA20: {len(ema20_col)}, RSI: {len(rsi_col)}, MACD: {len(macd_col)}")
        
        # สร้างเงื่อนไขซื้อ
        buy_condition = (close_col > ema20_col) & (rsi_col > 55) & (macd_col > 0)
        
        # ปรับเงื่อนไขตาม market_status
        if market_status == "Bearish":
            # ไม่ซื้อในตลาดขาลง
            buy = buy_condition & pd.Series(False, index=buy_condition.index)
        else:
            buy = buy_condition
        
        # เงื่อนไขขาย
        sell = (close_col < ema20_col) & (rsi_col < 45) & (macd_col < 0)
        
        # กำหนดสัญญาณ
        df.loc[buy.index[buy], "Signal"] = "BUY"
        df.loc[sell.index[sell], "Signal"] = "SELL"
        
        return df
    
    except Exception as e:
        # แสดงข้อความและส่งต่อ exception เพื่อให้ app.py จัดการ
        print(f"Error in generate_signals: {e}")
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
        
        # ทำให้แน่ใจว่าไม่มี NaN ในข้อมูล
        df_clean = df.dropna()
        if df_clean.empty:
            print("All data contain NaN values")
            return "Unknown"
        
        recent = df_clean.iloc[-1]
        
        # ตรวจสอบว่าค่าไม่ใช่ NaN
        if pd.isna(recent["Rsi"]) or pd.isna(recent["Ema20"]) or pd.isna(recent["Ema50"]) or pd.isna(recent["Macd"]):
            print("Some technical indicators contain NaN values")
            return "Unknown"
        
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
