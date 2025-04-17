# app.py
import streamlit as st
import pandas as pd
from breakout_scanner import (
    fetch_etf_data,
    calculate_technical_indicators,
    generate_signals,
    assess_market_condition,
)

st.set_page_config(page_title="Breakout Auto ETF Scanner", layout="wide")
st.title("\U0001F4C8 Breakout Auto ETF Scanner (YFinance Edition)")
st.caption("Powered by มาบอย 🐃🔥")

# Market Filter
st.sidebar.subheader("☁️ ใช้ Market Filter จาก ETF")
market_choice = st.sidebar.selectbox("เลือก ETF ตลาด", ["SPY", "QQQ"])
market_df = fetch_etf_data(market_choice)
if market_df.empty:
    market_status = "Unknown"
    st.sidebar.error(f"⚠️ โหลดข้อมูล {market_choice} ไม่สำเร็จ")
else:
    market_df = calculate_technical_indicators(market_df)
    market_status = assess_market_condition(market_df)

st.sidebar.markdown(f"**Market Status ({market_choice}):** `{market_status}`")

# Main Scanner
st.subheader("เลือก ETF ที่ต้องการสแกน")
ticker_list = ["YINN", "FNGU", "SOXL", "FXI", "EURL", "TNA", "GDXU"]
selected_etf = st.selectbox("ETF Scanner", ticker_list)

df = fetch_etf_data(selected_etf)
if df.empty:
    st.error(f"❌ โหลดข้อมูล {selected_etf} ไม่สำเร็จ")
    st.stop()

df = calculate_technical_indicators(df)
df = generate_signals(df, market_status)

if df.empty or "Signal" not in df.columns:
    st.error("❌ ข้อมูลไม่สมบูรณ์ ไม่สามารถแสดงผลได้")
    st.stop()

latest = df.iloc[-1]
latest_ts = df.index[-1]

date_str = latest_ts.strftime("%Y-%m-%d")
signal = latest["Signal"]
rsi_val = latest["Rsi"]
macd_val = latest["Macd"]
ema20_val = latest["Ema20"]

st.markdown(f"### 🧠 สัญญาณล่าสุด: `{selected_etf}`")
st.markdown(f"- 📅 วันที่: `{date_str}`")
if signal == "BUY":
    st.success(f"- 📊 สัญญาณ: **{signal}**")
elif signal == "SELL":
    st.error(f"- 📊 สัญญาณ: **{signal}**")
else:
    st.info(f"- 📊 สัญญาณ: **{signal}**")

st.markdown(f"- RSI: `{rsi_val:.2f}`")
st.markdown(f"- MACD: `{macd_val:.2f}`")
st.markdown(f"- EMA20: `{ema20_val:.2f}`")

with st.expander("🔍 ข้อมูลย้อนหลัง"):
    st.dataframe(df.tail(30), use_container_width=True)
