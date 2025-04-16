
import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.graph_objects as go
from breakout_scanner import calculate_technical_indicators, generate_signals

# ✅ รายชื่อ ETF ที่ใช้งานได้ (ยกเว้น JNUG และตัวที่รันไม่ผ่าน)
etfs = [
    'YINN', 'FNGU', 'SOXL', 'FXI', 'EURL',
    'TNA', 'GDXU', 'EURZ', 'TSLL', 'YANG',
    'TPOR', 'NRGU', 'INDL', 'CURE', 'FAS', 'EDC'
]

st.set_page_config(page_title="Breakout Auto ETF Scanner", layout="wide")
st.markdown("<h1 style='text-align: center;'>📈 Breakout Auto ETF Scanner (YFinance Edition)</h1>", unsafe_allow_html=True)
st.caption("Powered by มาบอย 🐃🔥")

selected_etf = st.sidebar.selectbox("เลือก ETF", etfs)

@st.cache_data(ttl=3600)
def fetch_yf_data(ticker):
    try:
        df = yf.download(ticker, period="3mo", interval="1d", progress=False)
        df.reset_index(inplace=True)
        return df
    except:
        return None

df = fetch_yf_data(selected_etf)

if df is None or df.empty:
    st.error("❌ โหลดข้อมูลไม่สำเร็จ กรุณาลองใหม่ หรือเช็กชื่อ ETF")
    st.stop()

df = calculate_technical_indicators(df)
df = generate_signals(df)

latest = df.iloc[-1]
st.subheader(f"📊 สัญญาณล่าสุด: {selected_etf}")
st.markdown(f"""
- วันที่: `{latest['Date'].date()}`
- ราคา: **${latest['Close']:.2f}**
- สัญญาณ: **{latest['signal']}**
- RSI: `{latest['rsi']:.0f}`
- MACD: `{latest['macd']:.2f}`
""")

fig = go.Figure()
fig.add_trace(go.Scatter(x=df['Date'], y=df['Close'], mode='lines', name='Close'))
fig.add_trace(go.Scatter(x=df['Date'], y=df['ema20'], mode='lines', name='EMA20'))
fig.add_trace(go.Scatter(x=df['Date'], y=df['ema50'], mode='lines', name='EMA50'))
fig.update_layout(title='📈 Price Chart with EMA', xaxis_title='Date', yaxis_title='Price')
st.plotly_chart(fig, use_container_width=True)

st.markdown("### 🧾 ข้อมูลย้อนหลัง")
st.dataframe(df[['Date', 'Close', 'ema20', 'ema50', 'rsi', 'macd', 'signal']].tail(10), use_container_width=True)
