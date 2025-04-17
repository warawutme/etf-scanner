import streamlit as st
import pandas as pd
import yfinance as yf
from breakout_scanner import calculate_technical_indicators, generate_signals, assess_market_condition

# ตั้งค่าหน้าเว็บ
st.set_page_config(page_title="Breakout Auto ETF Scanner", layout="wide")
st.markdown("## 📈 Breakout Auto ETF Scanner (YFinance Edition)")
st.caption("Powered by มาบอย 🐃🔥")

# รายชื่อ ETF
tickers = ['YINN', 'FNGU', 'SOXL', 'FXI', 'EURL', 'TNA', 'GDXU']
market_refs = ['SPY', 'QQQ', 'DIA']  # ✅ เพิ่มตัวเลือก Market Filter ได้

# ===== Sidebar =====
st.sidebar.markdown("### 🧭 ใช้ Market Filter จาก ETF:")
market_etf = st.sidebar.selectbox("เลือก ETF ตลาด", market_refs, index=0)
st.sidebar.subheader("📈 Market Filter")

# ✅ ประเมิน Market Status จาก ETF อ้างอิง
try:
    market_df = yf.download(market_etf, period='3mo', interval='1d', progress=False)
    market_df = market_df[['Open', 'High', 'Low', 'Close', 'Volume']].dropna()
    market_df.reset_index(inplace=True)
    market_df.columns.name = None
    market_df['Date'] = pd.to_datetime(market_df['Date'])
    market_df = calculate_technical_indicators(market_df)
    market_status = assess_market_condition(market_df)
except Exception as e:
    market_status = "Unknown"
    st.sidebar.warning("⚠️ ไม่สามารถประเมินตลาดได้")

st.sidebar.markdown(f"**Market Status ({market_etf}):** `{market_status}`")

# ===== Main Section =====
selected_etf = st.selectbox("เลือก ETF ที่ต้องการสแกน", tickers)

# ✅ ดึงข้อมูล ETF หลัก
try:
    df = yf.download(selected_etf, period='3mo', interval='1d', progress=False)
    df = df[['Open', 'High', 'Low', 'Close', 'Volume']].dropna()
    df.reset_index(inplace=True)
    df.columns.name = None
    df['Date'] = pd.to_datetime(df['Date'])
except Exception as e:
    st.error(f"❌ โหลดข้อมูล ETF ไม่สำเร็จ: {e}")
    st.stop()

# ✅ คำนวณอินดิเคเตอร์ + สร้างสัญญาณ
try:
    df = calculate_technical_indicators(df)
    df = generate_signals(df, market_status)
except Exception as e:
    st.error(f"❌ คำนวณอินดิเคเตอร์ไม่สำเร็จ: {e}")
    st.stop()

# ✅ แสดงสัญญาณล่าสุด
latest = df.iloc[-1] if not df.empty else None

if latest is not None:
    # ป้องกัน Error ถ้าไม่มีวันที่
    try:
        latest_date = latest['Date'].date() if pd.notnull(latest['Date']) else "ไม่พบวันที่"
    except:
        latest_date = "ไม่พบวันที่"

    st.markdown(f"### 🧠 สัญญาณล่าสุด: `{selected_etf}`")
    st.markdown(f"- 📅 วันที่: `{latest_date}`")
    st.markdown(f"- 📊 สัญญาณ: **{latest['Signal']}**")
    st.markdown(f"- RSI: `{float(latest['Rsi']):.2f}`")
    st.markdown(f"- MACD: `{float(latest['Macd']):.2f}`")
    st.markdown(f"- EMA20: `{float(latest['Ema20']):.2f}`")
else:
    st.warning("ไม่พบข้อมูลล่าสุด")

# ✅ ตารางย้อนหลัง
with st.expander("🔍 ข้อมูลย้อนหลัง"):
    st.dataframe(df.tail(30), use_container_width=True)
