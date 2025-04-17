import pandas as pd
import yfinance as yf

# ====== ฟังก์ชันดึงข้อมูลจาก yfinance ======
def fetch_etf_data(ticker):
    try:
        df = yf.download(ticker, period="3mo", interval="1d", progress=False)
        df = df[['Close']].copy()
        df.dropna(inplace=True)
        return df
    except:
        return pd.DataFrame()

# ====== คำนวณอินดิเคเตอร์ทางเทคนิค ======
def calculate_technical_indicators(df):
    df = df.copy()
    df['Ema20'] = df['Close'].ewm(span=20, adjust=False).mean()
    df['Ema50'] = df['Close'].ewm(span=50, adjust=False).mean()

    # RSI แบบ manual calculation
    delta = df['Close'].diff()
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)
    avg_gain = gain.rolling(14).mean()
    avg_loss = loss.rolling(14).mean()
    rs = avg_gain / avg_loss
    df['Rsi'] = 100 - (100 / (1 + rs))

    # MACD
    ema_12 = df['Close'].ewm(span=12, adjust=False).mean()
    ema_26 = df['Close'].ewm(span=26, adjust=False).mean()
    df['Macd'] = ema_12 - ema_26

    # ทำให้แน่ใจว่าเป็นตัวเลขทั้งหมด
    df['Rsi'] = pd.to_numeric(df['Rsi'], errors='coerce')
    df['Macd'] = pd.to_numeric(df['Macd'], errors='coerce')
    df['Ema20'] = pd.to_numeric(df['Ema20'], errors='coerce')
    df['Ema50'] = pd.to_numeric(df['Ema50'], errors='coerce')

    df.dropna(inplace=True)
    return df

# ====== ฟังก์ชันสร้างสัญญาณ (รับ market_status ด้วย) ======
def generate_signals(df, market_status="Bullish"):
    df = df.copy()
    df['Signal'] = 'HOLD'
    try:
        buy_condition = (
            (df['Close'] > df['Ema20']) &
            (df['Rsi'] > 55) &
            (df['Macd'] > 0) &
            (market_status != "Bearish")
        )

        sell_condition = (
            (df['Close'] < df['Ema20']) &
            (df['Rsi'] < 45) &
            (df['Macd'] < 0)
        )

        df.loc[buy_condition, 'Signal'] = 'BUY'
        df.loc[sell_condition, 'Signal'] = 'SELL'
    except Exception as e:
        print("Signal Generation Error:", e)
    return df

# ====== ฟังก์ชันวิเคราะห์แนวโน้มตลาดจาก SPY/QQQ ======
def assess_market_condition(df):
    try:
        recent = df.iloc[-1]
        condition = []

        if pd.to_numeric(recent['Rsi'], errors='coerce') > 55:
            condition.append('RSI Bullish')
        if pd.to_numeric(recent['Ema20'], errors='coerce') > pd.to_numeric(recent['Ema50'], errors='coerce'):
            condition.append('EMA Bullish')
        if pd.to_numeric(recent['Macd'], errors='coerce') > 0:
            condition.append('MACD Bullish')

        if len(condition) >= 2:
            return "Bullish"
        elif len(condition) == 1:
            return "Neutral"
        else:
            return "Bearish"
    except Exception as e:
        print("Market Condition Error:", e)
        return "Unknown"
