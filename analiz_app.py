import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# --- 1. SAYFA VE TEMA AYARLARI ---
st.set_page_config(page_title="Vision AI | Gemini Edition", layout="wide")

# Liste Kalıcılığı
if 'my_list' not in st.session_state:
    st.session_state.my_list = "THYAO.IS, SISE.IS, ASTOR.IS, BTC-USD, ETH-USD, GC=F"

# --- 2. GEMINI SIGNATURE UI (CSS) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;500;700&display=swap');
    
    html, body, [class*="st-"] { font-family: 'Space Grotesk', sans-serif; }
    .stApp { background: linear-gradient(135deg, #f8faff 0%, #eff2ff 100%); }
    
    /* Gemini Stil Karar Kartı */
    .gemini-card {
        background: rgba(255, 255, 255, 0.7);
        backdrop-filter: blur(15px);
        border-radius: 24px;
        padding: 25px;
        border: 1px solid rgba(255, 255, 255, 0.4);
        box-shadow: 0 20px 40px rgba(0,0,0,0.05);
        margin-bottom: 30px;
    }
    
    .status-text {
        font-size: 2.2rem; font-weight: 700; 
        background: linear-gradient(90deg, #4285f4, #9b72f3, #d96570);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    }
    
    /* Neon İndikatörler */
    .stat-pill {
        background: white; border-radius: 16px; padding: 15px;
        border: 1px solid #eef2ff; text-align: center;
        transition: transform 0.3s ease;
    }
    .stat-pill:hover { transform: translateY(-5px); box-shadow: 0 10px 20px rgba(66,133,244,0.1); }
    
    /* Sidebar Modernizasyonu */
    section[data-testid="stSidebar"] { background-color: #ffffff; border-right: 1px solid #f0f2f6; }
    .stButton>button {
        border-radius: 12px; border: none; background: #f0f4ff; color: #4285f4;
        font-weight: 600; transition: 0.3s;
    }
    .stButton>button:hover { background: #4285f4; color: white; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. ANALİZ MOTORU (AI LOGIC) ---
@st.cache_data(ttl=60)
def get_gemini_data(symbol):
    try:
        data = yf.download(symbol, period="1y", interval="1d")
        if data.empty: return None
        # Teknik Katmanlar
        data['MA20'] = data['Close'].rolling(20).mean()
        data['MA50'] = data['Close'].rolling(50).mean()
        # Bollinger
        std = data['Close'].rolling(20).std()
        data['Up'] = data['MA20'] + (std * 2)
        data['Low'] = data['MA20'] - (std * 2)
        # MACD
        ema12 = data['Close'].ewm(span=12).mean()
        ema26 = data['Close'].ewm(span=26).mean()
        data['MACD'] = ema12 - ema26
        data['Sig'] = data['MACD'].ewm(span=9).mean()
        data['Hist'] = data['MACD'] - data['Sig']
        # RSI
        delta = data['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
        data['RSI'] = 100 - (100 / (1 + (gain / loss)))
        return data
    except: return None

# --- 4. SIDEBAR VE NAVİGASYON ---
with st.sidebar:
    st.markdown("<h1 style='color:#4285f4;'>Vision AI</h1>", unsafe_allow_html=True)
    st.markdown("---")
    
    new_list = st.text_area("Hisse Portföyün", value=st.session_state.my_list, height=100)
    if st.button("Sistemi Senkronize Et"):
        st.session_state.my_list = new_list
        st.rerun()
    
    tickers = [x.strip().upper() for x in st.session_state.my_list.split(",")]
    if 'active_ticker' not in st.session_state: st.session_state.active_ticker = tickers[0]
    
    st.markdown("### ✨ Aktif Takipler")
    for t in tickers:
        active = t == st.session_state.active_ticker
        if st.button(f"{'💠 ' if active else ''}{t}", use_container_width=True):
            st.session_state.active_ticker = t
            st.rerun()

df = get_gemini_data(st.session_state.active_ticker)

# --- 5. MAIN UI ---
if df is not None:
    def sn(s): return float(s.iloc[-1])
    p, rsi, hist, m20, m50 = sn(df['Close']), sn(df['RSI']), sn(df['Hist']), sn(df['MA20']), sn(df['MA50'])

    # AI Karar Algoritması
    score = 0
    if rsi < 35: score += 2
    if rsi > 65: score -= 2
    if p > m20: score += 1
    if hist > 0: score += 1
    if m20 > m50: score += 1 # Golden Cross Trendi
    
    if score >= 3: status, sub = "Strong Buy", "Yapay zeka güçlü yükseliş potansiyeli saptadı."
    elif score <= -3: status, sub = "Strong Sell", "Yapay zeka ciddi geri çekilme riski saptadı."
    else: status, sub = "Neutral", "Piyasa şu an karar aşamasında, stabilite gözlemleniyor."

    # Gemini Karar Kartı
    st.markdown(f"""
        <div class="gemini-card">
            <div style="font-size:0.9rem; color:#6b7280; font-weight:500;">{st.session_state.active_ticker} ANALİZİ</div>
            <div class="status-text">{status}</div>
            <div style="color:#4b5563; font-size:1.1rem; margin-top:5px;">{sub}</div>
        </div>
    """, unsafe_allow_html=True)

    # İstatistik Paneli
    c1, c2, c3, c4 = st.columns(4)
    with c1: st.markdown(f"<div class='stat-pill'><small>Fiyat</small><br><b>{p:,.2f}</b></div>", unsafe_allow_html=True)
    with c2: st.markdown(f"<div class='stat-pill'><small>RSI (14)</small><br><b>{rsi:.1f}</b></div>", unsafe_allow_html=True)
    with c3: st.markdown(f"<div class='stat-pill'><small>Momentum</small><br><b>{hist:.2f}</b></div>", unsafe_allow_html=True)
    with c4: st.markdown(f"<div class='stat-pill'><small>MA20</small><br><b>{m20:,.2f}</b></div>", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # --- GEMINI DYNAMIC CHART ---
    # Grafik alanını daha sofistike ve geniş hale getiriyoruz
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.04, row_heights=[0.75, 0.25])
    
    # Mum Grafiği
    fig.add_trace(go.Candlestick(
        x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'],
        increasing_line_color='#4285f4', decreasing_line_color='#ea4335',
        increasing_fillcolor='rgba(66,133,244,0.3)', decreasing_fillcolor='rgba(234,67,53,0.3)'
    ), row=1, col=1)
    
    # Hareketli Ortalamalar
    fig.add_trace(go.Scatter(x=df.index, y=df['MA20'], line=dict(color='#9b72f3', width=2), name="Trend"), row=1, col=1)
    
    # MACD Histogram (Soft Colors)
    h_colors = ['rgba(66,133,244,0.5)' if x >= 0 else 'rgba(234,67,53,0.5)' for x in df['Hist']]
    fig.add_trace(go.Bar(x=df.index, y=df['Hist'], marker_color=h_colors), row=2, col=1)

    # Grafik Modernizasyon Ayarları
    fig.update_layout(
        height=650, margin=dict(l=0, r=0, t=0, b=0),
        template="plotly_white", xaxis_rangeslider_visible=False,
        showlegend=False, hovermode="x unified",
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
        yaxis=dict(side="right", gridcolor="#f1f5f9", tickfont=dict(color="#94a3b8"))
    )
    
    # Anlık Fiyat Etiketi
    fig.add_hline(y=p, line_dash="dot", line_color="#9b72f3", opacity=0.5, row=1, col=1)

    st.plotly_chart(fig, use_container_width=True, config={'display
