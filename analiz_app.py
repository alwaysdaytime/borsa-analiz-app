import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Sayfa Ayarları
st.set_page_config(page_title="PRO Finans Paneli", layout="wide")

# Kenar Çubuğu
with st.sidebar:
    st.title("🚀 Finans Analiz")
    sembol = st.text_input("Hisse Sembolü", value="THYAO.IS").upper()
    periyot = st.selectbox("Zaman Aralığı", ["1mo", "3mo", "6mo", "1y", "2y", "5y"], index=2)
    st.info("BIST hisseleri için sonuna .IS ekleyin.")

# Veri Çekme
@st.cache_data
def veri_yukle(symbol, period):
    return yf.download(symbol, period=period)

df = veri_yukle(sembol, periyot)

if df is not None and not df.empty:
    # Hesaplamalar
    df['MA20'] = df['Close'].rolling(window=20).mean()
    df['MA50'] = df['Close'].rolling(window=50).mean()
    
    # RSI
    delta = df['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    df['RSI'] = 100 - (100 / (1 + (gain / loss)))

    # Güvenli Veri Çevrimi
    son_fiyat = float(df['Close'].iloc[-1])
    onceki_fiyat = float(df['Close'].iloc[-2])
    degisim = ((son_fiyat - onceki_fiyat) / onceki_fiyat) * 100
    try:
        hacim = float(df['Volume'].iloc[-1])
    except:
        hacim = 0

    # Üst Panel
    st.title(f"📊 {sembol} Analiz Paneli")
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Son Fiyat", f"{son_fiyat:,.2f}", f"{degisim:+.2f}%")
    m2.metric("Günlük Hacim", f"{hacim:,.0f}")
    m3.metric("RSI (14)", f"{float(df['RSI'].iloc[-1]):.1f}")
    m4.metric("MA20", f"{float(df['MA20'].iloc[-1]):,.2f}")

    # Grafik
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.1, row_heights=[0.7, 0.3])
    fig.add_trace(go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'], name="Fiyat"), row=1, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=df['MA20'], name="MA20", line=dict(color='orange', width=1.5)), row=1, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=df['RSI'], name="RSI", line=dict(color='#6666ff')), row=2, col=1)
    
    fig.update_layout(height=600, template="plotly_dark", xaxis_rangeslider_visible=False)
    st.plotly_chart(fig, use_container_width=True)
else:
    st.error("Veri alınamadı, lütfen sembolü kontrol edin.")
