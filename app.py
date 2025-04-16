import yfinance as yf
import streamlit as st

st.set_page_config(page_title="ETF Checker", layout="centered")
st.title("✅ ตรวจสอบ ETF ที่ใช้ได้กับ yfinance")

tickers = ['YINN', 'FNGU', 'SOXL', 'FXI', 'EURL', 'TNA', 'GDXU', 'JUNG']

for symbol in tickers:
    try:
        df = yf.download(symbol, period='1mo', interval='1d')
        if df.empty:
            st.error(f"❌ {symbol}: No data")
        else:
            st.success(f"✅ {symbol}: Data OK")
    except Exception as e:
        st.warning(f"⚠️ {symbol}: ERROR – {str(e)}")
