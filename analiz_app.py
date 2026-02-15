import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# --- SAYFA AYARLARI ---
st.set_page_config(page_title="Vision Finans Terminali", layout="wide")

# --- BURAYI KENDİ HİSSELERİNLE DOLDUR (ASLA KAYBOLMAZ) ---
# Buraya yazdığın hisseler, uygulamanın ana kemiği olur.
VARSAYILAN_LISTEM = "THYAO.IS, EREGL.IS, SISE.IS, BTC-USD, GC=F, FROTO.IS"

# --- TASARIM (AYDINLIK TEMA) ---
st.markdown("""
    <style>
    .stApp { background-color: #f8f9fa; }
    .metric-card {
        background-color: #ffffff; padding: 15px; border-radius: 12px;
        border: 1px solid #e9ecef; text-align: center; box-shadow: 0 4px 6px rgba(0,0,0,0.05);
    }
    .signal-box {
        padding: 15px; border-radius: 10px; color: white; text-align: center;
        font-weight: bold; font-size: 1.1rem; margin-bottom: 15px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- SIDEBAR ---
with st.sidebar:
    st.title("🛡️ Vision Pro")
    
    # Hafıza yönetimi: Eğer kullanıcı henüz bir şey değiştirmediyse varsayılanı kullan
    if 'my_list' not in st.session_state:
        st.session_state.my_list = VARSAYILAN_LISTEM

    st.subheader("⭐ İzleme Listesini Düzenle")
    user_input = st.text_area("Hisseleri virgülle ayır (Örn: AAPL, TSLA):", 
                              value=st.session_state.my_list)
    
    if st.button("Listeyi Güncelle ve Kaydet"):
        st.session_state.my_list = user_input
        st.success("Liste oturuma kaydedildi!")

    izleme_listesi = [x.strip().upper() for x in st.session_state.my_list.split(",")]
    
    if 'secilen_hisse' not in st.session_state:
        st.session_state.secilen_hisse = izleme_listesi[0]

    st.markdown("---")
    st.write("📍 **Hızlı Seçim:**")
    # Butonları daha şık yan yana dizelim
    for f in izleme_listesi:
        if st.button(f"🔍 {f}", use_container_width=True):
            st.session_state.secilen_hisse = f
    
    st.markdown("---")
    periyot = st.selectbox("📅 Analiz Dönemi", ["1mo", "3mo", "6mo", "1y", "2y", "5y"], index=2)

# --- VERİ VE ANALİZ ---
@st.cache_data(ttl=300)
def verileri_getir(symbol, period):
    try:
        data = yf.download(symbol, period=period)
        if data.empty: return None
        data['MA20'] = data['Close'].rolling(window=20).mean()
        delta = data['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        data['RSI'] = 100 - (100 / (1 + (gain / loss)))
        return data
    except: return None

df = verileri_getir(st.session_state.secilen_hisse, periyot)

if df is not None:
    # Sayısal veri çevrimi
    def clean_val(val):
        return float(val.iloc[0]) if hasattr(val, 'iloc') else float(val)

    son_fiyat = clean_val(df['Close'].iloc[-1])
    rsi_son = clean_val(df['RSI'].iloc[-1])
    ma20_son = clean_val(df['MA20'].iloc[-1])

    st.subheader(f"📈 {st.session_state.secilen_hisse} Analiz Paneli")

    # --- AL/SAT ÖNERİSİ ---
    if rsi_son < 30:
        st.markdown(f"<div class='signal-box' style='background-color:#28a745'>🚀 GÜÇLÜ AL: RSI Çok Düşük</div>", unsafe_allow_html=True)
    elif rsi_son > 70:
        st.markdown(f"<div class='signal-box' style='background-color:#dc3545'>⚠️ DİKKAT: Aşırı Alım Bölgesi</div>", unsafe_allow_html=True)
    elif son_fiyat > ma20_son:
        st.markdown(f"<div class='signal-box' style='background-color:#17a2b8'>📈 TREND POZİTİF: MA20 Üzerinde</div>", unsafe_allow_html=True)
    else:
        st.markdown(f"<div class='signal-box' style='background-color:#6c757d'>⚖️ NÖTR: Beklemede Kal</div>", unsafe_allow_html=True)

    # --- METRİKLER ---
    c1, c2, c3 = st.columns(3)
    with c1: st.markdown(f"<div class='metric-card'><p>Fiyat</p><h2>{son_fiyat:,.2f}</h2></div>", unsafe_allow_html=True)
    with c2: st.markdown(f"<div class='metric-card'><p>RSI</p><h2>{rsi_son:.1f}</h2></div>", unsafe_allow_html=True)
    with c3: st.markdown(f"<div class='metric-card'><p>MA20</p><h2>{ma20_son:,.2f}</h2></div>", unsafe_allow_html=True)

    # --- GRAFİK ---
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.1, row_heights=[0.7, 0.3])
    fig.add_trace(go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'], name="Fiyat"), row=1, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=df['MA20'], name="MA20", line=dict(color='orange', width=2)), row=1, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=df['RSI'], name="RSI", line=dict(color='purple', width=2)), row=2, col=1)
    fig.update_layout(height=600, template="plotly_white", xaxis_rangeslider_visible=False)
    st.plotly_chart(fig, use_container_width=True)
else:
    st.error("Veri çekilemedi. Lütfen sembolü kontrol edin.")
