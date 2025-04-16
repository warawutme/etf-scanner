import streamlit as st
import pandas as pd
from breakout_scanner import calculate_technical_indicators, generate_signals
import yfinance as yf

st.set_page_config(page_title="Breakout Auto ETF Scanner", layout="wide")

st.markdown("## 📈 Breakout Auto ETF Scanner (YFinance Edition)")
st.caption("Powered by มาบอย 🐃🔥")

tickers = ['YINN', 'FNGU', 'SOXL', 'FXI', 'EURL', 'TNA', 'GDXU']  # กำหนด ETF ที่รองรับ

selected_etf = st.selectbox("เลือก ETF", tickers)

# ดึงข้อมูลจาก yfinance
try:
    df = yf.download(selected_etf, period='3mo', interval='1d', progress=False)
    df = df[['Open', 'High', 'Low', 'Close', 'Volume']].dropna()
    df.reset_index(inplace=True)
    df.columns.name = None
    df['Date'] = pd.to_datetime(df['Date'])
except Exception as e:
    st.error(f"โหลดข้อมูลไม่สำเร็จ: {e}")
    st.stop()

# คำนวณอินดิเคเตอร์
try:
    df = calculate_technical_indicators(df)
    df = generate_signals(df)
except Exception as e:
    st.error(f"❌ คำนวณอินดิเคเตอร์ไม่สำเร็จ: {e}")
    st.stop()

# แสดงผล
latest = df.iloc[-1:]

st.markdown(f"### 🧠 สัญญาณล่าสุด: `{selected_etf}`")
st.markdown(f"- 📅 วันที่: `{latest['Date'].iloc[0].date()}`")
st.markdown(f"- 📊 สัญญาณ: **{latest['Signal'].values[0]}**")
st.markdown(f"- RSI: `{latest['Rsi'].values[0]:.2f}`")
st.markdown(f"- MACD: `{latest['Macd'].values[0]:.2f}`")
st.markdown(f"- EMA20: `{latest['Ema20'].values[0]:.2f}`")

# แสดงตารางย้อนหลัง
with st.expander("🔍 ข้อมูลย้อนหลัง"):
    st.dataframe(df.tail(30), use_container_width=True)
