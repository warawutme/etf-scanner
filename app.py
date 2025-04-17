import streamlit as st
import pandas as pd
import yfinance as yf
from breakout_scanner import calculate_technical_indicators, generate_signals, assess_market_condition

# ——— ตั้งค่าหน้าเว็บ ———
st.set_page_config(page_title="Breakout Auto ETF Scanner", layout="wide")
st.title("📈 Breakout Auto ETF Scanner (YFinance Edition)")
st.caption("Powered by มาบอย 🐃🔥")

# ——— Sidebar: เลือก ETF สำหรับ Market Filter ———
st.sidebar.subheader("☁️ ใช้ Market Filter จาก ETF:")
market_tickers = ['SPY', 'QQQ']  # ถ้าต้องการเพิ่ม ETF ตัวอื่น ใส่ลงไปใน list นี้
market_ticker = st.sidebar.selectbox("เลือก ETF ตลาด", market_tickers)

# ——— ประเมิน Market Status ———
try:
    market_df = yf.download(market_ticker, period='3mo', interval='1d', progress=False)
    market_df = market_df[['Open', 'High', 'Low', 'Close', 'Volume']].dropna().reset_index()
    market_df['Date'] = pd.to_datetime(market_df['Date'])
    market_df = calculate_technical_indicators(market_df)
    market_status = assess_market_condition(market_df)
except Exception:
    market_status = "Unknown"
    st.sidebar.warning("⚠️ ไม่สามารถประเมินสภาพตลาดได้")

st.sidebar.markdown(f"**Market Status ({market_ticker}):** `{market_status}`")

# ——— Main: เลือก ETF ที่ต้องการสแกน ———
st.subheader("เลือก ETF ที่ต้องการสแกน")
tickers = ['YINN', 'FNGU', 'SOXL', 'FXI', 'EURL', 'TNA', 'GDXU']
selected_etf = st.selectbox("ETF Scanner", tickers)

# ——— ดึงข้อมูล ETF ———
try:
    df = yf.download(selected_etf, period='3mo', interval='1d', progress=False)
    df = df[['Open', 'High', 'Low', 'Close', 'Volume']].dropna().reset_index()
    df['Date'] = pd.to_datetime(df['Date'])
except Exception as e:
    st.error(f"❌ โหลดข้อมูล {selected_etf} ไม่สำเร็จ: {e}")
    st.stop()

# ——— คำนวณอินดิเคเตอร์ + สร้างสัญญาณ ———
try:
    df = calculate_technical_indicators(df)
    df = generate_signals(df, market_status)
except Exception as e:
    st.error(f"❌ คำนวณอินดิเคเตอร์ไม่สำเร็จ: {e}")
    st.stop()

# ——— แสดงสัญญาณล่าสุด ———
latest = df.iloc[-1]  # Series ของแถวสุดท้าย

# ดึงค่าต่าง ๆ ออกมาเป็น scalar
latest_date = latest.get('Date', pd.NaT)
if pd.isna(latest_date):
    date_str = "ไม่พบวันที่"
else:
    date_str = latest_date.date().isoformat()

signal = latest.get('Signal', 'N/A')
rsi = latest.get('Rsi', None)
macd = latest.get('Macd', None)
ema20 = latest.get('Ema20', None)

st.markdown(f"### 🧠 สัญญาณล่าสุด: `{selected_etf}`")
st.markdown(f"- 📅 วันที่: `{date_str}`")
st.markdown(f"- 📊 สัญญาณ: **{signal}**")
if rsi is not None:
    st.markdown(f"- RSI: `{rsi:.2f}`")
else:
    st.markdown("- RSI: N/A")
if macd is not None:
    st.markdown(f"- MACD: `{macd:.2f}`")
else:
    st.markdown("- MACD: N/A")
if ema20 is not None:
    st.markdown(f"- EMA20: `{ema20:.2f}`")
else:
    st.markdown("- EMA20: N/A")

# ——— ข้อมูลย้อนหลัง ———
with st.expander("🔍 ข้อมูลย้อนหลัง"):
    st.dataframe(df.tail(30), use_container_width=True)

