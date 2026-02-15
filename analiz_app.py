import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# --- SAYFA YAPILANDIRMASI ---
st.set_page_config(page_title="Vision Finans Terminali", layout="wide", initial_sidebar_state="expanded")

# --- ÖZEL TASARIM (DAHA FERAH ARKA PLAN VE MODERN KARTLAR) ---
st.markdown("""
    <style>
    /* Arka planı daha yumuşak bir koyu mavi/gri tonuna çektik */
    .stApp { 
        background-color: #1a1c24; 
        color: #ffffff; 
    }
    /* Kart tasarımları */
    .metric-card {
        background: linear-gradient(145deg, #232732, #1c1f26);
        padding: 20px;
        border-radius: 15px;
        border: 1px solid #3d4455;
        text-align: center;
        box-shadow: 5px 5px 15px rgba(0,0,0,0.2);
    }
    /* Kenar çubuğu stili */
    section[data-testid="stSidebar"] {
        background-color: #111318 !important;
    }
    .stButton>button {
        border-radius: 20px;
        background-color: #2d323e;
        color: #00d4ff;
        border: 1px solid #3d4455;
        transition: all 0.3s;
    }
    .stButton>button:hover {
        background-color: #00d4ff;
        color: #111318;
        border-color: #00d4ff;
    }
    </style>
    """, unsafe_allow_html=True)

# --- SIDEBAR: DİNAMİK LİSTE YÖNETİMİ ---
with st.sidebar:
    st.title("🛡️ Vision Terminal")
    st.markdown("---")
    
    st.subheader("⭐ İzleme Listesini Düzenle")
    # Kullanıcının kendi listesini oluşturabileceği alan
    default_list = "THYAO.IS, EREGL.IS, ASELS.IS, BTC-USD, GC=F"
    user_list_input = st.text_area("Hisseleri virgül ile ekle/sil:", value=default_list)
    izleme_listesi = [x.strip().upper() for x in user_list_input.split(",")]
    
    st.markdown("---")
    st.subheader("📍 Hızlı Seçim")
    
    # Session state ile seçili hisseyi tutma
    if 'secilen_hisse' not in st.session_state:
        st.session_state.secilen_hisse = izleme_listesi[0]

    # Dinamik butonlar
    cols = st.columns(2) # Butonları yan yana koymak için
    for i, f in enumerate(izleme_listesi):
        if cols[i % 2].button(f):
            st.session_state.secilen_hisse = f
    
    st.markdown("---")
    periyot = st.selectbox("📅 Analiz Dönemi", ["1mo", "3mo", "6mo", "1y", "2y", "5y"], index=2)

# --- VERİ İŞLEME ---
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
    except:
        return None

df = verileri_getir(st.session_state.secilen_hisse, periyot)

if df is not None:
    son_fiyat = float(df['Close'].iloc[-1])
    onceki_fiyat = float(df['Close'].iloc[-2])
    degisim = ((son_fiyat - onceki_fiyat) / onceki_fiyat) * 100
    rsi_son = float(df['RSI'].iloc[-1])

    st.header(f"📈 {st.session_state.secilen_hisse} Teknik Analiz")
    
    # Üst Panel Kartları
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(f"<div class='metric-card'><p style='color:#aeb9cc'>Son Fiyat</p><h2 style='color:#00d4ff'>{son_fiyat:,.2f}</h2><p style='color:{'#00ff88' if degisim>0 else '#ff4b4b'}'>{degisim:+.2f}%</p></div>", unsafe_allow_html=True)
    with c2:
        st.markdown(f"<div class='metric-card'><p style='color:#aeb9cc'>RSI (14)</p><h2 style='color:#ffd700'>{rsi_son:.1f}</h2><p>{'Aşırı Alım' if rsi_son>70 else 'Aşırı Satım' if rsi_son<30 else 'Nötr'}</p></div>", unsafe_allow_html=True)
    with c3:
        st.markdown(f"<div class='metric-card'><p style='color:#aeb9cc'>20 Günlük Ort.</p><h2>{float(df['MA20'].iloc[-1]):,.2f}</h2><p>Trend Desteği</p></div>", unsafe_allow_html=True)
    with c4:
        st.markdown(f"<div class='metric-card'><p style='color:#aeb9cc'>Hacim</p><h2>{df['Volume'].iloc[-1]:,.0f}</h2><p>Günlük İşlem</p></div>", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # --- GRAFİK ALANI ---
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.08, row_heights=[0.75, 0.25])

    # Mum Grafiği (Renkleri daha canlı yaptık)
    fig.add_trace(go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'], 
                                increasing_line_color='#00ff88', decreasing_line_color='#ff4b4b', name="Fiyat"), row=1, col=1)
    
    # Ortalamalar
    fig.add_trace(go.Scatter(x=df.index, y=df['MA20'], name="MA20", line=dict(color='#ffaa00', width=2)), row=1, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=df['MA50'], name="MA50", line=dict(color='#00d4ff', width=2)), row=1, col=1)

    # RSI
    fig.add_trace(go.Scatter(x=df.index, y=df['RSI'], name="RSI", line=dict(color='#a371f7', width=2)), row=2, col=1)
    fig.add_hline(y=70, line_dash="dash", line_color="#ff4b4b", row=2, col=1)
    fig.add_hline(y=30, line_dash="dash", line_color="#00ff88", row=2, col=1)

    fig.update_layout(height=650, template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                      xaxis_rangeslider_visible=False, margin=dict(l=10, r=10, t=10, b=10))
    
    st.plotly_chart(fig, use_container_width=True)

    # Alt Bilgi Paneli
    with st.expander("📝 Strateji Notu"):
        st.write(f"Şu an **{st.session_state.secilen_hisse}** için teknik göstergeler inceleniyor. Fiyat 20 günlük ortalamanın {'üzerinde' if son_fiyat > df['MA20'].iloc[-1] else 'altında'} seyrediyor.")

else:
    st.error("⚠️ Veri alınamadı. Lütfen sembolleri kontrol edin.")
