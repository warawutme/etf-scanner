import yfinance as yf
import pandas as pd
import pandas_ta as ta

def fetch_etf_data(ticker):
    try:
        df = yf.download(ticker, period="6mo", interval="1d", auto_adjust=True)
        if df.empty:
            return None
        return df
    except Exception as e:
        print(f"Error fetching {ticker}: {e}")
        return None

def calculate_technical_indicators(df):
    if df is None or df.empty:
        return df

    close = df['Close']
    df['Ema20'] = close.ewm(span=20, adjust=False).mean()
    df['Ema50'] = close.ewm(span=50, adjust=False).mean()
    df['Rsi'] = ta.rsi(close, length=14)
    macd = ta.macd(close)
    if macd is not None:
        df['Macd'] = macd['MACD_12_26_9'] - macd['MACDs_12_26_9']
    else:
        df['Macd'] = 0
    return df

def generate_signals(df):
    if df is None or df.empty:
        return df

    df['Signal'] = 'HOLD'
    latest = df.iloc[-1]
    if latest['Close'] > latest['Ema20'] and latest['Rsi'] > 55 and latest['Macd'] > 0:
        df.at[df.index[-1], 'Signal'] = 'BUY'
    elif latest['Close'] < latest['Ema50'] and latest['Rsi'] < 45 and latest['Macd'] < 0:
        df.at[df.index[-1], 'Signal'] = 'SELL'
    return df

def get_latest_signal(df):
    if df is None or df.empty:
        return None
    return df['Signal'].iloc[-1]
