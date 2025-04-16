import streamlit as st
import pandas as pd
from breakout_scanner import calculate_technical_indicators, generate_signals

st.set_page_config(page_title="Breakout Auto ETF Scanner (YFinance Edition)", layout="wide")
st.title("📈 Breakout Auto ETF Scanner (YFinance Edition)")
st.caption("Powered by มาบอย 🐃🔥")

# List of ETFs to scan
etfs = ['YINN', 'FNGU', 'SOXL', 'FXI', 'EURL', 'TNA', 'GDXU']
selected_etf = st.selectbox("เลือก ETF", etfs)

try:
    # ดึงข้อมูลและคำนวณอินดิเคเตอร์
    df = calculate_technical_indicators(selected_etf)
    df = generate_signals(df)

    # แสดงผลข้อมูลล่าสุด
    latest = df.tail(1)
    latest_date = latest['Date'].iloc[0].date()

    st.subheader(f"📊 สัญญาณล่าสุด: {selected_etf}")
    st.markdown(f"- วันที่: **{latest_date}**")
    st.markdown(f"- สัญญาณ: **{latest['Signal'].iloc[0]}**")
    st.markdown(f"- RSI: `{latest['Rsi'].values[0]:.2f}`")
    st.markdown(f"- MACD: `{latest['Macd'].values[0]:.2f}`")
    st.markdown(f"- R:R: `{latest['R:R'].values[0]:.2f}`")

    # กราฟราคาย้อนหลัง
    st.line_chart(df.set_index("Date")["Close"])

except Exception as e:
    st.error(f"❌ โหลดข้อมูลไม่สำเร็จ: {e}")
