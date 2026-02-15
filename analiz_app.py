import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime

# --- 1. AYARLAR ---
st.set_page_config(page_title="Vision Elite Terminal", layout="wide")

if 'my_list' not in st.session_state:
    st.session_state.my_list = "THYAO.IS, EREGL.IS, SISE.IS, ASTOR.IS, BTC-USD, GC=F"

# --- 2. ELITE UI DESIGN ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&display=swap');
    .stApp { background-color: #fcfdfe; }
    
    /* Karar Paneli */
    .decision-card {
        padding: 20px; border-radius: 15px; color: white;
        text-align: center; font-weight: 800; font-size: 1.4rem;
        box-shadow: 0 10px 20px rgba(0,0,0,0.05); margin-bottom: 25px;
    }
    
    /* Teknik Tablo */
    .tech-table {
        width: 100%; border-collapse: collapse; background: white;
        border-radius: 10px; overflow: hidden; box-shadow: 0 4px 6px rgba(0,0,0,0.02);
    }
    .tech-table td { padding: 12px; border-bottom: 1px solid #f1f5f9; font-size: 0.9rem; }
    .tech-val { font-weight: 700; color: #1e293b; text-align: right; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. YAN PANEL (SIDEBAR) ---
with st.sidebar:
    st.title("🛡️ Vision Elite")
    user_input = st.text_area("İzleme Listesi", value=st.session_state.my_list, height=100)
    if st.button("💾 Listeyi Güncelle"):
        st.session_state.my_list = user_input
        st.rerun()

    current_list = [x.strip().upper() for x in st.session_state.my_list.split(",")]
    if 'active_ticker' not in st.session_state:
        st.session_state.active_ticker = current_list[0]

    st.markdown("---")
    for ticker in current_list:
        is_active = ticker == st.session_state.active_ticker
        if st.button(f"{'⚡ ' if is_active else ''}{ticker}", use_container_width=True):
            st.session_state.active_ticker = ticker
            st.rerun()

# --- 4. GELİŞMİŞ ANALİZ MOTORU ---
@st.cache_data(ttl=60)
def get_elite_data(symbol):
    try:
        data = yf.download(symbol, period="1y", interval="1d")
        if data.empty: return None
        # Teknik İndikatörler
        data['MA20'] = data['Close'].rolling(20).mean()
        data['std'] = data['Close'].rolling(20).std()
        data['Upper'] = data['MA20'] + (data['std'] * 2)
        data['Lower'] = data['MA20'] - (data['std'] * 2)
        
        # MACD
        exp1 = data['Close'].ewm(span=12, adjust=False).mean()
        exp2 = data['Close'].ewm(span=26, adjust=False).mean()
        data['MACD'] = exp1 - exp2
        data['Signal'] = data['MACD'].ewm(span=9, adjust=False).mean()
        
        # RSI
        delta = data['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
        data['RSI'] = 100 - (100 / (1 + (gain / loss)))
        return data
    except: return None

df = get_elite_data(st.session_state.active_ticker)

if df is not None:
    def sn(series): return float(series.iloc[-1])
    
    # Anlık Veriler
    price = sn(df['Close'])
    rsi = sn(df['RSI'])
    macd = sn(df['MACD'])
    signal = sn(df['Signal'])
    upper = sn(df['Upper'])
    lower = sn(df['Lower'])

    # --- AL/SAT SKORLAMA ---
    score = 0
    if rsi < 35: score += 1
    if rsi > 65: score -= 1
    if price < lower: score += 1
    if price > upper: score -= 1
    if macd > signal: score += 1
    if macd < signal: score -= 1

    if score >= 2: color, advice = "#10b981", "GÜÇLÜ AL SİNYALİ"
    elif score == 1: color, advice = "#34d399", "KADEMELİ AL"
    elif score <= -2: color, advice = "#ef4444", "GÜÇLÜ SAT SİNYALİ"
    elif score == -1: color, advice = "#f87171", "KADEMELİ SAT"
    else: color, advice = "#64748b", "BEKLE / NÖTR"

    # Karar Başlığı
    st.markdown(f"<div class='decision-card' style='background:{color}'>{st.session_state.active_ticker}: {advice}</div>", unsafe_allow_html=True)

    col_chart, col_tech = st.columns([2.5, 1])

    with col_chart:
        # --- ELITE COMPACT GRAPH ---
        fig = go.Figure()
        # Bollinger Bantları (Gölge)
        fig.add_trace(go.Scatter(x=df.index, y=df['Upper'], line=dict(color='rgba(0,0,0,0)'), showlegend=False))
        fig.add_trace(go.Scatter(x=df.index, y=df['Lower'], line=dict(color='rgba(0,0,0,0)'), fill='tonexty', fillcolor='rgba(99, 102, 241, 0.05)', showlegend=False))
        
        # Mumlar
        fig.add_trace(go.Candlestick(
            x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'],
            increasing_line_color='#10b981', decreasing_line_color='#ef4444',
            increasing_fillcolor='#10b981', decreasing_fillcolor='#ef4444', name=""
        ))

        # Anlık Fiyat Çizgisi ve Etiketi
        fig.add_hline(y=price, line_dash="dot", line_color="#64748b", line_width=1)
        
        fig.update_layout(
            height=450, margin=dict(l=0,r=40,t=0,b=0), template="plotly_white",
            xaxis_rangeslider_visible=False, showlegend=False,
            yaxis=dict(side="right", gridcolor="#f1f5f9") # Fiyat ekseni sağda
        )
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

    with col_tech:
        # --- TEKNİK VERİ TABLOSU ---
        st.markdown(f"""
        <table class='tech-table'>
            <tr><td>Anlık Fiyat</td><td class='tech-val'>{price:,.2f}</td></tr>
            <tr><td>RSI (14)</td><td class='tech-val' style='color:{'red' if rsi>70 else 'green' if rsi<30 else 'black'}'>{rsi:.1f}</td></tr>
            <tr><td>MACD Durumu</td><td class='tech-val'>{'Pozitif' if macd > signal else 'Negatif'}</td></tr>
            <tr><td>Bollinger Üst</td><td class='tech-val'>{upper:,.2f}</td></tr>
            <tr><td>Bollinger Alt</td><td class='tech-val'>{lower:,.2f}</td></tr>
            <tr><td>Hacim (Gün)</td><td class='tech-val'>{sn(df['Volume'])/1e6:.1f}M</td></tr>
        </table>
        """, unsafe_allow_html=True)
        
        st.info(f"💡 {st.session_state.active_ticker} şu an Bollinger {'üst' if price > (upper+lower)/2 else 'alt'} kanalında seyrediyor.")

else:
    st.error("Sembol verisi alınamadı.")
