import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# --- 1. AYARLAR ---
st.set_page_config(page_title="Vision Elite v3", layout="wide")

if 'my_list' not in st.session_state:
    st.session_state.my_list = "THYAO.IS, EREGL.IS, SISE.IS, ASTOR.IS, BTC-USD, GC=F"

# --- 2. ELITE UI DESIGN ---
st.markdown("""
    <style>
    .stApp { background-color: #fcfdfe; }
    .decision-card {
        padding: 15px; border-radius: 12px; color: white;
        text-align: center; font-weight: 700; font-size: 1.2rem;
        box-shadow: 0 4px 10px rgba(0,0,0,0.05); margin-bottom: 15px;
    }
    .tech-table {
        width: 100%; border-collapse: collapse; background: white;
        border-radius: 10px; overflow: hidden; border: 1px solid #f1f5f9;
    }
    .tech-table td { padding: 10px; border-bottom: 1px solid #f1f5f9; font-size: 0.85rem; }
    .tech-val { font-weight: 700; color: #1e293b; text-align: right; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. SIDEBAR ---
with st.sidebar:
    st.title("🛡️ Vision Elite")
    user_input = st.text_area("İzleme Listesi", value=st.session_state.my_list, height=100)
    if st.button("💾 Kaydet"):
        st.session_state.my_list = user_input
        st.rerun()

    current_list = [x.strip().upper() for x in st.session_state.my_list.split(",")]
    if 'active_ticker' not in st.session_state:
        st.session_state.active_ticker = current_list[0]

    for ticker in current_list:
        is_active = ticker == st.session_state.active_ticker
        if st.button(f"{'⚡ ' if is_active else ''}{ticker}", use_container_width=True):
            st.session_state.active_ticker = ticker
            st.rerun()

# --- 4. ANALİZ MOTORU ---
@st.cache_data(ttl=60)
def get_advanced_data(symbol):
    try:
        data = yf.download(symbol, period="1y", interval="1d")
        if data.empty: return None
        # MA & Bollinger
        data['MA20'] = data['Close'].rolling(20).mean()
        data['std'] = data['Close'].rolling(20).std()
        data['Upper'] = data['MA20'] + (data['std'] * 2)
        data['Lower'] = data['MA20'] - (data['std'] * 2)
        # MACD
        exp1 = data['Close'].ewm(span=12, adjust=False).mean()
        exp2 = data['Close'].ewm(span=26, adjust=False).mean()
        data['MACD'] = exp1 - exp2
        data['Signal'] = data['MACD'].ewm(span=9, adjust=False).mean()
        data['Hist'] = data['MACD'] - data['Signal']
        # RSI
        delta = data['Close'].diff()
        up = (delta.where(delta > 0, 0)).rolling(14).mean()
        down = (-delta.where(delta < 0, 0)).rolling(14).mean()
        data['RSI'] = 100 - (100 / (1 + (up / down)))
        return data
    except: return None

df = get_advanced_data(st.session_state.active_ticker)

if df is not None:
    def sn(series): return float(series.iloc[-1])
    
    price = sn(df['Close'])
    rsi = sn(df['RSI'])
    macd_hist = sn(df['Hist'])
    
    # --- KARAR MOTORU ---
    score = 0
    if rsi < 32: score += 1
    if rsi > 68: score -= 1
    if price < sn(df['Lower']): score += 1
    if price > sn(df['Upper']): score -= 1
    if macd_hist > 0: score += 1
    if macd_hist < 0: score -= 1

    if score >= 2: color, advice = "#10b981", "GÜÇLÜ AL SİNYALİ"
    elif score <= -2: color, advice = "#ef4444", "GÜÇLÜ SAT SİNYALİ"
    else: color, advice = "#64748b", "NÖTR / BEKLE"

    st.markdown(f"<div class='decision-card' style='background:{color}'>{st.session_state.active_ticker}: {advice}</div>", unsafe_allow_html=True)

    col_chart, col_data = st.columns([3, 1])

    with col_chart:
        # --- SUBPLOT: MUM + MACD ---
        fig = make_subplots(rows=2, cols=1, shared_xaxes=True, 
                           vertical_spacing=0.08, row_heights=[0.7, 0.3])
        
        # 1. Row: Mum Grafiği & Bollinger
        fig.add_trace(go.Scatter(x=df.index, y=df['Upper'], line=dict(width=0), showlegend=False), row=1, col=1)
        fig.add_trace(go.Scatter(x=df.index, y=df['Lower'], line=dict(width=0), fill='tonexty', fillcolor='rgba(99, 102, 241, 0.03)', showlegend=False), row=1, col=1)
        fig.add_trace(go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'], name=""), row=1, col=1)
        
        # Anlık Fiyat Çizgisi
        fig.add_hline(y=price, line_dash="dash", line_color="#1e293b", row=1, col=1)

        # 2. Row: MACD Histogram
        colors = ['#10b981' if val >= 0 else '#ef4444' for val in df['Hist']]
        fig.add_trace(go.Bar(x=df.index, y=df['Hist'], marker_color=colors, name="MACD Hist"), row=2, col=1)
        fig.add_trace(go.Scatter(x=df.index, y=df['MACD'], line=dict(color='#6366f1', width=1), name="MACD"), row=2, col=1)
        
        fig.update_layout(height=500, margin=dict(l=0,r=40,t=0,b=0), template="plotly_white", 
                          xaxis_rangeslider_visible=False, showlegend=False, yaxis=dict(side="right"))
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

    with col_data:
        # --- TEKNİK ÖZET ---
        st.markdown(f"""
        <table class='tech-table'>
            <tr><td>Anlık Fiyat</td><td class='tech-val'>{price:,.2f}</td></tr>
            <tr><td>RSI (14)</td><td class='tech-val'>{rsi:.1f}</td></tr>
            <tr><td>MACD Momentum</td><td class='tech-val' style='color:{'green' if macd_hist>0 else 'red'}'>{macd_hist:.2f}</td></tr>
            <tr><td>Bollinger Üst</td><td class='tech-val'>{sn(df['Upper']):,.2f}</td></tr>
            <tr><td>Bollinger Alt</td><td class='tech-val'>{sn(df['Lower']):,.2f}</td></tr>
            <tr><td>Günlük Fark</td><td class='tech-val'>%{((price/sn(df['Open']))-1)*100:.2f}</td></tr>
        </table>
        """, unsafe_allow_html=True)
        
        st.markdown("🔍 **Trend Notu:**")
        if macd_hist > 0 and sn(df['Hist'].shift(1)) < macd_hist:
            st.success("Pozitif momentum güçleniyor.")
        elif macd_hist < 0 and sn(df['Hist'].shift(1)) > macd_hist:
            st.error("Negatif momentum artıyor.")
        else:
            st.info("Trend kararsız seyrediyor.")

else:
    st.error("Veri bağlantısı başarısız.")
