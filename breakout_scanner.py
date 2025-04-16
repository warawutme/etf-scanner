import pandas as pd
import yfinance as yf

def fetch_etf_data(ticker):
    try:
        df = yf.download(ticker, period="60d", interval="1d")
        df = df[['Close']].copy()
        df.columns = ['Close']
        return df
    except:
        return pd.DataFrame()

def calculate_technical_indicators(df):
    df = df.copy()
    df['Ema20'] = df['Close'].ewm(span=20, adjust=False).mean()
    df['Ema50'] = df['Close'].ewm(span=50, adjust=False).mean()
    df['MACD'] = df['Close'].ewm(span=12, adjust=False).mean() - df['Close'].ewm(span=26, adjust=False).mean()

    # RSI (ไม่ใช้ pandas_ta)
    delta = df['Close'].diff()
    gain = delta.where(delta > 0, 0).rolling(window=14).mean()
    loss = -delta.where(delta < 0, 0).rolling(window=14).mean()
    rs = gain / loss
    df['Rsi'] = 100 - (100 / (1 + rs))

    return df

def generate_signals(df):
    df = df.copy()
    df['Signal'] = 'HOLD'
    df.loc[(df['Close'] > df['Ema20']) & (df['Rsi'] > 55) & (df['MACD'] > 0), 'Signal'] = 'BUY'
    df.loc[(df['Close'] < df['Ema20']) & (df['Rsi'] < 45) & (df['MACD'] < 0), 'Signal'] = 'SELL'
    return df
