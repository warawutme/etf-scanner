import streamlit as st
import pandas as pd
import yfinance as yf
from breakout_scanner import calculate_technical_indicators, generate_signals, assess_market_condition

# ตั้งค่าหน้าเว็บ
st.set_page_config(page_title="Breakout Auto ETF Scanner", layout="wide")
st.markdown("## 📈 Breakout Auto ETF Scanner (YFinance Edition)")
st.caption("Powered by มาบอย 🐃🔥")

# 🧠 เลือก Market Filter ETF
use_market_filter = st.sidebar.checkbox("☁️ ใช้ Market Filter จาก ETF:", value=True)
market_etf = st.sidebar.selectbox("เลือก ETF ตลาด", ["SPY", "QQQ", "DIA"])

# ✅ เลือก ETF ที่ต้องการสแกน
tickers = ['YINN', 'FNGU', 'SOXL', 'FXI', 'EURL', 'TNA', 'GDXU']
selected_etf = st.selectbox("เลือก ETF ที่ต้องการสแกน", tickers)

# ✅ โหลดข้อมูล ETF ตลาด
if use_market_filter:
    try:
        market_df = yf.download(market_etf, period='3mo', interval='1d', progress=False)
        market_df = market_df[['Open', 'High', 'Low', 'Close', 'Volume']].dropna()
        market_df.reset_index(inplace=True)
        market_df.columns.name = None
        market_df['Date'] = pd.to_datetime(market_df['Date'])
        market_df = calculate_technical_indicators(market_df)
        market_status = assess_market_condition(market_df)
    except Exception as e:
        market_status = "Unknown"
        st.warning(f"⚠️ ไม่สามารถประเมินตลาดจาก {market_etf} ได้: {e}")
else:
    market_status = "Bullish"

# ✅ แสดงสถานะตลาด
st.sidebar.subheader("📉 Market Filter")
st.sidebar.markdown(f"**Market Status ({market_etf}):** `{market_status}`")

# ✅ โหลดข้อมูล ETF ที่เลือก
try:
    df = yf.download(selected_etf, period='3mo', interval='1d', progress=False)
    df = df[['Open', 'High', 'Low', 'Close', 'Volume']].dropna()
    df.reset_index(inplace=True)
    df.columns.name = None
    df['Date'] = pd.to_datetime(df['Date'])
except Exception as e:
    st.error(f"❌ โหลดข้อมูล {selected_etf} ไม่สำเร็จ: {e}")
    st.stop()

# ✅ คำนวณอินดิเคเตอร์ และ สร้างสัญญาณ
try:
    df = calculate_technical_indicators(df)
    df = generate_signals(df, market_status)
except Exception as e:
    st.error(f"❌ คำนวณอินดิเคเตอร์ไม่สำเร็จ: {e}")
    st.stop()

# ✅ แสดงผลสัญญาณล่าสุด
latest = df.iloc[-1]
try:
    latest_date = pd.to_datetime(latest['Date'])
    latest_date_str = latest_date.strftime('%Y-%m-%d') if not pd.isnull(latest_date) else "ไม่พบวันที่"
except Exception:
    latest_date_str = "ไม่พบวันที่"

st.markdown(f"### 🧠 สัญญาณล่าสุด: `{selected_etf}`")
st.markdown(f"- 📅 วันที่: `{latest_date_str}`")
st.markdown(f"- 📊 สัญญาณ: **{latest['Signal']}**")
st.markdown(f"- RSI: `{float(latest['Rsi']):.2f}`")
st.markdown(f"- MACD: `{float(latest['Macd']):.2f}`")
st.markdown(f"- EMA20: `{float(latest['Ema20']):.2f}`")

# ✅ ข้อมูลย้อนหลัง
with st.expander("🔍 ข้อมูลย้อนหลัง"):
    st.dataframe(df.tail(30), use_container_width=True)
