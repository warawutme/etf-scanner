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
    df.dropna(inplace=True)
    return df

# ====== ฟังก์ชันสร้างสัญญาณ ======
def generate_signals(df):
    df = df.copy()
    df['Signal'] = 'HOLD'
    try:
        df.loc[
            (df['Close'] > df['Ema20']) & 
            (df['Rsi'] > 55) & 
            (df['Macd'] > 0),
            'Signal'
        ] = 'BUY'

        df.loc[
            (df['Close'] < df['Ema20']) & 
            (df['Rsi'] < 45) & 
            (df['Macd'] < 0),
            'Signal'
        ] = 'SELL'
    except Exception as e:
        print("Signal Generation Error:", e)
    return df
