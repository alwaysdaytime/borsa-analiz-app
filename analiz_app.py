import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# --- 1. AYARLAR ---
st.set_page_config(page_title="Vision Pro Terminal", layout="wide")

# --- 2. KALICI LİSTE YAPILANDIRMASI ---
# Buradaki listeyi bir kez düzenle, her açılışta bu liste gelir.
if 'my_list' not in st.session_state:
    st.session_state.my_list = "THYAO.IS, EREGL.IS, SISE.IS, ASTOR.IS, BTC-USD, GC=F"

# --- 3. TASARIM (AYDINLIK & PROFESYONEL) ---
st.markdown("""
    <style>
    .stApp { background-color: #f8f9fa; }
    .compact-card {
        background: white; padding: 15px; border-radius: 10px;
        border: 1px solid #e2e8f0; text-align: center;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    .compact-card h4 { margin: 0; font-size: 0.8rem; color: #64748b; }
    .compact-card h2 { margin: 5px 0; font-size: 1.4rem; color: #1e293b; }
    .decision-box {
        padding: 20px; border-radius: 12px; color: white; text-align: center;
        font-weight: bold; font-size: 1.2rem; margin-bottom: 20px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .kademe-box {
        background: #ffffff; padding: 15px; border-radius: 10px;
        border: 1px solid #cbd5e1; font-family: monospace; height: 100%;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 4. YAN PANEL ---
with st.sidebar:
    st.title("🛡️ Vision Terminal")
    st.markdown("---")
    
    new_input = st.text_area("Takip Listesini Düzenle:", value=st.session_state.my_list, height=100)
    if st.button("💾 LİSTEYİ KAYDET"):
        st.session_state.my_list = new_input
        st.rerun()

    current_list = [x.strip().upper() for x in st.session_state.my_list.split(",")]
    
    if 'active_ticker' not in st.session_state:
        st.session_state.active_ticker = current_list[0]

    st.markdown("### 📍 Hızlı Erişim")
    for ticker in current_list:
        if st.button(f"📊 {ticker}", use_container_width=True):
            st.session_state.active_ticker = ticker
    
    st.markdown("---")
    period = st.selectbox("Analiz Periyodu", ["1mo", "3mo", "6mo", "1y"], index=1)

# --- 5. VERİ ÇEKME MOTORU ---
@st.cache_data(ttl=60)
def get_data(symbol, prd):
    try:
        data = yf.download(symbol, period=prd)
        if data.empty: return None
        data['MA20'] = data['Close'].rolling(20).mean()
        data['MA50'] = data['Close'].rolling(50).mean()
        delta = data['Close'].diff()
        up = delta.clip(lower=0).rolling(14).mean()
        down = -delta.clip(upper=0).rolling(14).mean()
        data['RSI'] = 100 - (100 / (1 + (up / down)))
        return data
    except: return None

df = get_data(st.session_state.active_ticker, period)

# --- 6. KARAR VE GÖRSELLEŞTİRME ---
if df is not None:
    def safe_num(val):
        try:
            v = val.iloc[-1] if hasattr(val, 'iloc') else val
            return float(v.iloc[0]) if hasattr(v, 'iloc') else float(v)
        except: return 0.0

    last_p = safe_num(df['Close'])
    rsi_p = safe_num(df['RSI'])
    ma20_p = safe_num(df['MA20'])
    ma50_p = safe_num(df['MA50'])
    hacim_p = safe_num(df['Volume'])

    # --- AL-SAT ÖNERİ BÖLÜMÜ (GERİ GELDİ) ---
    if rsi_p < 30:
        bg, msg = "#22c55e", "🚀 GÜÇLÜ AL: Teknik olarak aşırı ucuz bölge!"
    elif rsi_p > 70:
        bg, msg = "#ef4444", "⚠️ GÜÇLÜ SAT: Teknik olarak aşırı değerli bölge!"
    elif last_p > ma20_p and ma20_p > ma50_p:
        bg, msg = "#0ea5e9", "📈 ALIMI KORU: Yükseliş trendi güçlü şekilde sürüyor."
    elif last_p < ma20_p:
        bg, msg = "#f59e0b", "🟡 BEKLE / NÖTR: Kısa vadeli zayıflık var, izlemede kal."
    else:
        bg, msg = "#64748b", "⚖️ KARARSIZ: Net bir yön sinyali yok."

    st.markdown(f"<div class='decision-box' style='background-color:{bg}'>{msg}</div>", unsafe_allow_html=True)

    # --- KOMPAKT VERİ PANELİ ---
    c_info, c_kademe = st.columns([3, 1])
    
    with c_info:
        m1, m2, m3, m4 = st.columns(4)
        m1.markdown(f"<div class='compact-card'><h4>Fiyat</h4><h2>{last_p:,.2f}</h2></div>", unsafe_allow_html=True)
        m2.markdown(f"<div class='compact-card'><h4>RSI</h4><h2>{rsi_p:.1f}</h2></div>", unsafe_allow_html=True)
        m3.markdown(f"<div class='compact-card'><h4>MA20</h4><h2>{ma20_p:,.2f}</h2></div>", unsafe_allow_html=True)
        m4.markdown(f"<div class='compact-card'><h4>Hacim</h4><h2>{hacim_p/1e6:.1f}M</h2></div>", unsafe_allow_html=True)

    with c_kademe:
        st.markdown(f"<div class='kademe-box'><b>TEKNİK SEVİYE</b><br><hr>" +
                    f"<span style='color:green'>Dir: {last_p*1.02:,.2f}</span><br>" +
                    f"<span style='color:red'>Des: {last_p*0.98:,.2f}</span><br>" +
                    f"Trend: {'Yukarı' if last_p > ma20_p else 'Aşağı'}</div>", unsafe_allow_html=True)

    # --- GRAFİK ---
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.05, row_heights=[0.8, 0.2])
    fig.add_trace(go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'], name="Mum"), row=1, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=df['MA20'], name="MA20", line=dict(color='#f59e0b', width=1.5)), row=1, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=df['RSI'], name="RSI", line=dict(color='#8b5cf6')), row=2, col=1)
    fig.update_layout(height=550, template="plotly_white", xaxis_rangeslider_visible=False, margin=dict(l=0,r=0,t=0,b=0))
    st.plotly_chart(fig, use_container_width=True)

else:
    st.warning("Lütfen yan panelden bir hisse seçin veya sembolü kontrol edin.")
