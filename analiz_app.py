import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# --- SAYFA YAPILANDIRMASI ---
st.set_page_config(page_title="Vision Finans Terminali", layout="wide")

# --- AYDINLIK TEMA VE ÖNERİ KUTUSU TASARIMI ---
st.markdown("""
    <style>
    .stApp { background-color: #f8f9fa; color: #2c3e50; }
    .metric-card {
        background-color: #ffffff;
        padding: 20px;
        border-radius: 12px;
        border: 1px solid #e9ecef;
        text-align: center;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
    }
    .signal-box {
        padding: 25px;
        border-radius: 15px;
        color: white;
        text-align: center;
        font-weight: bold;
        font-size: 1.2rem;
        margin-bottom: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- SIDEBAR ---
with st.sidebar:
    st.title("🛡️ Vision Pro")
    default_list = "THYAO.IS, EREGL.IS, SISE.IS, BTC-USD, GC=F"
    user_list_input = st.text_area("İzleme Listesini Düzenle:", value=default_list)
    izleme_listesi = [x.strip().upper() for x in user_list_input.split(",")]
    
    if 'secilen_hisse' not in st.session_state:
        st.session_state.secilen_hisse = izleme_listesi[0]

    st.markdown("---")
    cols = st.columns(2)
    for i, f in enumerate(izleme_listesi):
        if cols[i % 2].button(f):
            st.session_state.secilen_hisse = f
    periyot = st.selectbox("📅 Dönem", ["1mo", "3mo", "6mo", "1y", "2y", "5y"], index=2)

# --- VERİ İŞLEME ---
@st.cache_data(ttl=300)
def verileri_getir(symbol, period):
    try:
        data = yf.download(symbol, period=period)
        if data.empty: return None
        # MA20 ve MA50
        data['MA20'] = data['Close'].rolling(window=20).mean()
        data['MA50'] = data['Close'].rolling(window=50).mean()
        # RSI
        delta = data['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        data['RSI'] = 100 - (100 / (1 + (gain / loss)))
        return data
    except: return None

df = verileri_getir(st.session_state.secilen_hisse, periyot)

if df is not None:
    def to_float(val):
        try: return float(val.iloc[0]) if hasattr(val, 'iloc') else float(val)
        except: return 0.0

    son_fiyat = to_float(df['Close'].iloc[-1])
    rsi_son = to_float(df['RSI'].iloc[-1])
    ma20_son = to_float(df['MA20'].iloc[-1])
    ma50_son = to_float(df['MA50'].iloc[-1])

    st.subheader(f"📈 {st.session_state.secilen_hisse} Analiz ve Öneri Paneli")

    # --- YENİ BÖLÜM: ALIM-SATIM ÖNERİSİ ---
    st.markdown("### 🤖 Teknik Karar Destek Sistemi")
    
    # Karar Algoritması
    if rsi_son < 35:
        color = "#28a745" # Yeşil
        mesaj = "GÜÇLÜ AL: Hisse aşırı satım bölgesinde ve fiyat toparlanma eğiliminde."
    elif rsi_son > 70:
        color = "#dc3545" # Kırmızı
        mesaj = "GÜÇLÜ SAT: Hisse aşırı alım (pahalı) bölgesinde. Kar realizasyonu beklenebilir."
    elif son_fiyat > ma20_son and ma20_son > ma50_son:
        color = "#17a2b8" # Turkuaz
        mesaj = "ALIMI KORU: Pozitif trend devam ediyor. Destek seviyeleri üzerinde."
    elif son_fiyat < ma20_son:
        color = "#ffc107" # Sarı
        mesaj = "BEKLE / NÖTR: Fiyat kısa vadeli ortalamanın altında, zayıflık işareti."
    else:
        color = "#6c757d" # Gri
        mesaj = "İZLE: Net bir sinyal yok. Piyasa dengelenmeye çalışıyor."

    st.markdown(f"<div class='signal-box' style='background-color:{color}'>{mesaj}</div>", unsafe_allow_html=True)

    # --- METRİK KARTLARI ---
    c1, c2, c3, c4 = st.columns(4)
    c1.markdown(f"<div class='metric-card'><p>Son Fiyat</p><h2>{son_fiyat:,.2f}</h2></div>", unsafe_allow_html=True)
    c2.markdown(f"<div class='metric-card'><p>RSI (14)</p><h2>{rsi_son:.1f}</h2></div>", unsafe_allow_html=True)
    c3.markdown(f"<div class='metric-card'><p>20G Ort.</p><h2>{ma20_son:,.2f}</h2></div>", unsafe_allow_html=True)
    c4.markdown(f"<div class='metric-card'><p>50G Ort.</p><h2>{ma50_son:,.2f}</h2></div>", unsafe_allow_html=True)

    # --- GRAFİK ---
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.1, row_heights=[0.7, 0.3])
    fig.add_trace(go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'], name="Mum Grafiği"), row=1, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=df['MA20'], name="MA20", line=dict(color='#fd7e14', width=2)), row=1, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=df['RSI'], name="RSI", line=dict(color='#6f42c1', width=2)), row=2, col=1)
    fig.update_layout(height=600, template="plotly_white", xaxis_rangeslider_visible=False)
    st.plotly_chart(fig, use_container_width=True)

else:
    st.error("Veri alınamadı, lütfen sembolü kontrol edin.")
