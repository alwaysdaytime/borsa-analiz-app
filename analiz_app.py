import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

st.set_page_config(page_title="Pro Borsa Analiz", layout="wide")

# Kenar Çubuğu
st.sidebar.header("⚙️ Ayarlar")
sembol = st.sidebar.text_input("Hisse Sembolü (Örn: THYAO.IS)", value="THYAO.IS")
periyot = st.sidebar.selectbox("Zaman Aralığı", ["1mo", "3mo", "6mo", "1y", "2y", "5y"], index=2)

# Veri Çekme
@st.cache_data
def veri_indir(symbol, period):
    data = yf.download(symbol, period=period)
    return data

df = veri_indir(sembol, periyot)

if not df.empty:
    # --- TEKNİK HESAPLAMALAR ---
    # Hareketli Ortalamalar
    df['MA20'] = df['Close'].rolling(window=20).mean()
    df['MA50'] = df['Close'].rolling(window=50).mean()
    
    # RSI Hesaplama
    delta = df['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    df['RSI'] = 100 - (100 / (1 + rs))

    # --- HIZLI İSTATİSTİKLER (METRIC) ---
    son_fiyat = float(df['Close'].iloc[-1])
    onceki_fiyat = float(df['Close'].iloc[-2])
    degisim = ((son_fiyat - onceki_fiyat) / onceki_fiyat) * 100
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Son Fiyat", f"{son_fiyat:.2f} TL", f"{degisim:.2f}%")
    col2.metric("24s En Yüksek", f"{df['High'].max().iloc[0]:.2f} TL")
    col3.metric("24s En Düşük", f"{df['Low'].min().iloc[0]:.2f} TL")
    col4.metric("RSI (14)", f"{df['RSI'].iloc[-1]:.2f}")

    # --- OTOMATİK SİNYAL MEKANİZMASI ---
    st.subheader("🤖 Algoritmik Sinyal Notu")
    rsi_degeri = df['RSI'].iloc[-1]
    
    if rsi_degeri < 30:
        st.success("🔥 GÜÇLÜ AL: Hisse teknik olarak aşırı satım bölgesinde (Ucuz).")
    elif rsi_degeri > 70:
        st.error("⚠️ GÜÇLÜ SAT: Hisse teknik olarak aşırı alım bölgesinde (Pahalı).")
    elif son_fiyat > df['MA20'].iloc[-1]:
        st.info("⬆️ YÜKSELİŞ TRENDİ: Fiyat 20 günlük ortalamanın üzerinde.")
    else:
        st.warning("➗ NÖTR: Şu an net bir kırılım yok, izlemede kalınmalı.")

    # --- GELİŞMİŞ GRAFİK ---
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, 
                        vertical_spacing=0.1, row_heights=[0.7, 0.3])

    # Ana Fiyat Grafiği (Candlestick + MA)
    fig.add_trace(go.Candlestick(x=df.index, open=df['Open'], high=df['High'],
                                low=df['Low'], close=df['Close'], name="Mum Grafiği"), row=1, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=df['MA20'], line=dict(color='orange', width=1.5), name="MA20"), row=1, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=df['MA50'], line=dict(color='blue', width=1.5), name="MA50"), row=1, col=1)

    # RSI Grafiği
    fig.add_trace(go.Scatter(x=df.index, y=df['RSI'], line=dict(color='purple'), name="RSI"), row=2, col=1)
    fig.add_hline(y=70, line_dash="dash", line_color="red", row=2, col=1)
    fig.add_hline(y=30, line_dash="dash", line_color="green", row=2, col=1)

    fig.update_layout(height=600, template="plotly_dark", showlegend=True,
                      xaxis_rangeslider_visible=False)
    st.plotly_chart(fig, use_container_width=True)

else:
    st.error("Veri alınamadı. Lütfen sembolü kontrol edin.")
