import streamlit as st
import pandas as pd
import yfinance as yf
from breakout_scanner import calculate_technical_indicators, generate_signals, assess_market_condition

# ====== ตั้งค่าหน้าเว็บ ======
st.set_page_config(page_title="Breakout Auto ETF Scanner", layout="wide")
st.markdown("## 📈 Breakout Auto ETF Scanner (YFinance Edition)")
st.caption("Powered by มาบอย 🐃🔥")

# ====== รายชื่อ ETF และ Market Filter ให้เลือก ======
tickers = ['YINN', 'FNGU', 'SOXL', 'FXI', 'EURL', 'TNA', 'GDXU']
market_filters = ['SPY', 'QQQ']

selected_etf = st.selectbox("เลือก ETF ที่ต้องการสแกน", tickers)
selected_market = st.sidebar.selectbox("🔍 ใช้ Market Filter จาก ETF:", market_filters)

# ====== ดึงข้อมูลตลาด (SPY / QQQ) ======
try:
    market_df = yf.download(selected_market, period='3mo', interval='1d', progress=False)
    market_df = market_df[['Close']].dropna()
    market_df = calculate_technical_indicators(market_df)
    market_status = assess_market_condition(market_df)
except Exception as e:
    market_status = "Unknown"
    st.sidebar.warning(f"⚠️ ไม่สามารถประเมินตลาดจาก {selected_market}")

# ====== แสดงสถานะตลาดใน Sidebar ======
st.sidebar.subheader("📈 Market Filter")
st.sidebar.markdown(f"**Market Status ({selected_market}):** `{market_status}`")

# ====== ดึงข้อมูล ETF ======
try:
    df = yf.download(selected_etf, period='3mo', interval='1d', progress=False)
    df.reset_index(inplace=True)
    df = df[['Date', 'Open', 'High', 'Low', 'Close', 'Volume']]
    df['Date'] = pd.to_datetime(df['Date'])
except Exception as e:
    st.error(f"❌ โหลดข้อมูล ETF ไม่สำเร็จ: {e}")
    st.stop()

# ====== คำนวณอินดิเคเตอร์ + สัญญาณ ======
try:
    df = calculate_technical_indicators(df)
    df = generate_signals(df, market_status)
except Exception as e:
    st.error(f"❌ คำนวณอินดิเคเตอร์ไม่สำเร็จ: {e}")
    st.stop()

# ====== แสดงผลล่าสุด ======
latest = df.iloc[-1] if not df.empty else None

if latest is not None:
    st.markdown(f"### 🧠 สัญญาณล่าสุด: `{selected_etf}`")
    st.markdown(f"- 📅 วันที่: `{latest['Date'].date() if pd.notnull(latest['Date']) else 'ไม่พบวันที่'}`")
    st.markdown(f"- 📊 สัญญาณ: **{latest['Signal']}**")
    st.markdown(f"- RSI: `{float(latest['Rsi']):.2f}`")
    st.markdown(f"- MACD: `{float(latest['Macd']):.2f}`")
    st.markdown(f"- EMA20: `{float(latest['Ema20']):.2f}`")
else:
    st.warning("ไม่พบข้อมูลล่าสุด")

# ====== ตารางย้อนหลัง ======
with st.expander("🔍 ข้อมูลย้อนหลัง"):
    st.dataframe(df.tail(30), use_container_width=True)
