import streamlit as st
import pandas as pd
from breakout_scanner import calculate_technical_indicators, generate_signals

# รายการ ETF ที่รองรับ
etfs = ['YINN', 'FNGU', 'SOXL', 'FXI', 'EURL', 'TNA', 'GDXU']

# UI พื้นฐาน
st.set_page_config(page_title="Breakout Auto ETF Scanner", layout="wide")
st.markdown("## 📉 Breakout Auto ETF Scanner (YFinance Edition)")
st.caption("Powered by มาบอย 🐂🔥")

# เลือก ETF
selected_etf = st.selectbox("เลือก ETF", etfs)

try:
    # ดึงข้อมูลและคำนวณอินดิเคเตอร์
    df = calculate_technical_indicators(selected_etf)
    df = generate_signals(df)

    # แสดงผลข้อมูลล่าสุด
    latest = df.tail(1)

    st.markdown(f"### 📊 สัญญาณล่าสุด: **{selected_etf}**")
    latest_date = latest['Date'].iloc[0].date()
    st.markdown(f"- 📅 วันที่: `{latest_date}`")

    # แสดงสัญญาณ
    signal = latest['Signal'].values[0]
    rsi = latest['Rsi'].values[0]
    macd = latest['Macd'].values[0]
    rr = latest['R:R'].values[0]

    st.markdown(f"- 🔔 สัญญาณ: `{signal}`")
    st.markdown(f"- RSI: `{rsi:.2f}` | MACD: `{macd:.2f}` | R:R: `{rr:.1f}`")

    # แสดงกราฟราคาย้อนหลัง
    st.line_chart(df.set_index("Date")["Close"])

except Exception as e:
    st.error(f"❌ โหลดข้อมูลไม่สำเร็จ: {e}")
