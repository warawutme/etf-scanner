import streamlit as st
import pandas as pd
from breakout_scanner import (
    fetch_etf_data,
    calculate_technical_indicators,
    assess_market_condition,
    generate_signals
)

# ✅ API KEY ที่พี่มาบอยใช้งาน
API_KEY = 'UWXY2WAJMZUGL03O'

# 🔍 รายชื่อ ETF ที่ต้องการสแกน
etfs = ['TQQQ', 'SOXL', 'LABU', 'GUSH']

st.set_page_config(page_title="ETF Auto Scanner", layout="centered")
st.title("📊 Breakout Auto ETF Scanner")
st.caption("Powered by มาบอย 🐂🔥")

# 📉 เลือก ETF อ้างอิงสำหรับประเมินสภาพตลาด
market_etf = st.selectbox("เลือก ETF ตลาด", ['SPY', 'QQQ', 'IWM'])

# ✅ ดึงข้อมูลจาก Alpha Vantage
market_data = fetch_etf_data(market_etf, API_KEY)

# ✅ ป้องกันการพังถ้าข้อมูลไม่มา
if market_data.empty or market_data.shape[0] < 20:
    st.error("❌ โหลดข้อมูลจาก API ไม่สำเร็จ กรุณาเช็ก API Key หรือรอสักครู่ (อาจเกิน limit 5 ครั้ง/นาที)")
    st.stop()

# 🧠 วิเคราะห์แนวโน้มตลาด
market_data = calculate_technical_indicators(market_data)
market_condition = assess_market_condition(market_data)
st.markdown(f"### 🧭 สภาพตลาดตอนนี้: `{market_condition}`")

# 🧪 สแกน ETF ทั้งหมด
rows = []

for etf in etfs:
    df = fetch_etf_data(etf, API_KEY)

    if df.empty or df.shape[0] < 20:
        rows.append({'ETF': etf, 'Status': '❌ ไม่มีข้อมูล'})
        continue

    df = calculate_technical_indicators(df)
    df = generate_signals(df, market_condition)
    latest = df.iloc[-1]

    rows.append({
        'ETF': etf,
        'Date': df.index[-1].date(),
        'Close': latest['close'],
        'Signal': latest['signal'],
        'RR': round(latest['rr'], 2) if 'rr' in latest else '-',
    })

# 📋 แสดงตารางผลลัพธ์
result_df = pd.DataFrame(rows)
st.dataframe(result_df)


