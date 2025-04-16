
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from breakout_scanner import fetch_etf_data, calculate_technical_indicators, generate_signals, assess_market_condition

st.set_page_config(page_title="ETF Breakout Scanner", layout="wide")

st.title("📈 Breakout Auto ETF Scanner (YFinance Edition)")

# รายชื่อ ETF ที่ใช้ในระบบ
etfs = ['TQQQ', 'YINN', 'FNGU', 'SOXL', 'FXI', 'EURL', 'TNA', 'GDXU', 'JNUG']

# เลือก ETF ที่ต้องการแสดง
selected_etf = st.sidebar.selectbox("เลือก ETF", etfs)

# โหลดข้อมูล
with st.spinner("📡 กำลังดึงข้อมูลจากตลาด..."):
    try:
        data = fetch_etf_data(selected_etf)
        market_data = fetch_etf_data("SPY")  # ใช้ SPY เป็นตัวแทนตลาด
        market_status = assess_market_condition(market_data)
        data = calculate_technical_indicators(data)
        data = generate_signals(data, market_status)
        last_signal = data['signal'].iloc[-1]
    except Exception as e:
        st.error("❌ โหลดข้อมูลไม่สำเร็จ กรุณาลองใหม่ หรือเช็กชื่อ ETF")
        st.stop()

# แสดงสถานะตลาด
st.subheader(f"🧭 สถานะตลาดตอนนี้: `{market_status}`")

# แสดงสัญญาณล่าสุด
st.metric("📊 สัญญาณล่าสุด", last_signal, delta=None)

# กราฟราคากับสัญญาณ
fig = go.Figure()
fig.add_trace(go.Candlestick(
    x=data.index,
    open=data['open'], high=data['high'],
    low=data['low'], close=data['close'],
    name='Price'
))
fig.add_trace(go.Scatter(x=data.index, y=data['ema20'], name='EMA20', line=dict(color='blue')))
fig.add_trace(go.Scatter(x=data.index, y=data['ema50'], name='EMA50', line=dict(color='orange')))
fig.update_layout(title=f'{selected_etf} Price Chart with EMA', xaxis_title='Date', yaxis_title='Price')
st.plotly_chart(fig, use_container_width=True)

# ตารางสรุป
st.subheader("📋 ตารางข้อมูลล่าสุด")
st.dataframe(data[['close', 'rsi', 'macd', 'volume_ratio', 'signal']].tail(10))

# Footer
st.caption("© มาบอย Auto Scanner | Powered by yfinance + Streamlit")
