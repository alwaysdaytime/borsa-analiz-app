import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# --- 1. AYARLAR ---
st.set_page_config(page_title="Vision Pro Terminal", layout="wide")

# --- 2. SENİN ÖZEL LİSTEN (BURAYI BİR KEZ DÜZENLE) ---
# Buraya yazdığın hisseler senin "Kalıcı Listen" olacak.
# Uygulama her sıfırlandığında bu liste geri gelir.
FENOMEN_LISTE = "THYAO.IS, EREGL.IS, SISE.IS, ASTOR.IS, SASA.IS, BTC-USD, GC=F"

# --- 3. TASARIM (MODERN & AYDINLIK) ---
st.markdown("""
    <style>
    .stApp { background-color: #fcfcfc; }
    .compact-card {
        background: white; padding: 12px; border-radius: 10px;
        border: 1px solid #edf2f7; text-align: center;
        box-shadow: 0 2px 4px rgba(0,0,0,0.04);
    }
    .compact-card h4 { margin: 0; font-size: 0.75rem; color: #718096; text-transform: uppercase; }
    .compact-card h2 { margin: 4px 0; font-size: 1.3rem; color: #2d3748; }
    .kademe-box {
        background: #ffffff; padding: 15px; border-radius: 10px;
        border: 1px solid #e2e8f0; font-family: 'Courier New', monospace;
    }
    .stButton>button { border-radius: 6px; height: 38px; border: 1px solid #e2e8f0; }
    .signal-tag {
        padding: 5px 12px; border-radius: 20px; font-size: 0.85rem; font-weight: 600;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 4. HAFIZA YÖNETİMİ (PERSISTENCE) ---
if 'my_list' not in st.session_state:
    st.session_state.my_list = FENOMEN_LISTE

# --- 5. SIDEBAR (YAN PANEL) ---
with st.sidebar:
    st.title("🛡️ Vision Terminal")
    st.markdown("---")
    
    st.subheader("⭐ Takip Listeni Yönet")
    user_input = st.text_area("Hisseleri virgülle ayır:", value=st.session_state.my_list, height=100)
    
    if st.button("💾 Listeyi Sisteme Kaydet", use_container_width=True):
        st.session_state.my_list = user_input
        st.success("Liste güncellendi!")
        st.rerun()

    current_list = [x.strip().upper() for x in st.session_state.my_list.split(",")]
    
    if 'active_ticker' not in st.session_state:
        st.session_state.active_ticker = current_list[0]

    st.markdown("---")
    st.write("📍 **Hızlı Erişim**")
    for ticker in current_list:
        if st.button(f"📊 {ticker}", use_container_width=True):
            st.session_state.active_ticker = ticker

    st.markdown("---")
    period = st.selectbox("Zaman Dilimi", ["1mo", "3mo", "6mo", "1y", "2y"], index=1)

# --- 6. VERİ ANALİZ MOTORU ---
@st.cache_data(ttl=60)
def fetch_data(symbol, prd):
    try:
        data = yf.download(symbol, period=prd)
        if data.empty: return None
        data['MA20'] = data['Close'].rolling(20).mean()
        data['MA50'] = data['Close'].rolling(50).mean()
        # RSI
        change = data['Close'].diff()
        up = change.clip(lower=0).rolling(14).mean()
        down = -change.clip(upper=0).rolling(14).mean()
        data['RSI'] = 100 - (100 / (1 + (up / down)))
        return data
    except: return None

df = fetch_data(st.session_state.active_ticker, period)

# --- 7. EKRAN ÇIKTISI ---
if df is not None:
    def safe_val(val):
        try:
            v = val.iloc[-1] if hasattr(val, 'iloc') else val
            return float(v.iloc[0]) if hasattr(v, 'iloc') else float(v)
        except: return 0.0

    last_price = safe_val(df['Close'])
    rsi_val = safe_val(df['RSI'])
    ma20 = safe_val(df['MA20'])
    vol = safe_val(df['Volume'])

    # Başlık ve Sinyal
    c_title, c_sig = st.columns([3, 1])
    with c_title:
        st.subheader(f"🚀 {st.session_state.active_ticker} Teknik Görünüm")
    with c_sig:
        if rsi_val < 35: st.markdown("<span class='signal-tag' style='background:#c6f6d5; color:#22543d;'>🟢 GÜÇLÜ AL</span>", unsafe_allow_html=True)
        elif rsi_val > 65: st.markdown("<span class='signal-tag' style='background:#fed7d7; color:#822727;'>🔴 GÜÇLÜ SAT</span>", unsafe_allow_html=True)
        else: st.markdown("<span class='signal-tag' style='background:#edf2f7; color:#2d3748;'>⚪ NÖTR</span>", unsafe_allow_html=True)

    # Üst Bilgi Paneli
    col_info, col_depth = st.columns([3, 1])
    
    with col_info:
        m1, m2, m3, m4 = st.columns(4)
        m1.markdown(f"<div class='compact-card'><h4>Fiyat</h4><h2>{last_price:,.2f}</h2></div>", unsafe_allow_html=True)
        m2.markdown(f"<div class='compact-card'><h4>RSI</h4><h2>{rsi_val:.1f}</h2></div>", unsafe_allow_html=True)
        m3.markdown(f"<div class='compact-card'><h4>MA20</h4><h2>{ma20:,.2f}</h2></div>", unsafe_allow_html=True)
        m4.markdown(f"<div class='compact-card'><h4>Hacim</h4><h2>{vol/1e6:.1f}M</h2></div>", unsafe_allow_html=True)

    with col_depth:
        st.markdown("<div class='kademe-box'>" + 
                    f"<b style='color:#4a5568'>KADEMELER</b><br>" + 
                    f"<span style='color:#38a169'>Dir: {last_price*1.02:,.2f}</span><br>" +
                    f"<span style='color:#718096'>Piv: {last_price:,.2f}</span><br>" +
                    f"<span style='color:#e53e3e'>Des: {last_price*0.98:,.2f}</span></div>", unsafe_allow_html=True)

    # Grafik
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.07, row_heights=[0.8, 0.2])
    fig.add_trace(go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'], name="Fiyat"), row=1, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=df['MA20'], name="MA20", line=dict(color='#ed8936', width=1.5)), row=1, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=df['RSI'], name="RSI", line=dict(color='#805ad5', width=1.5)), row=2, col=1)
    fig.update_layout(height=500, template="plotly_white", xaxis_rangeslider_visible=False, margin=dict(l=0,r=0,t=0,b=0))
    st.plotly_chart(fig, use_container_width=True)

else:
    st.warning("Veri bekleniyor... Lütfen listeden bir hisse seçin veya sembolü kontrol edin.")
