import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# --- SAYFA YAPILANDIRMASI ---
st.set_page_config(page_title="Vision Finans Terminali", layout="wide")

# --- ÖNEMLİ: BURAYI KENDİ HİSSELERİNLE BİR KEZ GÜNCELLE ---
# Bu liste, sayfa her sıfırlandığında gelecek olan senin "ana listen" olacak.
KENDI_ANA_LISTEM = "THYAO.IS, EREGL.IS, SISE.IS, BTC-USD, GC=F, FROTO.IS"

# --- TEMA VE STİL ---
st.markdown("""
    <style>
    .stApp { background-color: #f8f9fa; }
    .metric-card {
        background-color: #ffffff; padding: 20px; border-radius: 12px;
        border: 1px solid #e9ecef; text-align: center; box-shadow: 0 4px 6px rgba(0,0,0,0.05);
    }
    .signal-box {
        padding: 20px; border-radius: 12px; color: white; text-align: center;
        font-weight: bold; font-size: 1.1rem; margin-bottom: 15px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- SIDEBAR (YAN PANEL) ---
with st.sidebar:
    st.title("🛡️ Vision Pro")
    
    # Kullanıcı listesini session_state'e alıyoruz ki uygulama içinde kaybolmasın
    if 'my_list' not in st.session_state:
        st.session_state.my_list = KENDI_ANA_LISTEM

    st.subheader("⭐ İzleme Listeni Yönet")
    user_list_input = st.text_area("Hisseleri virgülle ayırarak düzenle:", 
                                   value=st.session_state.my_list,
                                   help="Eklediğin hisseler bu oturum boyunca saklanır.")
    
    # Listeyi güncelle butonu
    if st.button("Listeyi Uygula"):
        st.session_state.my_list = user_list_input
        st.rerun()

    izleme_listesi = [x.strip().upper() for x in st.session_state.my_list.split(",")]
    
    if 'secilen_hisse' not in st.session_state:
        st.session_state.secilen_hisse = izleme_listesi[0]

    st.markdown("---")
    st.write("📍 **Hızlı Geçiş:**")
    cols = st.columns(2)
    for i, f in enumerate(izleme_listesi):
        if cols[i % 2].button(f, key=f"btn_{f}"):
            st.session_state.secilen_hisse = f
    
    st.markdown("---")
    periyot = st.selectbox("📅 Dönem", ["1mo", "3mo", "6mo", "1y", "2y", "5y"], index=2)

# --- VERİ VE ANALİZ (AYNI KALIYOR) ---
@st.cache_data(ttl=300)
def verileri_getir(symbol, period):
    try:
        data = yf.download(symbol, period=period)
        if data.empty: return None
        data['MA20'] = data['Close'].rolling(window=20).mean()
        data['MA50'] = data['Close'].rolling(window=50).mean()
        delta = data['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        data['RSI'] = 100 - (100 / (1 + (gain / loss)))
        return data
    except: return None

df = verileri_getir(st.session_state.secilen_hisse, periyot)

# ... (Geri kalan görselleştirme ve öneri kodları buraya gelecek)
if df is not None:
    def to_float(val):
        try: return float(val.iloc[0]) if hasattr(val, 'iloc') else float(val)
        except: return 0.0

    son_fiyat = to_float(df['Close'].iloc[-1])
    rsi_son = to_float(df['RSI'].iloc[-1])
    ma20_son = to_float(df['MA20'].iloc[-1])

    # Sinyal Bölümü
    if rsi_son < 35:
        st.markdown(f"<div class='signal-box' style='background-color:#28a745'>🚀 GÜÇLÜ AL SİNYALİ</div>", unsafe_allow_html=True)
    elif rsi_son > 70:
        st.markdown(f"<div class='signal-box' style='background-color:#dc3545'>⚠️ DİKKAT: AŞIRI ALIM</div>", unsafe_allow_html=True)
    else:
        st.markdown(f"<div class='signal-box' style='background-color:#6c757d'>⚖️ NÖTR: İZLEMEDE KAL</div>", unsafe_allow_html=True)

    # Grafik Çizimi
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.1, row_heights=[0.7, 0.3])
    fig.add_trace(go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'], name="Fiyat"), row=1, col=1)
    fig.update_layout(height=600, template="plotly_white", xaxis_rangeslider_visible=False)
    st.plotly_chart(fig, use_container_width=True)
