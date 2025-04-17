import streamlit as st
import pandas as pd
import yfinance as yf
from breakout_scanner import calculate_technical_indicators, generate_signals, assess_market_condition

# ตั้งค่าหน้าเว็บ
st.set_page_config(page_title="Breakout Auto ETF Scanner", layout="wide")
st.markdown("## 📈 Breakout Auto ETF Scanner (YFinance Edition)")
st.caption("Powered by มาบอย 🐃🔥")

# ============================
# Sidebar: Market Filter
# ============================
st.sidebar.markdown("### 🧭 ใช้ Market Filter จาก ETF:")
market_etfs = ['SPY', 'QQQ', 'DIA']
market_etf = st.sidebar.selectbox("เลือก ETF ตลาด", market_etfs)

try:
    market_df = yf.download(market_etf, period='3mo', interval='1d', progress=False)
    market_df = market_df[['Open', 'High', 'Low', 'Close', 'Volume']].dropna()
    market_df.reset_index(inplace=True)
    market_df['Date'] = pd.to_datetime(market_df['Date'])
    market_df = calculate_technical_indicators(market_df)
    market_status = assess_market_condition(market_df)
except Exception as e:
    market_status = "Unknown"
    st.sidebar.warning("⚠️ ไม่สามารถประเมินสภาพตลาดได้")

st.sidebar.subheader("📈 Market Filter")
st.sidebar.markdown(f"**Market Status ({market_etf}):** `{market_status}`")

# ============================
# Main: เลือก ETF ที่ต้องการดู
# ============================
tickers = ['YINN', 'FNGU', 'SOXL', 'FXI', 'EURL', 'TNA', 'GDXU']
selected_etf = st.selectbox("เลือก ETF ที่ต้องการสแกน", tickers)

try:
    df = yf.download(selected_etf, period='3mo', interval='1d', progress=False)
    df = df[['Open', 'High', 'Low', 'Close', 'Volume']].dropna()
    df.reset_index(inplace=True)
    df['Date'] = pd.to_datetime(df['Date'])
except Exception as e:
    st.error(f"❌ โหลดข้อมูลไม่สำเร็จ: {e}")
    st.stop()

# ============================
# คำนวณอินดิเคเตอร์และสร้างสัญญาณ
# ============================
try:
    df = calculate_technical_indicators(df)
    df = generate_signals(df, market_status)
except Exception as e:
    st.error(f"❌ คำนวณอินดิเคเตอร์ไม่สำเร็จ: {e}")
    st.stop()

# ============================
# แสดงผลสัญญาณล่าสุด
# ============================
latest = df.iloc[-1]

st.markdown(f"### 🧠 สัญญาณล่าสุด: `{selected_etf}`")

# เช็กว่า latest['Date'] มีค่าหรือไม่
if 'Date' in latest and pd.notnull(latest['Date']):
    st.markdown(f"- 📅 วันที่: `{latest['Date'].date()}`")
else:
    st.markdown("- 📅 วันที่: `ไม่พบวันที่`")

# แสดงผลสัญญาณแบบปลอดภัย
signal = str(latest['Signal']) if 'Signal' in latest else 'N/A'
rsi = float(latest['Rsi']) if 'Rsi' in latest and pd.notnull(latest['Rsi']) else 0
macd = float(latest['Macd']) if 'Macd' in latest and pd.notnull(latest['Macd']) else 0
ema20 = float(latest['Ema20']) if 'Ema20' in latest and pd.notnull(latest['Ema20']) else 0

st.markdown(f"- 📊 สัญญาณ: **{signal}**")
st.markdown(f"- RSI: `{rsi:.2f}`")
st.markdown(f"- MACD: `{macd:.2f}`")
st.markdown(f"- EMA20: `{ema20:.2f}`")

# ============================
# ตารางย้อนหลัง
# ============================
with st.expander("🔍 ข้อมูลย้อนหลัง"):
    st.dataframe(df.tail(30), use_container_width=True)

