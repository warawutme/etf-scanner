import streamlit as st
import pandas as pd
from breakout_scanner import (
    fetch_etf_data,
    calculate_technical_indicators,
    generate_signals
)

st.set_page_config(page_title="Breakout Auto ETF Scanner", layout="wide")

st.title("📈 Breakout Auto ETF Scanner (YFinance Edition)")
st.caption("Powered by มาบอย 🐃🔥")

# รายชื่อ ETF ที่ใช้ได้ (ยกเว้นตัวที่ดึงข้อมูลไม่ได้)
etfs = ['YINN', 'FNGU', 'SOXL', 'FXI', 'EURL', 'TNA', 'GDXU', 'TSLL', 'TNA', 'URTY', 'FAS', 'INDL', 'TPOR', 'CURE', 'EDC']

# เลือก ETF ที่ต้องการดู
selected_etf = st.selectbox("เลือก ETF", etfs)

# ดึงข้อมูล
df = fetch_etf_data(selected_etf)

# เช็กข้อมูลว่าโหลดได้หรือไม่
if df is None or df.empty:
    st.error("❌ โหลดข้อมูลไม่สำเร็จ กรุณาลองใหม่ หรือตรวจเช็คชื่อ ETF")
    st.stop()

# คำนวณอินดิเคเตอร์
df = calculate_technical_indicators(df)

# สร้างสัญญาณ
df = generate_signals(df)

# แสดงผลลัพธ์ล่าสุด
latest = df.iloc[-1]

# แสดงสัญญาณล่าสุด
st.subheader(f"📊 สัญญาณล่าสุด: {selected_etf}")
st.markdown(f"- วันที่: `{latest.name.date()}`")
st.markdown(f"- สัญญาณ: **{latest['Signal']}**")
st.markdown(f"- RSI: `{latest['Rsi']:.2f}`")
st.markdown(f"- MACD: `{latest['Macd']:.2f}`")
st.markdown(f"- EMA20: `{latest['Ema20']:.2f}`")
