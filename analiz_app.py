import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# --- 1. AYARLAR ---
st.set_page_config(page_title="Vision Pro Terminal", layout="wide")

# --- 2. KALICI LİSTE YAPILANDIRMASI ---
if 'my_list' not in st.session_state:
    st.session_state.my_list = "THYAO.IS, EREGL.IS, SISE.IS, ASTOR.IS, BTC-USD, GC=F"

# --- 3. ÖZEL CSS (MODERN FINTECH TEMASI) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600&display=swap');
    html, body, [class*="st-"] { font-family: 'Inter', sans-serif; }
    
    .stApp { background-color: #fcfdfe; }
    
    /* Üst Durum Şeridi */
    .status-bar {
        padding: 12px 25px;
        border-radius: 12px;
        color: white;
        font-weight: 600;
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 20px;
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
    }
    
    /* Modern Kart Tasarımı */
    .metric-container {
        background: white;
        border-radius: 16px;
        padding: 20px;
        border: 1px solid #f1f5f9;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
        text-align: center;
    }
    .metric-label { color: #64748b; font-size: 0.85rem; font-weight: 500; margin-bottom: 5px; }
    .metric-value { color: #1e293b; font-size: 1.5rem; font-weight: 700; }
    
    /* Yan Panel Butonları */
    .stButton>button {
        border-radius: 10px;
        border: 1px solid #e2e8f0;
        background-color: white;
        transition: all 0.2s ease;
    }
    .stButton>button:hover {
        border-color: #3b82f6;
        color: #3b82f6;
        background-color: #eff6ff;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 4. YAN PANEL ---
with st.sidebar:
    st.title("🛡️ Vision")
    st.markdown("<p style='color:#64748b; font-size:0.9rem;'>Finansal Analiz Terminali</p>", unsafe_allow_html=True)
    
    new_input = st.text_area("Takip Listesi", value=st.session_state.my_list, height=100)
    if st.button("💾 Kaydet"):
        st.session_state.my_list = new_input
        st.rerun()

    current_list = [x.strip().upper() for x in st.session_state.my_list.split(",")]
    if 'active_ticker' not in st.session_state:
        st.session_state.active_ticker = current_list[0]

    st.markdown("---")
    for ticker in current_list:
        is_active = ticker == st.session_state.active_ticker
        label = f"📍 {ticker}" if is_active else f"{ticker}"
        if st.button(label, use_container_width=True, key=f"btn_{ticker}"):
            st.session_state.active_ticker = ticker
            st.rerun()
    
    period = st.selectbox("Zaman Dilimi", ["1mo", "3mo", "6mo", "1y"], index=1)

# --- 5. VERİ MOTORU ---
@st.cache_data(ttl=60)
def get_clean_data(symbol, prd):
    try:
        data = yf.download(symbol, period=prd)
        if data.empty: return None
        data['MA20'] = data['Close'].rolling(20).mean()
        # RSI
        delta = data['Close'].diff()
        up = delta.clip(lower=0).rolling(14).mean()
        down = -delta.clip(upper=0).rolling(14).mean()
        data['RSI'] = 100 - (100 / (1 + (up / down)))
        return data
    except: return None

df = get_clean_data(st.session_state.active_ticker, period)

# --- 6. GÖRSELLEŞTİRME ---
if df is not None:
    def safe_n(val):
        try:
            v = val.iloc[-1] if hasattr(val, 'iloc') else val
            return float(v.iloc[0]) if hasattr(v, 'iloc') else float(v)
        except: return 0.0

    last_p = safe_n(df['Close'])
    rsi_p = safe_n(df['RSI'])
    ma20_p = safe_n(df['MA20'])

    # --- ÜST DURUM ŞERİDİ ---
    if rsi_p < 35: bg, msg = "#10b981", "ALIM FIRSATI"
    elif rsi_p > 65: bg, msg = "#ef4444", "AŞIRI DEĞERLİ"
    else: bg, msg = "#6366f1", "TREND STABİL"

    st.markdown(f"""
        <div class='status-bar' style='background-color:{bg}'>
            <span>{st.session_state.active_ticker} ANALİZİ</span>
            <span>ÖNERİ: {msg}</span>
        </div>
    """, unsafe_allow_html=True)

    # --- METRİK KARTLARI ---
    m1, m2, m3, m4 = st.columns(4)
    with m1: st.markdown(f"<div class='metric-container'><div class='metric-label'>SON FİYAT</div><div class='metric-value'>{last_p:,.2f}</div></div>", unsafe_allow_html=True)
    with m2: st.markdown(f"<div class='metric-container'><div class='metric-label'>RSI (14)</div><div class='metric-value'>{rsi_p:.1f}</div></div>", unsafe_allow_html=True)
    with m3: st.markdown(f"<div class='metric-container'><div class='metric-label'>20 GÜNLÜK ORT.</div><div class='metric-value'>{ma20_p:,.2f}</div></div>", unsafe_allow_html=True)
    with m4: st.markdown(f"<div class='metric-container'><div class='metric-label'>KADEME (DİRENÇ)</div><div class='metric-value'>{last_p*1.02:,.2f}</div></div>", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # --- SADELEŞTİRİLMİŞ GRAFİK ---
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.03, row_heights=[0.8, 0.2])
    
    # Mum Grafiği
    fig.add_trace(go.Candlestick(
        x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'],
        increasing_line_color='#10b981', decreasing_line_color='#ef4444',
        name="", showlegend=False # Belirteçleri sildik
    ), row=1, col=1)
    
    # MA20 Çizgisi
    fig.add_trace(go.Scatter(
        x=df.index, y=df['MA20'], line=dict(color='#f59e0b', width=1.5),
        name="", showlegend=False # Belirteçleri sildik
    ), row=1, col=1)
    
    # RSI Çizgisi
    fig.add_trace(go.Scatter(
        x=df.index, y=df['RSI'], line=dict(color='#6366f1', width=1.5),
        name="", showlegend=False # Belirteçleri sildik
    ), row=2, col=1)

    # Grafik Tasarım İnce Ayarları
    fig.update_layout(
        height=600,
        template="plotly_white",
        xaxis_rangeslider_visible=False,
        margin=dict(l=0, r=0, t=0, b=0),
        hovermode="x unified" # Fareyle üzerine gelince tüm veriyi temiz gösterir
    )
    
    # Eksenleri temizleme
    fig.update_xaxes(showgrid=False, zeroline=False)
    fig.update_yaxes(showgrid=True, gridcolor='#f1f5f9', zeroline=False)

    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False}) # Gereksiz butonları gizledik

else:
    st.info("Lütfen sol panelden analiz etmek istediğiniz hisseyi seçin.")
