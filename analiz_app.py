import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

# --- 1. AYARLAR ---
st.set_page_config(page_title="Vision Pro", layout="wide")

# --- 2. KALICI LİSTE ---
if 'my_list' not in st.session_state:
    st.session_state.my_list = "THYAO.IS, EREGL.IS, SISE.IS, ASTOR.IS, BTC-USD"

# --- 3. TASARIM (Minimalist & Fintech) ---
st.markdown("""
    <style>
    .stApp { background-color: #f8fafc; }
    .status-bar {
        padding: 10px 20px; border-radius: 8px; color: white;
        font-weight: 600; font-size: 0.9rem; margin-bottom: 15px;
        display: flex; justify-content: space-between;
    }
    .metric-card {
        background: white; border-radius: 12px; padding: 15px;
        border: 1px solid #e2e8f0; text-align: center;
    }
    .metric-value { font-size: 1.3rem; font-weight: 700; color: #1e293b; }
    .metric-label { font-size: 0.75rem; color: #64748b; font-weight: 600; }
    </style>
    """, unsafe_allow_html=True)

# --- 4. YAN PANEL ---
with st.sidebar:
    st.title("🛡️ Vision")
    user_input = st.text_area("Hisse Listesi", value=st.session_state.my_list, height=80)
    if st.button("💾 Kaydet"):
        st.session_state.my_list = user_input
        st.rerun()

    current_list = [x.strip().upper() for x in st.session_state.my_list.split(",")]
    if 'active_ticker' not in st.session_state:
        st.session_state.active_ticker = current_list[0]

    st.markdown("---")
    for ticker in current_list:
        is_active = ticker == st.session_state.active_ticker
        if st.button(f"{'📍 ' if is_active else ''}{ticker}", use_container_width=True):
            st.session_state.active_ticker = ticker
            st.rerun()
    
    period = st.selectbox("Dönem", ["1mo", "3mo", "6mo", "1y"], index=0)

# --- 5. VERİ ÇEKME ---
@st.cache_data(ttl=60)
def get_clean_data(symbol, prd):
    try:
        data = yf.download(symbol, period=prd)
        if data.empty: return None
        data['MA20'] = data['Close'].rolling(20).mean()
        return data
    except: return None

df = get_clean_data(st.session_state.active_ticker, period)

# --- 6. GÖRSELLEŞTİRME ---
if df is not None:
    # Sayısal veri sabitleme
    def sn(val):
        v = val.iloc[-1] if hasattr(val, 'iloc') else val
        return float(v.iloc[0]) if hasattr(v, 'iloc') else float(v)

    last_p = sn(df['Close'])
    ma20_p = sn(df['MA20'])
    high_p = df['High'].max()

    # Üst Şerit
    bg = "#10b981" if last_p > ma20_p else "#f59e0b"
    st.markdown(f"<div class='status-bar' style='background:{bg}'><span>{st.session_state.active_ticker}</span><span>TREND: {'POZİTİF' if last_p > ma20_p else 'ZAYIF'}</span></div>", unsafe_allow_html=True)

    # Küçük Metrikler
    m1, m2, m3 = st.columns(3)
    m1.markdown(f"<div class='metric-card'><div class='metric-label'>SON FİYAT</div><div class='metric-value'>{last_p:,.2f}</div></div>", unsafe_allow_html=True)
    m2.markdown(f"<div class='metric-card'><div class='metric-label'>MA20 DESTEĞİ</div><div class='metric-value'>{ma20_p:,.2f}</div></div>", unsafe_allow_html=True)
    m3.markdown(f"<div class='metric-card'><div class='metric-label'>PERİYOT ZİRVESİ</div><div class='metric-value'>{sn(high_p):,.2f}</div></div>", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # --- KÜÇÜK VE STABİL GRAFİK ---
    fig = go.Figure()

    # Mumlar
    fig.add_trace(go.Candlestick(
        x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'],
        increasing_line_color='#10b981', decreasing_line_color='#ef4444',
        name="Fiyat"
    ))

    # MA20 Çizgisi
    fig.add_trace(go.Scatter(x=df.index, y=df['MA20'], line=dict(color='#6366f1', width=1.5), name="MA20"))

    # --- ANLIK DURUM BELİRTECİ (YATAY ÇİZGİ) ---
    fig.add_hline(
        y=last_p, 
        line_dash="dash", 
        line_color="#1e293b", 
        annotation_text=f"Şu an: {last_p:,.2f}", 
        annotation_position="bottom right",
        annotation_font=dict(size=12, color="#1e293b")
    )

    fig.update_layout(
        height=400, # Daha küçük ve stabil bir yükseklik
        margin=dict(l=0, r=0, t=0, b=0),
        template="plotly_white",
        xaxis_rangeslider_visible=False,
        showlegend=False,
        hovermode="x unified"
    )

    # Izgara ayarları
    fig.update_xaxes(showgrid=True, gridcolor='#f1f5f9')
    fig.update_yaxes(showgrid=True, gridcolor='#f1f5f9')

    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

else:
    st.error("Veri yüklenemedi. Lütfen sembolü kontrol edin.")
