import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import time
from breakout_scanner import (
    fetch_etf_data,
    calculate_technical_indicators,
    generate_signals,
    assess_market_condition,
)

st.set_page_config(page_title="Breakout Auto ETF Scanner", layout="wide")
st.title("📈 Breakout Auto ETF Scanner (YFinance Edition)")
st.caption("Powered by มาบอย 🐃🔥")

# ─── Sidebar: Market Filter ──────────────────────────
st.sidebar.subheader("☁️ ใช้ Market Filter จาก ETF")
market_choice = st.sidebar.selectbox("เลือก ETF ตลาด", ["SPY", "QQQ"])

fallback_market_etfs = ["SPY", "QQQ", "IWM", "DIA"]
market_df = pd.DataFrame()

with st.sidebar.status("กำลังโหลดข้อมูลตลาด...") as status:
    # ลองโหลดข้อมูลตลาดหลัก
    market_df = fetch_etf_data(market_choice)
    
    # ถ้าโหลดไม่สำเร็จ ให้ลองโหลด ETF สำรอง
    if market_df.empty:
        status.update(label=f"⚠️ โหลดข้อมูล {market_choice} ไม่สำเร็จ กำลังลองใช้ ETF สำรอง...", state="running")
        
        for fallback_etf in fallback_market_etfs:
            if fallback_etf == market_choice:
                continue
                
            st.sidebar.info(f"กำลังลองใช้ {fallback_etf} แทน...")
            market_df = fetch_etf_data(fallback_etf)
            
            if not market_df.empty:
                market_choice = fallback_etf  # ใช้ ETF ตัวที่โหลดได้แทน
                st.sidebar.success(f"ใช้ {fallback_etf} เป็น Market ETF แทน")
                break
                
    if market_df.empty:
        market_status = "Unknown"
        st.sidebar.error(f"⚠️ ไม่สามารถโหลดข้อมูลตลาดได้จากทุก ETF ที่ลอง")
        status.update(label="❌ โหลดข้อมูลตลาดไม่สำเร็จ", state="error")
    else:
        try:
            # แสดงข้อมูลเบื้องต้นเพื่อตรวจสอบ
            st.sidebar.success(f"โหลดข้อมูล {market_choice} สำเร็จ {len(market_df)} แถว")
            
            # คำนวณตัวชี้วัดและประเมินตลาด
            market_df = calculate_technical_indicators(market_df)
            market_status = assess_market_condition(market_df)
            status.update(label=f"✅ วิเคราะห์ตลาดสำเร็จ: {market_status}", state="complete")
        except Exception as e:
            market_status = "Unknown"
            st.sidebar.error(f"⚠️ ประเมินตลาดไม่ได้: {str(e)}")
            status.update(label="❌ วิเคราะห์ตลาดล้มเหลว", state="error")

# แสดงสถานะตลาด
if market_status == "Bullish":
    st.sidebar.success(f"**Market Status ({market_choice}):** `{market_status}` 🟢")
elif market_status == "Neutral":
    st.sidebar.warning(f"**Market Status ({market_choice}):** `{market_status}` 🟡")
elif market_status == "Bearish":
    st.sidebar.error(f"**Market Status ({market_choice}):** `{market_status}` 🔴")
else:
    st.sidebar.info(f"**Market Status ({market_choice}):** `{market_status}` ⚪")

# ─── Debug info ───────────────────────────────────────
with st.sidebar.expander("📊 ข้อมูลตลาด (Debug)"):
    if not market_df.empty:
        st.dataframe(market_df.tail(5))
    else:
        st.error("ไม่มีข้อมูลตลาด")

# ─── Main: ETF Scanner ────────────────────────────────
st.subheader("เลือก ETF ที่ต้องการสแกน")
ticker_list = ["YINN", "FNGU", "SOXL", "FXI", "EURL", "TNA", "GDXU", "SPY", "QQQ"]
selected_etf = st.selectbox("ETF Scanner", ticker_list)

# เพิ่มตัวเลือกขั้นสูง
with st.expander("⚙️ ตัวเลือกขั้นสูง"):
    use_fallback = st.checkbox("ใช้ ETF สำรอง (ถ้าโหลดไม่สำเร็จ)", value=True)
    fallback_choices = st.multiselect(
        "ETF สำรอง", 
        options=["SPY", "QQQ", "AAPL", "IWM", "DIA"], 
        default=["SPY", "QQQ"],
        disabled=not use_fallback
    )

