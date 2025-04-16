import streamlit as st
import pandas as pd
from breakout_scanner import calculate_technical_indicators, generate_signals
import yfinance as yf

st.set_page_config(page_title="Breakout Auto ETF Scanner", layout="wide")
st.markdown("""
    <style>
    .main {background-color: #111111; color: white;}
    </style>
""", unsafe_allow_html=True)

st.title("📈 Breakout Auto ETF Scanner (YFinance Edition)")
st.caption("Powered by มาบอย 🐃🔥")

# ✅ รายการ ETF ที่ทดสอบแล้วใช้งานได้
tickers = [
    'YINN', 'FNGU', 'SOXL', 'FXI', 'EURL', 'TNA', 'GDXU', 'TQQQ', 'SPXL', 'LABU', 'TSLL',
    'YANG', 'EDC', 'CURE', 'TPOR', 'INDL', 'FAS', 'URTY', 'NRGU'
]

selected_ticker = st.selectbox("เลือก ETF", tickers)

@st.cache_data(ttl=3600)
def fetch_data_yf(ticker):
    df = yf.download(ticker, period="3mo", interval="1d")
    df.reset_index(inplace=True)
    df = df[['Date', 'Open', 'High', 'Low', 'Close', 'Volume']]
    return df

try:
    df = fetch_data_yf(selected_ticker)
    df = calculate_technical_indicators(df)
    df = generate_signals(df)

    st.subheader(f"📊 สัญญาณล่าสุด: {selected_ticker}")
    latest = df.iloc[-1]

    st.markdown(f"- วันที่: `{latest['Date'].date()}`")
    st.markdown(f"- สัญญาณ: **Ticker {latest['Signal']}**")
    st.markdown(f"- RSI: `{float(latest['Rsi']):.2f}`")
    st.markdown(f"- MACD: `{float(latest['Macd']):.2f}`")
    st.markdown(f"- EMA20: `{float(latest['Ema20']):.2f}`")

    with st.expander("📉 ข้อมูลย้อนหลัง"):
        st.dataframe(df.tail(20), use_container_width=True)

except Exception as e:
    st.error(f"❌ โหลดข้อมูลไม่สำเร็จ: {e}")
