import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# --- SAYFA YAPILANDIRMASI ---
st.set_page_config(page_title="Vision Finans Terminali", layout="wide")

# --- AYDINLIK TEMA (CSS) ---
st.markdown("""
    <style>
    /* Ana arka plan */
    .stApp { 
        background-color: #f8f9fa; 
        color: #2c3e50; 
    }
    /* Metrik Kartları - Aydınlık ve Gölgeli */
    .metric-card {
        background-color: #ffffff;
        padding: 20px;
        border-radius: 12px;
        border: 1px solid #e9ecef;
        text-align: center;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        margin-bottom: 10px;
    }
    .metric-card h2 { color: #1a73e8; margin: 0; }
    .metric-card p { color: #6c757d; margin: 0; font-size: 0.9rem; }
    
    /* Yan Panel */
    section[data-testid="stSidebar"] {
        background-color: #ffffff !important;
        border-right: 1px solid #dee2e6;
    }
    /* Butonlar */
    .stButton>button {
        border-radius: 8px;
        background-color: #f1f3f4;
        color: #3c4043;
        border: 1px solid #dadce0;
        font-weight: 500;
    }
    .stButton>button:hover {
        background-color: #1a73e8;
        color: white;
    }
    </style>
    """, unsafe_allow_html=True)

# --- SIDEBAR: DİNAMİK LİSTE ---
with st.sidebar:
    st.title("🛡️ Vision Pro")
    st.subheader("⭐ İzleme Listesi")
    default_list = "THYAO.IS, EREGL.IS, SISE.IS, BTC-USD, GC=F"
    user_list_input = st.text_area("Hisseleri virgülle ayırın:", value=default_list)
    izleme_listesi = [x.strip().upper() for x in user_list_input.split(",")]
    
    if 'secilen_hisse' not in st.session_state:
        st.session_state.secilen_hisse = izleme_listesi[0]

    st.markdown("---")
    cols = st.columns(2)
    for i, f in enumerate(izleme_listesi):
        if cols[i % 2].button(f):
            st.session_state.secilen_hisse = f
    
    periyot = st.selectbox("📅 Dönem", ["1mo", "3mo", "6mo", "1y", "2y", "5y"], index=2)

# --- VERİ İŞLEME VE GÜVENLİ HACİM HESABI ---
@st.cache_data(ttl=300)
def verileri_getir(symbol, period):
    try:
        data = yf.download(symbol, period=period)
        if data.empty: return None
        data['MA20'] = data['Close'].rolling(window=20).mean()
        data['RSI'] = 100 - (100 / (1 + (data['Close'].diff().where(data['Close'].diff() > 0, 0).rolling(14).mean() / 
                                        -data['Close'].diff().where(data['Close'].diff() < 0, 0).rolling(14).mean())))
        return data
    except:
        return None

df = verileri_getir(st.session_state.secilen_hisse, periyot)

if df is not None:
    # Verileri Güvenli Sayıya Çevirme
    def to_float(val):
        try: return float(val.iloc[0]) if hasattr(val, 'iloc') else float(val)
        except: return 0.0

    son_fiyat = to_float(df['Close'].iloc[-1])
    onceki_fiyat = to_float(df['Close'].iloc[-2])
    degisim = ((son_fiyat - onceki_fiyat) / onceki_fiyat) * 100
    hacim = to_float(df['Volume'].iloc[-1])
    rsi_son = to_float(df['RSI'].iloc[-1])

    st.subheader(f"📈 {st.session_state.secilen_hisse} Analiz Paneli")
    
    # Metrik Kartları
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(f"<div class='metric-card'><p>Son Fiyat</p><h2>{son_fiyat:,.2f}</h2><p style='color:{'#28a745' if degisim>0 else '#dc3545'}'>{degisim:+.2f}%</p></div>", unsafe_allow_html=True)
    with c2:
        st.markdown(f"<div class='metric-card'><p>RSI (14)</p><h2 style='color:#6f42c1'>{rsi_son:.1f}</h2><p>{'Pahalı' if rsi_son>70 else 'Ucuz' if rsi_son<30 else 'Normal'}</p></div>", unsafe_allow_html=True)
    with c3:
        st.markdown(f"<div class='metric-card'><p>Hacim</p><h2 style='color:#17a2b8'>{hacim:,.0f}</h2><p>Adet</p></div>", unsafe_allow_html=True)
    with c4:
        st.markdown(f"<div class='metric-card'><p>20G Ort.</p><h2 style='color:#fd7e14'>{to_float(df['MA20'].iloc[-1]):,.2f}</h2><p>Destek</p></div>", unsafe_allow_html=True)

    # --- GRAFİK ---
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.1, row_heights=[0.7, 0.3])
    
    # Aydınlık Temaya Uygun Mum Grafiği
    fig.add_trace(go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'],
                                increasing_line_color='#28a745', decreasing_line_color='#dc3545', name="Fiyat"), row=1, col=1)
    
    fig.add_trace(go.Scatter(x=df.index, y=df['MA20'], name="MA20", line=dict(color='#fd7e14', width=2)), row=1, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=df['RSI'], name="RSI", line=dict(color='#6f42c1', width=2)), row=2, col=1)

    fig.update_layout(height=600, template="plotly_white", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                      xaxis_rangeslider_visible=False, margin=dict(l=0, r=0, t=0, b=0))
    
    st.plotly_chart(fig, use_container_width=True)

else:
    st.error("Sembol bulunamadı. Lütfen kontrol edin.")
