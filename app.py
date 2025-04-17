import streamlit as st
import pandas as pd
import yfinance as yf
from breakout_scanner import calculate_technical_indicators, generate_signals, assess_market_condition

st.set_page_config(page_title="Breakout Auto ETF Scanner", layout="wide")
st.markdown("## 📈 Breakout Auto ETF Scanner (YFinance Edition)")
st.caption("Powered by มาบอย 🐃🔥")

# ====== Market Filter Options ======
market_etfs = ['SPY', 'QQQ', 'DIA']
selected_market = st.sidebar.selectbox("🧠 ใช้ Market Filter จาก ETF:", market_etfs)

# ====== Main ETF Selection ======
tickers = ['YINN', 'FNGU', 'SOXL', 'FXI', 'EURL', 'TNA', 'GDXU']
selected_etf = st.selectbox("เลือก ETF ที่ต้องการสแกน", tickers)

# ====== Load Market Data ======
try:
    market_df = yf.download(selected_market, period='3mo', interval='1d', progress=False)
    market_df = market_df[['Open', 'High', 'Low', 'Close', 'Volume']].dropna()
    market_df.reset_index(inplace=True)
    market_df['Date'] = pd.to_datetime(market_df['Date'])
    market_df = calculate_technical_indicators(market_df)
    market_status = assess_market_condition(market_df)
except Exception as e:
    market_status = "Unknown"
    st.sidebar.warning("\u26a0\ufe0f ไม่สามารถสภาพตลาดได้")

st.sidebar.subheader("📉 Market Filter")
st.sidebar.markdown(f"**Market Status ({selected_market}):** `{market_status}`")

# ====== Load Selected ETF Data ======
try:
    df = yf.download(selected_etf, period='3mo', interval='1d', progress=False)
    df = df[['Open', 'High', 'Low', 'Close', 'Volume']].dropna()
    df.reset_index(inplace=True)
    df['Date'] = pd.to_datetime(df['Date'])
except Exception as e:
    st.error(f"❌ โหลดข้อมูลไม่สำเร็จ: {e}")
    st.stop()

# ====== Indicators and Signals ======
try:
    df = calculate_technical_indicators(df)
    df = generate_signals(df, market_status)
except Exception as e:
    st.error(f"❌ คำนวณอินดิเคเตอร์ไม่สำเร็จ: {e}")
    st.stop()

# ====== Latest Signal ======
try:
    latest = df.iloc[-1]
    latest_date = pd.to_datetime(latest['Date']).date() if pd.notnull(latest['Date']) else "ไม่พบวันที่"
    st.markdown(f"### 🧠 สัญญาณล่าสุด: `{selected_etf}`")
    st.markdown(f"- 🗓️ วันที่: `{latest_date}`")
    st.markdown(f"- 📊 สัญญาณ: **{latest['Signal']}**")
    st.markdown(f"- RSI: `{float(latest['Rsi']):.2f}`")
    st.markdown(f"- MACD: `{float(latest['Macd']):.2f}`")
    st.markdown(f"- EMA20: `{float(latest['Ema20']):.2f}`")
except Exception as e:
    st.error(f"❌ แสดงสัญญาณล่าสุดไม่สำเร็จ: {e}")

# ====== Historical Data Table ======
with st.expander("🔍 ข้อมูลย้อนหลัง"):
    st.dataframe(df.tail(30), use_container_width=True)

