import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# ตรวจสอบว่าไฟล์ breakout_scanner.py มีและอยู่ในโฟลเดอร์เดียวกันหรือไม่
try:
    from breakout_scanner import (
        fetch_etf_data,
        calculate_technical_indicators,
        generate_signals,
        assess_market_condition,
    )
except ImportError:
    st.error("❌ ไม่พบไฟล์ breakout_scanner.py กรุณาตรวจสอบว่าอยู่ในโฟลเดอร์เดียวกัน")
    st.stop()

st.set_page_config(page_title="Breakout Auto ETF Scanner", layout="wide")
st.title("📈 Breakout Auto ETF Scanner (YFinance Edition)")
st.caption("Powered by มาบอย 🐃🔥")

# ─── Sidebar: Market Filter ──────────────────────────
st.sidebar.subheader("☁️ ใช้ Market Filter จาก ETF")
market_choice = st.sidebar.selectbox("เลือก ETF ตลาด", ["SPY", "QQQ"])

with st.sidebar.status("กำลังโหลดข้อมูลตลาด..."):
    market_df = fetch_etf_data(market_choice)
    
    if market_df.empty:
        market_status = "Unknown"
        st.sidebar.error(f"⚠️ โหลดข้อมูล {market_choice} ไม่สำเร็จ")
    else:
        try:
            market_df = calculate_technical_indicators(market_df)
            market_status = assess_market_condition(market_df)
        except Exception as e:
            st.sidebar.error(f"⚠️ เกิดข้อผิดพลาดในการประเมินตลาด: {str(e)}")
            market_status = "Unknown"

# แสดงสถานะตลาดพร้อม indicator สี        
if market_status == "Bullish":
    st.sidebar.success(f"**Market Status ({market_choice}):** `{market_status}` 🟢")
elif market_status == "Bearish":
    st.sidebar.error(f"**Market Status ({market_choice}):** `{market_status}` 🔴")
elif market_status == "Neutral":
    st.sidebar.warning(f"**Market Status ({market_choice}):** `{market_status}` 🟡")
else:
    st.sidebar.info(f"**Market Status ({market_choice}):** `{market_status}` ⚪")

# ─── Main: ETF Scanner ────────────────────────────────
st.subheader("เลือก ETF ที่ต้องการสแกน")
ticker_list = ["YINN", "FNGU", "SOXL", "FXI", "EURL", "TNA", "GDXU"]
selected_etf = st.selectbox("ETF Scanner", ticker_list)

with st.status("กำลังโหลดข้อมูล ETF..."):
    df = fetch_etf_data(selected_etf)
    
    if df.empty:
        st.error(f"❌ โหลดข้อมูล {selected_etf} ไม่สำเร็จ")
        st.stop()
    
    try:
        df = calculate_technical_indicators(df)
        df = generate_signals(df, market_status)
    except Exception as e:
        st.error(f"❌ เกิดข้อผิดพลาดในการสร้างสัญญาณ: {str(e)}")
        st.stop()

# ตรวจสอบว่ามีคอลัมน์ที่จำเป็นหรือไม่
required_columns = ["Signal", "Rsi", "Macd", "Ema20"]
missing_columns = [col for col in required_columns if col not in df.columns]
if missing_columns:
    st.error(f"❌ ไม่พบคอลัมน์ที่จำเป็น: {', '.join(missing_columns)}")
    st.stop()

# Latest signal
latest_ts = df.index[-1]
latest = df.iloc[-1]
date_str = latest_ts.date().isoformat()
signal = latest["Signal"]
rsi_val = latest["Rsi"]
macd_val = latest["Macd"]
ema20_val = latest["Ema20"]

# แสดงสัญญาณล่าสุด
st.markdown(f"### 🧠 สัญญาณล่าสุด: `{selected_etf}`")
st.markdown(f"- 📅 วันที่: `{date_str}`")

if signal == "BUY":
    st.success(f"- 📊 สัญญาณ: **{signal}** 🟢")
elif signal == "SELL":
    st.error(f"- 📊 สัญญาณ: **{signal}** 🔴")
else:
    st.info(f"- 📊 สัญญาณ: **{signal}** ⚪")

col1, col2, col3 = st.columns(3)
with col1:
    # แสดง RSI พร้อมสี
    if rsi_val > 70:
        st.warning(f"- RSI: `{rsi_val:.2f}` (Overbought)")
    elif rsi_val < 30:
        st.warning(f"- RSI: `{rsi_val:.2f}` (Oversold)")
    else:
        st.markdown(f"- RSI: `{rsi_val:.2f}`")
        
with col2:
    # แสดง MACD พร้อมสถานะ
    if macd_val > 0:
        st.markdown(f"- MACD: `{macd_val:.2f}` (Positive)")
    else:
        st.markdown(f"- MACD: `{macd_val:.2f}` (Negative)")
        
with col3:
    # แสดงสถานะ EMA20 เทียบกับราคาปิด
    if latest["Close"] > ema20_val:
        st.markdown(f"- EMA20: `{ema20_val:.2f}` (Price > EMA20)")
    else:
        st.markdown(f"- EMA20: `{ema20_val:.2f}` (Price < EMA20)")

# แสดงกราฟ
st.subheader("📊 กราฟราคาและตัวชี้วัด")
fig = make_subplots(rows=2, cols=1, shared_xaxes=True, 
                   vertical_spacing=0.05, row_heights=[0.7, 0.3])

# กราฟราคาและ EMA
fig.add_trace(go.Scatter(x=df.index, y=df["Close"], name="ราคาปิด",
                         line=dict(color='royalblue')), row=1, col=1)
fig.add_trace(go.Scatter(x=df.index, y=df["Ema20"], name="EMA20",
                         line=dict(color='orange')), row=1, col=1)

# กราฟ RSI
fig.add_trace(go.Scatter(x=df.index, y=df["Rsi"], name="RSI",
                         line=dict(color='purple')), row=2, col=1)
fig.add_trace(go.Scatter(x=df.index, y=[70]*len(df), name="Overbought",
                         line=dict(color='red', dash='dash')), row=2, col=1)
fig.add_trace(go.Scatter(x=df.index, y=[30]*len(df), name="Oversold",
                         line=dict(color='green', dash='dash')), row=2, col=1)

# แสดงสัญญาณซื้อขาย
buy_signals = df[df["Signal"] == "BUY"]
sell_signals = df[df["Signal"] == "SELL"]

if not buy_signals.empty:
    fig.add_trace(go.Scatter(x=buy_signals.index, y=buy_signals["Close"], name="Buy",
                        mode="markers", marker=dict(color="green", size=10, symbol="triangle-up")), row=1, col=1)
if not sell_signals.empty:
    fig.add_trace(go.Scatter(x=sell_signals.index, y=sell_signals["Close"], name="Sell",
                        mode="markers", marker=dict(color="red", size=10, symbol="triangle-down")), row=1, col=1)

fig.update_layout(height=600, title_text=f"{selected_etf} - ราคาและตัวชี้วัด")
st.plotly_chart(fig, use_container_width=True)

with st.expander("🔍 ข้อมูลย้อนหลัง"):
    st.dataframe(df.tail(30)[["Close", "Ema20", "Rsi", "Macd", "Signal"]], use_container_width=True)
