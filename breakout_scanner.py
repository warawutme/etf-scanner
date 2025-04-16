import yfinance as yf
import pandas as pd

# ดึงข้อมูลจาก yfinance
def fetch_etf_data(ticker, period='3mo', interval='1d'):
    try:
        df = yf.download(ticker, period=period, interval=interval)
        df = df[['Close']].rename(columns={'Close': 'close'})
        df.dropna(inplace=True)
        return df
    except Exception as e:
        print(f"Error fetching {ticker}: {e}")
        return pd.DataFrame()

# คำนวณอินดิเคเตอร์ทางเทคนิค
def calculate_technical_indicators(df):
    df['ema20'] = df['close'].ewm(span=20, adjust=False).mean()
    df['rsi'] = compute_rsi(df['close'], 14)
    return df

# คำนวณ RSI
def compute_rsi(series, period=14):
    delta = series.diff()
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)
    avg_gain = gain.rolling(window=period).mean()
    avg_loss = loss.rolling(window=period).mean()
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

# ประเมินแนวโน้มตลาดจาก RSI ของ ETF หลัก เช่น SPY

def assess_market_condition(df):
    rsi = df['rsi'].iloc[-1]
    if rsi > 60:
        return "Bullish"
    elif rsi < 40:
        return "Bearish"
    else:
        return "Neutral"

# สร้างสัญญาณ BUY / SELL

def generate_signals(df, market_status):
    df['signal'] = 'HOLD'
    for i in range(1, len(df)):
        if market_status == "Bullish" and df['close'].iloc[i] > df['ema20'].iloc[i] and df['rsi'].iloc[i] > 50:
            df.at[i, 'signal'] = 'BUY'
        elif market_status == "Bearish" and df['close'].iloc[i] < df['ema20'].iloc[i] and df['rsi'].iloc[i] < 50:
            df.at[i, 'signal'] = 'SELL'
    return df
    
