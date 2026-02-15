import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# --- SAYFA YAPILANDIRMASI ---
st.set_page_config(page_title="Vision Finans Terminali", layout="wide", initial_sidebar_state="expanded")

# --- ÖZEL TASARIM (CSS) ---
st.markdown("""
    <style>
    .stApp { background-color: #0b0e14; color: #e1e1e1; }
    .metric-card {
        background-color: #161b22;
        padding: 20px;
        border-radius: 12px;
        border: 1px solid #30363d;
        text-align: center;
    }
    .stButton>button {
        width: 100%;
        border-radius: 8px;
        background-color: #21262d;
        color: white;
        border: 1px solid #30363d;
    }
    .stButton>button:hover {
        background-color: #238636;
        border-color: #2ea043;
    }
    </style>
    """, unsafe_allow_html=True)

# --- SIDEBAR: İZLEME LİSTESİ VE AYARLAR ---
with st.sidebar:
    st.title("🛡️ Vision Terminal")
    st.markdown("---")
    
    st.subheader("⭐ İzleme Listesi")
    # Favori hisseler için butonlar
    favoriler = ["THYAO.IS", "EREGL.IS", "ASELS.IS", "BTC-USD", "GC=F", "USDTRY=X"]
    
    # Butonlarla hızlı seçim mekanizması
    if 'secilen_hisse' not in st.session_state:
        st.session_state.secilen_hisse = "THYAO.IS"

    for f in favoriler:
        if st.button(f):
            st.session_state.secilen_hisse = f
    
    st.markdown("---")
    manuel_sembol = st.text_input("🔍 Manuel Sembol Ara", value=st.session_state.secilen_hisse).upper()
    periyot = st.selectbox("📅 Analiz Dönemi", ["1mo", "3mo", "6mo", "1y", "2y", "5y"], index=2)

# --- VERİ İŞLEME ---
@st.cache_data(ttl=300)
def verileri_getir(symbol, period):
    data = yf.download(symbol, period=period)
    if data.empty: return None
    # Hesaplamalar
    data['MA20'] = data['Close'].rolling(window=20).mean()
    data['MA50'] = data['Close'].rolling(window=50).mean()
    delta = data['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    data['RSI'] = 100 - (100 / (1 + (gain / loss)))
    return data

df = verileri_getir(manuel_sembol, periyot)

if df is not None:
    # --- ÜST BİLGİ PANELİ ---
    son_fiyat = float(df['Close'].iloc[-1])
    onceki_fiyat = float(df['Close'].iloc[-2])
    degisim = ((son_fiyat - onceki_fiyat) / onceki_fiyat) * 100
    rsi_son = float(df['RSI'].iloc[-1])

    st.header(f"📈 {manuel_sembol} Teknik Analiz Görünümü")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f"<div class='metric-card'><h5>Fiyat</h5><h2>{son_fiyat:,.2f}</h2><p style='color:{'#2ea043' if degisim>0 else '#f85149'}'>{degisim:+.2f}%</p></div>", unsafe_allow_html=True)
    with col2:
        st.markdown(f"<div class='metric-card'><h5>RSI (14)</h5><h2>{rsi_son:.1f}</h2><p>{'Aşırı Alım' if rsi_son>70 else 'Aşırı Satım' if rsi_son<30 else 'Nötr'}</p></div>", unsafe_allow_html=True)
    with col3:
        st.markdown(f"<div class='metric-card'><h5>20G Ort.</h5><h2>{float(df['MA20'].iloc[-1]):,.2f}</h2><p>Trend Desteği</p></div>", unsafe_allow_html=True)
    with col4:
        st.markdown(f"<div class='metric-card'><h5>Zirve (Periyot)</h5><h2>{df['High'].max().iloc[0]:,.2f}</h2><p>Direnç Seviyesi</p></div>", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # --- GRAFİK ALANI ---
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.08, row_heights=[0.75, 0.25])

    # Mum Grafiği
    fig.add_trace(go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'], name="Fiyat"), row=1, col=1)
    
    # Hareketli Ortalamalar
    fig.add_trace(go.Scatter(x=df.index, y=df['MA20'], name="MA20 (Kısa)", line=dict(color='#ffaa00', width=1.5)), row=1, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=df['MA50'], name="MA50 (Uzun)", line=dict(color='#00aaff', width=1.5)), row=1, col=1)

    # RSI Grafiği
    fig.add_trace(go.Scatter(x=df.index, y=df['RSI'], name="RSI", line=dict(color='#a371f7', width=2)), row=2, col=1)
    fig.add_hline(y=70, line_dash="dash", line_color="#f85149", row=2, col=1)
    fig.add_hline(y=30, line_dash="dash", line_color="#2ea043", row=2, col=1)

    fig.update_layout(height=700, template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                      xaxis_rangeslider_visible=False, margin=dict(l=10, r=10, t=10, b=10))
    
    st.plotly_chart(fig, use_container_width=True)

    # --- ANALİZ ÖZETİ ---
    with st.expander("📝 Detaylı Algoritma Yorumu"):
        c1, c2 = st.columns(2)
        with c1:
            if son_fiyat > df['MA20'].iloc[-1]:
                st.success("✅ Fiyat MA20 üzerinde: Kısa vadeli trend pozitif.")
            else:
                st.error("❌ Fiyat MA20 altında: Kısa vadeli baskı devam ediyor.")
        with c2:
            if rsi_son < 40:
                st.warning("ℹ️ RSI düşük seviyelerde: Toplama bölgesi olabilir.")
            elif rsi_son > 60:
                st.warning("ℹ️ RSI yüksek seviyelerde: Kar satışı beklenebilir.")

else:
    st.error("⚠️ Veri bulunamadı. Sembolün doğruluğundan emin olun (Örn: EREGL.IS veya BTC-USD).")
