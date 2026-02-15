import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta

# Sayfa Genişliği ve Başlık
st.set_page_config(page_title="PRO Finans Paneli", layout="wide", initial_sidebar_state="expanded")

# --- CSS İLE GÖRSEL GÜZELLEŞTİRME ---
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    .stMetric { background-color: #1e2130; padding: 15px; border-radius: 10px; border: 1px solid #31333f; }
    .stAlert { border-radius: 10px; }
    div[data-testid="stExpander"] { border: none; background-color: #1e2130; border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

# --- SIDEBAR (YAN PANEL) ---
with st.sidebar:
    st.title("🚀 Finans Analiz")
    st.markdown("---")
    sembol = st.text_input("Hisse/Varlık Sembolü", value="THYAO.IS").upper()
    
    st.subheader("📅 Analiz Ayarları")
    periyot = st.selectbox("Zaman Aralığı", ["1mo", "3mo", "6mo", "1y", "2y", "5y", "max"], index=2)
    grafik_turu = st.radio("Grafik Tipi", ["Mum Grafiği", "Çizgi Grafiği"])
    
    st.markdown("---")
    st.info("İpucu: BIST hisseleri için sonuna '.IS' ekleyin (Örn: EREGL.IS)")

# --- VERİ ÇEKME FONKSİYONU ---
@st.cache_data
def veri_yukle(symbol, period):
    try:
        data = yf.download(symbol, period=period)
        return data
    except:
        return None

df = veri_yukle(sembol, periyot)

if df is not None and not df.empty:
    # --- HESAPLAMALAR ---
    df['MA20'] = df['Close'].rolling(window=20).mean()
    df['MA50'] = df['Close'].rolling(window=50).mean()
    
    # RSI
    delta = df['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    df['RSI'] = 100 - (100 / (1 + (gain / loss)))

    # --- ÜST PANEL: METRİKLER ---
    son_fiyat = float(df['Close'].iloc[-1])
    onceki_fiyat = float(df['Close'].iloc[-2])
    degisim = ((son_fiyat - onceki_fiyat) / onceki_fiyat) * 100
    hacim = df['Volume'].iloc[-1]

    st.title(f"📊 {sembol} Analiz Paneli")
    
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Anlık Fiyat", f"{son_fiyat:,.2f}", f"{degisim:+.2f}%")
    m2.metric("Günlük Hacim", f"{hacim:,.0f}")
    m3.metric("RSI (14)", f"{df['RSI'].iloc[-1]:.1f}")
    m4.metric("20 Günlük Ort.", f"{df['MA20'].iloc[-1]:,.2f}")

    st.markdown("---")

    # --- ANA GÖVDE: GRAFİK VE ANALİZ ---
    col_grafik, col_analiz = st.columns([3, 1])

    with col_grafik:
        # Alt alta iki grafik (Fiyat ve RSI)
        fig = make_subplots(rows=2, cols=1, shared_xaxes=True, 
                            vertical_spacing=0.05, row_heights=[0.7, 0.3])

        if grafik_turu == "Mum Grafiği":
            fig.add_trace(go.Candlestick(x=df.index, open=df['Open'], high=df['High'],
                          low=df['Low'], close=df['Close'], name="Fiyat"), row=1, col=1)
        else:
            fig.add_trace(go.Scatter(x=df.index, y=df['Close'], name="Fiyat", line=dict(color='#00ffcc', width=2)), row=1, col=1)

        # Ortalamalar
        fig.add_trace(go.Scatter(x=df.index, y=df['MA20'], name="MA20", line=dict(color='orange', width=1)), row=1, col=1)
        fig.add_trace(go.Scatter(x=df.index, y=df['MA50'], name="MA50", line=dict(color='#ff00ff', width=1)), row=1, col=1)

        # RSI
        fig.add_trace(go.Scatter(x=df.index, y=df['RSI'], name="RSI", line=dict(color='#6666ff')), row=2, col=1)
        fig.add_hline(y=70, line_dash="dash", line_color="red", row=2, col=1)
        fig.add_hline(y=30, line_dash="dash", line_color="green", row=2, col=1)

        fig.update_layout(height=600, template="plotly_dark", 
                          margin=dict(l=0, r=0, t=0, b=0),
                          legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
        fig.update_xaxes(rangeslider_visible=False)
        st.plotly_chart(fig, use_container_width=True)

    with col_analiz:
        st.subheader("🤖 Zeka Notları")
        rsi_degeri = df['RSI'].iloc[-1]
        
        if rsi_degeri < 35:
            st.success("✅ **ALIM FIRSATI?**\nRSI aşırı satım bölgesine yakın. Hisse ucuzlamış olabilir.")
        elif rsi_degeri > 65:
            st.error("⚠️ **DİKKAT!**\nRSI aşırı alım bölgesinde. Kar satışı gelebilir.")
        else:
            st.info("⚖️ **NÖTR BÖLGE**\nFiyat şu an denge noktasında. Kırılım beklenmeli.")

        with st.expander("📌 Teknik Özet"):
            st.write(f"**MA20 Durumu:** {'Üstünde' if son_fiyat > df['MA20'].iloc[-1] else 'Altında'}")
            st.write(f"**Periyot Başı:** {df['Close'].iloc[0]:.2f}")
            st.write(f"**En Yüksek:** {df['High'].max().iloc[0]:.2f}")
            st.write(f"**En Düşük:** {df['Low'].min().iloc[0]:.2f}")

else:
    st.warning("⚠️ Lütfen geçerli bir sembol girin (Örn: BTC-USD, AAPL, THYAO.IS)")
    st.image("https://via.placeholder.com/800x400.png?text=Veri+Bekleniyor...", use_container_width=True)
