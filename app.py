import streamlit as st
import pandas as pd
import yfinance as yf
from breakout_scanner import calculate_technical_indicators, generate_signals, assess_market_condition
from datetime import datetime

# ตั้งค่าหน้าเว็บ
st.set_page_config(page_title="Breakout Auto ETF Scanner", layout="wide")
st.markdown("## 📈 Breakout Auto ETF Scanner (YFinance Edition)")
st.caption("Powered by มาบอย 🐃🔥")

# 📌 Filter ตัวเลือก ETF และ Market
tickers = ['YINN', 'FNGU', 'SOXL', 'FXI', 'EURL', 'TNA', 'GDXU']
market_etfs = ['SPY', 'QQQ', 'DIA']
use_filter = st.sidebar.checkbox("☁️ ใช้ Market Filter จาก ETF:", value=True)
market_etf = st.sidebar.selectbox("เลือก ETF ตลาด", market_etfs)

# ✅ ดึงข้อมูล Market Filter (SPY/QQQ/อื่น ๆ)
if use_filter:
    try:
        market_df = yf.download(market_etf, period='3mo', interval='1d', progress=False)
        market_df = market_df[['Open', 'High', 'Low', 'Close', 'Volume']].dropna()
        market_df.reset_index(inplace=True)
        market_df['Date'] = pd.to_datetime(market_df['Date'])
        market_df = calculate_technical_indicators(market_df)
        market_status = assess_market_condition(market_df)
    except Exception as e:
        market_status = "Unknown"
        st.warning("⚠️ ไม่สามารถประเมินสภาพตลาดได้")
else:
    market_status = "Bullish"  # ถ้าไม่ใช้ Market Filter ให้ถือว่าเป็น Bullish

# ✅ แสดง Market Status
st.sidebar.subheader("📈 Market Filter")
st.sidebar.markdown(f"**Market Status ({market_etf}):** `{market_status}`")

# ✅ ดึงข้อมูล ETF ที่เลือก
selected_etf = st.selectbox("เลือก ETF ที่ต้องการสแกน", tickers)
try:
    df = yf.download(selected_etf, period='3mo', interval='1d', progress=False)
    df = df[['Open', 'High', 'Low', 'Close', 'Volume']].dropna()
    df.reset_index(inplace=True)
    df['Date'] = pd.to_datetime(df['Date'])
except Exception as e:
    st.error(f"❌ โหลดข้อมูล {selected_etf} ไม่สำเร็จ: {e}")
    st.stop()

# ✅ คำนวณอินดิเคเตอร์ + สัญญาณ
try:
    df = calculate_technical_indicators(df)
    df = generate_signals(df, market_status)
except Exception as e:
    st.error(f"❌ สร้างสัญญาณไม่สำเร็จ: {e}")
    st.stop()

# ✅ แสดงผลสัญญาณล่าสุด
try:
    latest = df.iloc[-1]
    latest_date = latest['Date'].strftime('%Y-%m-%d') if isinstance(latest['Date'], (pd.Timestamp, datetime)) else "ไม่พบวันที่"
    signal = str(latest['Signal'])
    rsi = float(latest['Rsi'])
    macd = float(latest['Macd'])
    ema20 = float(latest['Ema20'])

    st.markdown(f"### 🧠 สัญญาณล่าสุด: `{selected_etf}`")
    st.markdown(f"- 📅 วันที่: `{latest_date}`")
    st.markdown(f"- 📊 สัญญาณ: **{signal}**")
    st.markdown(f"- RSI: `{rsi:.2f}`")
    st.markdown(f"- MACD: `{macd:.2f}`")
    st.markdown(f"- EMA20: `{ema20:.2f}`")
except Exception as e:
    st.error("❌ แสดงสัญญาณล่าสุดไม่สำเร็จ")

# ✅ ตารางย้อนหลัง
with st.expander("🔍 ข้อมูลย้อนหลัง"):
    st.dataframe(df.tail(30), use_container_width=True)
