# breakout_scanner.py (เวอร์ชันแก้ bug 'close')

import requests
import pandas as pd
import numpy as np

def fetch_etf_data(ticker, api_key, outputsize='compact'):
    url = f'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={ticker}&outputsize={outputsize}&apikey={api_key}'
    response = requests.get(url)
    data = response.json()

    if 'Time Series (Daily)' in data:
        df = pd.DataFrame(data['Time Series (Daily)']).T
        df.columns = ['open', 'high', 'low', 'close', 'volume']
        df = df.apply(pd.to_numeric)
        df.index = pd.to_datetime(df.index)
        df = df.sort_index()
        return df
    else:
        # คืน DataFrame ว่าง (ป้องกัน crash)
        return pd.DataFrame(columns=['open', 'high', 'low', 'close', 'volume'])

def calculate_technical_indicators(df):
    df['ema20'] = df['close'].ewm(span=20, adjust=False).mean()
    df['ema50'] = df['close'].ewm(span=50, adjust=False).mean()
    df['tr1'] = abs(df['high'] - df['low'])
    df['tr2'] = abs(df['high'] - df['close'].shift())
    df['tr3'] = abs(df['low'] - df['close'].shift())
    df['tr'] = df[['tr1', 'tr2', 'tr3']].max(axis=1)
    df['atr'] = df['tr'].rolling(window=14).mean()
    return df

def assess_market_condition(df):
    close = df['close'].iloc[-1]
    ema20 = df['ema20'].iloc[-1]
    ema50 = df['ema50'].iloc[-1]
    if close > ema50 and ema20 > ema50:
        return "Bullish"
    elif close < ema50 and ema20 < ema50:
        return "Bearish"
    else:
        return "Neutral"

def generate_signals(df, market_condition):
    df['signal'] = 'HOLD'
    buy_cond = (df['close'] > df['ema20']) & (market_condition == 'Bullish')
    sell_cond = (df['close'] < df['ema20']) & (market_condition in ['Bearish', 'Neutral'])
    df.loc[buy_cond, 'signal'] = 'BUY'
    df.loc[sell_cond, 'signal'] = 'SELL'
    df['stop_loss'] = df['close'] - (2 * df['atr'])
    df['take_profit'] = df['close'] + (3 * df['atr'])
    df['rr'] = abs(df['take_profit'] - df['close']) / abs(df['close'] - df['stop_loss'])
    return df