with st.status("📥 กำลังโหลดข้อมูล ETF...") as etf_status:
    df = fetch_etf_data(selected_etf)
    
    # ลองใช้ ETF สำรอง
    if df.empty and use_fallback:
        etf_status.update(label=f"⚠️ โหลดข้อมูล {selected_etf} ไม่สำเร็จ กำลังลองใช้ ETF สำรอง...", state="running")
        
        for fallback_etf in fallback_choices:
            if fallback_etf == selected_etf:
                continue
                
            st.info(f"กำลังลองใช้ {fallback_etf} แทน...")
            df = fetch_etf_data(fallback_etf)
            
            if not df.empty:
                selected_etf = fallback_etf  # ใช้ ETF ตัวที่โหลดได้แทน
                st.success(f"ใช้ {fallback_etf} แทน")
                break
    
    if df.empty:
        etf_status.update(label=f"❌ โหลดข้อมูล {selected_etf} ไม่สำเร็จ", state="error")
        st.error(f"❌ โหลดข้อมูล {selected_etf} ไม่สำเร็จ")
        st.stop()
    
    try:
        # ดำเนินการคำนวณตัวชี้วัดและสัญญาณ
        etf_status.update(label=f"🧮 กำลังคำนวณตัวชี้วัดสำหรับ {selected_etf}...", state="running")
        df = calculate_technical_indicators(df)
        
        # ตรวจสอบข้อมูลพื้นฐาน
        st.write(f"มีข้อมูลทั้งหมด {len(df)} แถว")
        
        # ตรวจสอบข้อมูล NaN
        if df.isna().any().any():
            st.warning(f"พบข้อมูล NaN ในชุดข้อมูล จะทำการกรองออกอัตโนมัติ")
            nan_counts = df.isna().sum()
            st.write(f"จำนวน NaN แต่ละคอลัมน์: {nan_counts.to_dict()}")
        
        # สร้างสัญญาณ
        etf_status.update(label=f"🔍 กำลังสร้างสัญญาณสำหรับ {selected_etf}...", state="running")
        df = generate_signals(df, market_status)
        
        # กรองข้อมูล NaN ออก
        df = df.dropna()
        
        if df.empty:
            etf_status.update(label=f"⚠️ ข้อมูลไม่เพียงพอหลังกรอง NaN", state="error")
            st.error("หลังจากกรอง NaN แล้ว ไม่มีข้อมูลเหลืออยู่")
            st.stop()
            
        etf_status.update(label=f"✅ วิเคราะห์ {selected_etf} เสร็จสมบูรณ์", state="complete")
        
    except Exception as e:
        etf_status.update(label=f"❌ เกิดข้อผิดพลาดในการประมวลผล", state="error")
        st.error(f"❌ เกิดข้อผิดพลาดในการประมวลผล: {str(e)}")
        import traceback
        st.code(traceback.format_exc())
        st.stop()

# ─── Signal Section ───────────────────────────────────
try:
    latest_ts = df.index[-1]
    latest = df.iloc[-1]
    date_str = latest_ts.date().isoformat()
    signal = latest.get("Signal", "HOLD")
    rsi_val = latest.get("Rsi", 0)
    macd_val = latest.get("Macd", 0)
    ema20_val = latest.get("Ema20", 0)

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
        st.markdown(f"- RSI: `{rsi_val:.2f}`")
    with col2:
        st.markdown(f"- MACD: `{macd_val:.2f}`")
    with col3:
        st.markdown(f"- EMA20: `{ema20_val:.2f}`")
except Exception as e:
    st.error(f"เกิดข้อผิดพลาดในการแสดงสัญญาณ: {str(e)}")

# ─── Graph Section ────────────────────────────────────
try:
    st.subheader("📊 กราฟราคาและตัวชี้วัด")
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True,
                        vertical_spacing=0.05, row_heights=[0.7, 0.3])

    fig.add_trace(go.Scatter(x=df.index, y=df["Close"], name="ราคาปิด",
                            line=dict(color='royalblue')), row=1, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=df["Ema20"], name="EMA20",
                            line=dict(color='orange')), row=1, col=1)
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
except Exception as e:
    st.error(f"เกิดข้อผิดพลาดในการสร้างกราฟ: {str(e)}")

# ─── Data Table ────────────────────────────────────────
with st.expander("🔍 ข้อมูลย้อนหลัง"):
    try:
        st.dataframe(df.tail(30)[["Close", "Ema20", "Rsi", "Macd", "Signal"]], use_container_width=True)
    except Exception as e:
        st.error(f"เกิดข้อผิดพลาดในการแสดงตาราง: {str(e)}")
