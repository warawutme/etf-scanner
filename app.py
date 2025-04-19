
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
    market_df = fetch_etf_data(market_choice)
    if market_df.empty:
        status.update(label=f"⚠️ โหลดข้อมูล {market_choice} ไม่สำเร็จ กำลังลองใช้ ETF สำรอง...", state="running")
        for fallback_etf in fallback_market_etfs:
            if fallback_etf == market_choice:
                continue
            st.sidebar.info(f"กำลังลองใช้ {fallback_etf} แทน...")
            market_df = fetch_etf_data(fallback_etf)
            if not market_df.empty:
                market_choice = fallback_etf
                st.sidebar.success(f"ใช้ {fallback_etf} เป็น Market ETF แทน")
                break

    if market_df.empty:
        market_status = "Unknown"
        st.sidebar.error(f"⚠️ ไม่สามารถโหลดข้อมูลตลาดได้จากทุก ETF ที่ลอง")
        status.update(label="❌ โหลดข้อมูลตลาดไม่สำเร็จ", state="error")
    else:
        try:
            st.sidebar.success(f"โหลดข้อมูล {market_choice} สำเร็จ {len(market_df)} แถว")
            market_df = calculate_technical_indicators(market_df)
            required_cols = ["Close", "Ema20", "Ema50", "Rsi", "Macd"]
            if not all(col in market_df.columns for col in required_cols):
                raise ValueError(f"ข้อมูลไม่ครบ: {', '.join([col for col in required_cols if col not in market_df.columns])}")
            market_status = assess_market_condition(market_df)
            status.update(label=f"✅ วิเคราะห์ตลาดสำเร็จ: {market_status}", state="complete")
        except Exception as e:
            market_status = "Unknown"
            st.sidebar.error(f"⚠️ ประเมินตลาดไม่ได้: {str(e)}")
            status.update(label="❌ วิเคราะห์ตลาดล้มเหลว", state="error")

if market_status == "Bullish":
    st.sidebar.success(f"**Market Status ({market_choice}):** `{market_status}` 🟢")
elif market_status == "Neutral":
    st.sidebar.warning(f"**Market Status ({market_choice}):** `{market_status}` 🟡")
elif market_status == "Bearish":
    st.sidebar.error(f"**Market Status ({market_choice}):** `{market_status}` 🔴")
else:
    st.sidebar.info(f"**Market Status ({market_choice}):** `{market_status}` ⚪")

with st.sidebar.expander("📊 ข้อมูลตลาด (Debug)"):
    if not market_df.empty:
        st.dataframe(market_df.tail(5))
    else:
        st.error("ไม่มีข้อมูลตลาด")

# ─── Main: ETF Scanner ────────────────────────────────
st.subheader("เลือก ETF ที่ต้องการสแกน")
ticker_list = ["YINN", "FNGU", "SOXL", "FXI", "EURL", "TNA", "GDXU", "SPY", "QQQ"]
selected_etf = st.selectbox("ETF Scanner", ticker_list)

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
    if df.empty and use_fallback:
        etf_status.update(label=f"⚠️ โหลดข้อมูล {selected_etf} ไม่สำเร็จ กำลังลองใช้ ETF สำรอง...", state="running")
        for fallback_etf in fallback_choices:
            if fallback_etf == selected_etf:
                continue
            st.info(f"กำลังลองใช้ {fallback_etf} แทน...")
            df = fetch_etf_data(fallback_etf)
            if not df.empty:
                selected_etf = fallback_etf
                st.success(f"ใช้ {fallback_etf} แทน")
                break

    if df.empty:
        etf_status.update(label=f"❌ โหลดข้อมูล {selected_etf} ไม่สำเร็จ", state="error")
        st.error(f"❌ โหลดข้อมูล {selected_etf} ไม่สำเร็จ")
        st.stop()

    try:
        etf_status.update(label=f"🧮 กำลังคำนวณตัวชี้วัดสำหรับ {selected_etf}...", state="running")
        df = calculate_technical_indicators(df)
        required_cols = ["Close", "Ema20", "Rsi", "Macd"]
        if not all(col in df.columns for col in required_cols):
            st.error(f"⚠️ ข้อมูลไม่ครบ ไม่สามารถวิเคราะห์ {selected_etf} ได้")
            st.stop()
        df = generate_signals(df, market_status)
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
