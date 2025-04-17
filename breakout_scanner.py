# ✅ breakout_scanner.py (รุ่นจำลองที่รันได้แน่นอน)
import pandas as pd
import yfinance as yf

def fetch_etf_data(ticker: str) -> pd.DataFrame:
    try:
        df = yf.download(ticker, period="3mo", interval="1d", progress=False)
        if df.empty:
            return pd.DataFrame()
        return df[['Close']].dropna()
    except:
        return pd.DataFrame()

def calculate_technical_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df['Ema20'] = df['Close'].ewm(span=20, adjust=False).mean()
    df['Ema50'] = df['Close'].ewm(span=50, adjust=False).mean()
    delta = df['Close'].diff()
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)
    avg_gain = gain.rolling(14).mean()
    avg_loss = loss.rolling(14).mean()
    rs = avg_gain / avg_loss
    df['Rsi'] = 100 - (100 / (1 + rs))
    ema12 = df['Close'].ewm(span=12, adjust=False).mean()
    ema26 = df['Close'].ewm(span=26, adjust=False).mean()
    df['Macd'] = ema12 - ema26
    return df.fillna(0)

def generate_signals(df: pd.DataFrame, market_status: str = "Bullish") -> pd.DataFrame:
    df = df.copy()
    df = df.fillna(0)
    df['Signal'] = 'HOLD'

    # ปรับวิธีคำนวณโดยใช้ pandas Series โดยตรง (index alignment OK)
    buy_condition = (
        (df['Close'] > df['Ema20']) &
        (df['Rsi'] > 55) &
        (df['Macd'] > 0) &
        (market_status != 'Bearish')
    )
    sell_condition = (
        (df['Close'] < df['Ema20']) &
        (df['Rsi'] < 45) &
        (df['Macd'] < 0)
    )
    df.loc[buy_condition, 'Signal'] = 'BUY'
    df.loc[sell_condition, 'Signal'] = 'SELL'
    return df

def assess_market_condition(df: pd.DataFrame) -> str:
    if df.empty or len(df) < 20:
        return "Unknown"
    df = df.fillna(0)
    latest = df.iloc[-1]
    cond = sum([
        latest['Rsi'] > 55,
        latest['Ema20'] > latest['Ema50'],
        latest['Macd'] > 0
    ])
    if cond >= 2:
        return "Bullish"
    elif cond == 1:
        return "Neutral"
    else:
        return "Bearish"
