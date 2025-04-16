import yfinance as yf
import pandas as pd

def fetch_etf_data(ticker):
    try:
        df = yf.download(ticker, period="6mo", interval="1d")
        df = df.reset_index()
        df.columns = df.columns.str.capitalize()  # Ensure consistent column names
        return df
    except Exception as e:
        print(f"Error fetching {ticker}: {e}")
        return pd.DataFrame()

def calculate_technical_indicators(df):
    df['Ema20'] = df['Close'].ewm(span=20, adjust=False).mean()
    df['Ema50'] = df['Close'].ewm(span=50, adjust=False).mean()
    df['Rsi'] = compute_rsi(df['Close'], 14)
    df['Macd'] = df['Close'].ewm(span=12, adjust=False).mean() - df['Close'].ewm(span=26, adjust=False).mean()
    return df

def compute_rsi(series, period):
    delta = series.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

def generate_signals(df):
    df['Signal'] = 'HOLD'
    df.loc[(df['Close'] > df['Ema20']) & (df['Rsi'] > 55) & (df['Macd'] > 0), 'Signal'] = 'BUY'
    df.loc[(df['Close'] < df['Ema20']) & (df['Rsi'] < 45) & (df['Macd'] < 0), 'Signal'] = 'SELL'
    return df

def get_latest_signal(df):
    latest_row = df.iloc[-1]
    return {
        'Date': latest_row['Date'].strftime('%Y-%m-%d') if 'Date' in latest_row else '-',
        'Close': round(latest_row['Close'], 2),
        'Signal': latest_row['Signal'],
        'RSI': round(latest_row['Rsi'], 2),
        'MACD': round(latest_row['Macd'], 2),
    }
