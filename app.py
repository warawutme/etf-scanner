import streamlit as st
import pandas as pd
import yfinance as yf
from breakout_scanner import calculate_technical_indicators, generate_signals, assess_market_condition

st.set_page_config(page_title="Breakout Auto ETF Scanner", layout="wide")
st.markdown("## 📈 Breakout Auto ETF Scanner (YFinance Edition)")
st.caption("Powered by มาบอย 🐃🔥")

# ===========================
# ตั้งค่า ETF และ Market Filter
# ===========================
tickers = ['YINN', 'FNGU', 'SOXL', 'FXI', 'EURL', 'TNA', 'GDXU']
market_etfs = ['SPY', 'QQQ', 'DIA']

st.sidebar.markdown("### ☁️ ใช้ Market Filter จาก ETF:")
selected_market_etf = st.sidebar.selectbox("เลือก ETF ตลาด", market_etfs)
st.sidebar.subheader(":chart_with_upwards_trend: Market Filter")

# ===========================
# ดึงข้อม Market ETF และเปรียบ
# ===========================
try:
    market_df = yf.download(selected_market_etf, period='3mo', interval='1d', progress=False)
    market_df = market_df[['Open', 'High', 'Low', 'Close', 'Volume']].dropna()
    market_df.reset_index(inplace=True)
    market_df['Date'] = pd.to_datetime(market_df['Date'])
    market_df = calculate_technical_indicators(market_df)
    market_status = assess_market_condition(market_df)
except Exception as e:
    market_status = "Unknown"
    st.sidebar.warning(":warning: ไม่สามารถสภาพตลาดได้")

st.sidebar.markdown(f"**Market Status ({selected_market_etf}):** `{market_status}`")

# ===========================
# เลือก ETF ที่ต้องการสแกน
# ===========================
selected_etf = st.selectbox("เลือก ETF ที่ต้องการสแกน", tickers)

try:
    df = yf.download(selected_etf, period='3mo', interval='1d', progress=False)
    df = df[['Open', 'High', 'Low', 'Close', 'Volume']].dropna()
    df.reset_index(inplace=True)
    df['Date'] = pd.to_datetime(df['Date'])
except Exception as e:
    st.error(f"❌ โหลดข้อมูลไม่สำเร็จ: {e}")
    st.stop()

# ===========================
# คำนวณอินดิเคเตอร์ + สัญญาณ
# ===========================
try:
    df = calculate_technical_indicators(df)
    df = generate_signals(df, market_status)
except Exception as e:
    st.error(f"❌ คำนวณอินดิเคตอร์ไม่สำเร็จ: {e}")
    st.stop()

# ===========================
# แสดงสัญญาณล่าสุด
# ===========================
latest = df.iloc[-1]

# ตรวจสอบและแสดงวันที่
try:
    latest_date = latest['Date'].date() if pd.notnull(latest['Date']) else "ไม่พบวันที่"
except Exception:
    latest_date = "ไม่พบวันที่"

# ตรวจสอบและแสดงสัญญาณ
try:
    latest_signal = str(latest['Signal']) if pd.notnull(latest['Signal']) else "Unknown"
except Exception:
    latest_signal = "Unknown"

st.markdown(f"### 🧠 สัญญาณล่าสุด: `{selected_etf}`")
st.markdown(f"- 🗓️ วันที่: `{latest_date}`")
st.markdown(f"- 📊 สัญญาณ: **{latest_signal}**")
st.markdown(f"- RSI: `{latest['Rsi']:.2f}`")
st.markdown(f"- MACD: `{latest['Macd']:.2f}`")
st.markdown(f"- EMA20: `{latest['Ema20']:.2f}`")

# ===========================
# แสดงตารางย้อนหลัง
# ===========================
with st.expander("🔍 ข้อมูลย้อนหลัง"):
    st.dataframe(df.tail(30), use_container_width=True)
