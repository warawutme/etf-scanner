import streamlit as st
from breakout_scanner import analyze_ticker, evaluate_market

# ตั้งค่าหน้าหลักของแอป
st.set_page_config(page_title="Breakout Auto ETF Scanner", layout="wide")

st.title("📊 Breakout Auto ETF Scanner (YFinance Edition)")
st.write("วิเคราะห์แนวโน้มตลาดและสัญญาณซื้อ/ขายอัตโนมัติสำหรับกลุ่ม ETF ที่เลือก โดยอ้างอิงข้อมูลราคาย้อนหลังจาก Yahoo Finance")

# ส่วนเลือก Market Filter ETF (เช่น SPY หรือ QQQ)
market_choices = ["SPY", "QQQ"]
market_ticker = st.selectbox("เลือก ETF หลักสำหรับ Market Filter:", market_choices, index=0)
# ดึงและวิเคราะห์ข้อมูลของ ETF หลัก (market)
market_df = analyze_ticker(market_ticker)
market_status = evaluate_market(market_df)

# แสดงสถานะตลาด
st.subheader(f"Market Status ({market_ticker}): **{market_status}**")
# เพิ่มการเน้นสีตามสถานะเพื่อความชัดเจน
if market_status == "Bullish":
    st.success(f"Market is {market_status}")
elif market_status == "Bearish":
    st.error(f"Market is {market_status}")
else:
    st.info(f"Market is {market_status}")

# ส่วนกรอกชื่อย่อ ETF ที่ต้องการสแกน
default_list = "YINN, SOXL, FNGU, FXI"
tickers_input = st.text_input(
    "ใส่รายชื่อ ETF ที่ต้องการสแกน (คั่นด้วยเครื่องหมายจุลภาค):",
    default_list
)
# แปลง input string เป็น list และลบช่องว่างเกินจำเป็น
tickers_list = [t.strip().upper() for t in tickers_input.split(",") if t.strip()]

# ตรวจสอบว่ามี tickers ให้วิเคราะห์
if len(tickers_list) == 0:
    st.warning("กรุณาระบุรายชื่อ ETF อย่างน้อย 1 ตัวเพื่อสแกน")
else:
    # ดึงข้อมูลและวิเคราะห์สำหรับทุก ticker ในรายการ
    results = {}  # เก็บ DataFrame ของแต่ละ ticker
    for tic in tickers_list:
        df = analyze_ticker(tic)
        if df is None:
            st.error(f"ไม่สามารถดึงข้อมูล {tic} ได้")
        else:
            results[tic] = df

    if results:
        # สรุปสัญญาณล่าสุดของแต่ละ ETF
        summary_data = {
            "Ticker": [],
            "Last Price": [],
            "Signal (Latest)": []
        }
        for tic, df in results.items():
            summary_data["Ticker"].append(tic)
            summary_data["Last Price"].append(round(df["Close"].iloc[-1], 2))
            summary_data["Signal (Latest)"].append(df["Signal"].iloc[-1])
        summary_df = (
            pd.DataFrame(summary_data)
            .set_index("Ticker")
            .sort_index()
        )
        st.subheader("🔎 Latest Signals Summary")
        st.dataframe(summary_df)

        # แสดงข้อมูลย้อนหลังและสัญญาณของแต่ละ ETF
        for tic, df in results.items():
            st.subheader(f"ETF: {tic} – Recent Data & Indicators")
            # แสดง 10 แถวสุดท้ายของข้อมูลรวมอินดิเคเตอร์และสัญญาณ
            st.dataframe(df.tail(10))
