import streamlit as st
import pandas as pd
import yfinance as yf
from breakout_scanner import calculate_technical_indicators, generate_signals, assess_market_condition

st.set_page_config(page_title="Breakout Auto ETF Scanner", layout="wide")

st.markdown("## 📈 Breakout Auto ETF Scanner (YFinance Edition)")
st.caption("Powered by มาบอย 🐃🔥")

tickers = ['YINN', 'FNGU', 'SOXL', 'FXI', 'EURL', 'TNA', 'GDXU']
selected_etf = st.selectbox("เลือก ETF", tickers)

# ✅ ประเมิน Market Status จาก SPY
try:
    market_df = yf.download('SPY', period='3mo', interval='1d', progress=False)
    market_df = market_df[['Open', 'High', 'Low', 'Close', 'Volume']].dropna()
    market_df.reset_index(inplace=True)
    market_df.columns.name = None
    market_df['Date'] = pd.to_datetime(market_df['Date'])
    market_df = calculate_technical_indicators(market_df)

    # 🔍 Debug: แสดง DataFrame ล่าสุดของตลาด
    st.subheader("🔍 Debug: Market Data (SPY)")
    st.dataframe(market_df.tail(3))

    market_status = assess_market_condition(market_df)
except Exception as e:
    market_status = "Unknown"
    st.warning("⚠️ ไม่สามารถประเมินสภาพตลาดได้")

# ✅ แสดงสถานะตลาดใน Sidebar
st.sidebar.subheader("📈 Market Filter")
st.sidebar.markdown(f"**Market Status (SPY):** `{market_status}`")

# ✅ ดึงข้อมูล ETF ที่เลือก
try:
    df = yf.download(selected_etf, period='3mo', interval='1d', progress=False)
    df = df[['Open', 'High', 'Low', 'Close', 'Volume']].dropna()
    df.reset_index(inplace=True)
    df.columns.name = None
    df['Date'] = pd.to_datetime(df['Date'])
except Exception as e:
    st.error(f"❌ โหลดข้อมูลไม่สำเร็จ: {e}")
    st.stop()

# ✅ คำนวณอินดิเคเตอร์ และ สร้างสัญญาณ
try:
    df = calculate_technical_indicators(df)
    df = generate_signals(df, market_status)
except Exception as e:
    st.error(f"❌ คำนวณอินดิเคเตอร์ไม่สำเร็จ: {e}")
    st.stop()

# ✅ แสดงผลสัญญาณล่าสุด
latest = df.iloc[-1:]

st.markdown(f"### 🧠 สัญญาณล่าสุด: `{selected_etf}`")
st.markdown(f"- 📅 วันที่: `{latest['Date'].iloc[0].date()}`")
st.markdown(f"- 📊 สัญญาณ: **{latest['Signal'].iloc[0]}**")
st.markdown(f"- RSI: `{latest['Rsi'].iloc
