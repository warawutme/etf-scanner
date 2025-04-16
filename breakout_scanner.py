
import yfinance as yf
import pandas as pd

def fetch_etf_data(ticker, period="6mo", interval="1d"):
    """
    ดึงข้อมูลจาก yfinance โดยไม่ต้องใช้ API Key
    """
    data = yf.download(ticker, period=period, interval=interval, progress=False)
    if data.empty:
        raise ValueError("ไม่พบข้อมูลจาก yfinance")
    data = data.rename(columns={
        "Open": "open",
        "High": "high",
        "Low": "low",
        "Close": "close",
        "Volume": "volume"
    })
    return data

def calculate_technical_indicators(df):
    df['ema20'] = df['close'].ewm(span=20, adjust=False).mean()
    df['ema50'] = df['close'].ewm(span=50, adjust=False).mean()

    delta = df['close'].diff()
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)
    avg_gain = gain.rolling(window=14).mean()
    avg_loss = loss.rolling(window=14).mean()
    rs = avg_gain / avg_loss
    df['rsi'] = 100 - (100 / (1 + rs))

    df['ema12'] = df['close'].ewm(span=12, adjust=False).mean()
    df['ema26'] = df['close'].ewm(span=26, adjust=False).mean()
    df['macd'] = df['ema12'] - df['ema26']

    df['volume_sma50'] = df['volume'].rolling(window=50).mean()
    df['volume_ratio'] = df['volume'] / df['volume_sma50']

    return df

def generate_signals(df, market_status="Bullish"):
    df['signal'] = 'HOLD'
    buy_condition = (
        (df['macd'] > 0) &
        (df['rsi'] > 50) &
        (df['volume_ratio'] > 1.2) &
        (df['close'] > df['ema20']) &
        (market_status != "Bearish")
    )
    sell_condition = (
        (df['macd'] < 0) &
        (df['rsi'] < 45) &
        (df['close'] < df['ema20'])
    )
    df.loc[buy_condition, 'signal'] = 'BUY'
    df.loc[sell_condition, 'signal'] = 'SELL'
    return df

def assess_market_condition(df):
    df['ema20'] = df['close'].ewm(span=20, adjust=False).mean()
    df['ema50'] = df['close'].ewm(span=50, adjust=False).mean()
    if df['close'].iloc[-1] > df['ema50'].iloc[-1] and df['ema20'].iloc[-1] > df['ema50'].iloc[-1]:
        return "Bullish"
    elif df['close'].iloc[-1] < df['ema50'].iloc[-1] and df['ema20'].iloc[-1] < df['ema50'].iloc[-1]:
        return "Bearish"
    else:
        return "Neutral"
