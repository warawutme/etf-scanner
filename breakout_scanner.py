import yfinance as yf
import pandas as pd

def fetch_etf_data(ticker):
    """
    ดึงข้อมูล ETF จาก Yahoo Finance ผ่าน yfinance
    """
    df = yf.download(ticker, period="6mo", interval="1d", progress=False)
    df = df.rename(columns={
        'Open': 'open',
        'High': 'high',
        'Low': 'low',
        'Close': 'close',
        'Volume': 'volume'
    })
    df = df[['open', 'high', 'low', 'close', 'volume']]
    return df

def calculate_technical_indicators(df):
    """
    คำนวณอินดิเคเตอร์พื้นฐานที่ใช้ในระบบ Breakout
    """
    df['ema20'] = df['close'].ewm(span=20).mean()
    df['ema50'] = df['close'].ewm(span=50).mean()

    delta = df['close'].diff()
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)
    avg_gain = gain.rolling(14).mean()
    avg_loss = loss.rolling(14).mean()
    rs = avg_gain / avg_loss
    df['rsi'] = 100 - (100 / (1 + rs))

    df['ema12'] = df['close'].ewm(span=12).mean()
    df['ema26'] = df['close'].ewm(span=26).mean()
    df['macd'] = df['ema12'] - df['ema26']
    df['signal_line'] = df['macd'].ewm(span=9).mean()
    df['macd_histogram'] = df['macd'] - df['signal_line']

    df['sma20'] = df['close'].rolling(20).mean()
    df['std20'] = df['close'].rolling(20).std()
    df['upper_band'] = df['sma20'] + 2 * df['std20']
    df['lower_band'] = df['sma20'] - 2 * df['std20']

    df['high_20d'] = df['high'].rolling(20).max()
    df['volume_sma50'] = df['volume'].rolling(50).mean()
    df['volume_ratio'] = df['volume'] / df['volume_sma50']
    df['breakout'] = (df['close'] > df['high_20d'].shift(1)) & (df['volume_ratio'] > 1.2)

    return df

def generate_signals(df, market_status="Bullish"):
    df['signal'] = 'HOLD'

    buy = (
        df['breakout'] &
        (df['rsi'] >= 40) & (df['rsi'] <= 70) &
        (df['macd'] > df['signal_line']) &
        (df['volume_ratio'] > 1.2) &
        (df['close'] > df['ema20']) &
        (market_status != 'Bearish')
    )

    sell = (
        (df['close'] < df['ema20']) &
        (df['macd'] < df['signal_line']) &
        ((df['rsi'] < 40) | (df['close'] < df['lower_band']))
    )

    df.loc[buy, 'signal'] = 'BUY'
    df.loc[sell, 'signal'] = 'SELL'

    df['atr'] = df['high'].rolling(14).max() - df['low'].rolling(14).min()
    df['stop_loss'] = df['close'] - 2 * df['atr']
    df['take_profit'] = df['close'] + 3 * df['atr']
    df['risk'] = abs(df['close'] - df['stop_loss'])
    df['reward'] = abs(df['take_profit'] - df['close'])
    df['rr'] = df['reward'] / df['risk']
    df.loc[df['rr'] < 1.5, 'signal'] = 'HOLD'

    return df

def assess_market_condition(df):
    """
    ประเมินแนวโน้มตลาดจาก EMA และ RSI
    """
    if len(df) < 50:
        return "Neutral"

    df = calculate_technical_indicators(df)

    if df['close'].iloc[-1] > df['ema50'].iloc[-1] and df['ema20'].iloc[-1] > df['ema50'].iloc[-1]:
        return "Bullish"
    elif df['close'].iloc[-1] < df['ema50'].iloc[-1] and df['ema20'].iloc[-1] < df['ema50'].iloc[-1]:
        return "Bearish"
    else:
        return "Neutral"
