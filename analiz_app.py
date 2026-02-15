import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# --- 1. AYARLAR ---
st.set_page_config(page_title="Vision AI Terminal", layout="wide")

if 'my_list' not in st.session_state:
    st.session_state.my_list = "THYAO.IS, EREGL.IS, SISE.IS, ASTOR.IS, BTC-USD, GC=F"

# --- 2. AI UI DESIGN ---
st.markdown("""
    <style>
    .stApp { background-color: #fcfdfe; }
    .ai-card {
        padding: 20px; border-radius: 15px; color: white;
        text-align: center; font-weight: 800; font-size: 1.5rem;
        box-shadow: 0 10px 25px rgba(0,0,0,0.1); margin-bottom: 20px;
        border: 2px solid rgba(255,255,255,0.2);
    }
    .metric-box {
        background: white; padding: 15px; border-radius: 12px;
        border: 1px solid #e2e8f0; box-shadow: 0 4px 6px rgba(0,0,0,0.02);
    }
    .tech-label { font-size: 0.8rem; color: #64748b; font-weight: 600; }
    .tech-val { font-size: 1.1rem; font-weight: 700; color: #1e293b; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. SIDEBAR ---
with st.sidebar:
    st.title("🛡️ Vision AI")
    user_input = st.text_area("İzleme Listesi", value=st.session_state.my_list, height=100)
    if st.button("💾 Kaydet ve Yenile"):
        st.session_state.my_list = user_input
        st.rerun()

    current_list = [x.strip().upper() for x in st.session_state.my_list.split(",")]
    if 'active_ticker' not in st.session_state:
        st.session_state.active_ticker = current_list[0]

    for ticker in current_list:
        is_active = ticker == st.session_state.active_ticker
        if st.button(f"{'🤖 ' if is_active else ''}{ticker}", use_container_width=True):
            st.session_state.active_ticker = ticker
            st.rerun()

# --- 4. AI ANALİZ MOTORU (MULTI-FAKTÖR) ---
@st.cache_data(ttl=60)
def get_ai_data(symbol):
    try:
        data = yf.download(symbol, period="1y", interval="1d")
        if data.empty: return None
        
        # Trend: Hareketli Ortalamalar
        data['SMA20'] = data['Close'].rolling(20).mean()
        data['SMA50'] = data['Close'].rolling(50).mean()
        
        # Volatilite: Bollinger
        data['std'] = data['Close'].rolling(20).std()
        data['Upper'] = data['SMA20'] + (data['std'] * 2)
        data['Lower'] = data['SMA20'] - (data['std'] * 2)
        
        # Momentum: MACD & RSI
        exp1 = data['Close'].ewm(span=12, adjust=False).mean()
        exp2 = data['Close'].ewm(span=26, adjust=False).mean()
        data['MACD'] = exp1 - exp2
        data['Signal'] = data['MACD'].ewm(span=9, adjust=False).mean()
        data['Hist'] = data['MACD'] - data['Signal']
        
        delta = data['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
        data['RSI'] = 100 - (100 / (1 + (gain / loss)))
        
        # Hacim Analizi
        data['Vol_Mean'] = data['Volume'].rolling(20).mean()
        return data
    except: return None

df = get_ai_data(st.session_state.active_ticker)

if df is not None:
    def sn(series): return float(series.iloc[-1])
    
    p = sn(df['Close'])
    rsi = sn(df['RSI'])
    macd_h = sn(df['Hist'])
    sma20 = sn(df['SMA20'])
    sma50 = sn(df['SMA50'])
    vol = sn(df['Volume'])
    vol_m = sn(df['Vol_Mean'])
    up_b = sn(df['Upper'])
    lo_b = sn(df['Lower'])

    # --- AI KARAR ALGORİTMASI ---
    ai_score = 0
    reasons = []

    # 1. RSI Kontrolü
    if rsi < 30: ai_score += 2; reasons.append("Aşırı Satım (Fırsat)")
    elif rsi > 70: ai_score -= 2; reasons.append("Aşırı Alım (Risk)")

    # 2. Trend Kontrolü (Golden/Death Cross yakınlığı)
    if p > sma20: ai_score += 1; reasons.append("Kısa Vade Pozitif")
    if sma20 > sma50: ai_score += 1; reasons.append("Yükseliş Trendi (MA)")

    # 3. Momentum (MACD)
    if macd_h > 0: ai_score += 1; reasons.append("Pozitif Momentum")
    else: ai_score -= 1; reasons.append("Negatif Momentum")

    # 4. Hacim Onayı
    if vol > vol_m * 1.2: ai_score *= 1.2; reasons.append("Yüksek Hacim Desteği")

    # Final Karar
    if ai_score >= 3: color, status = "#10b981", "KESİN AL (STRONG BUY)"
    elif ai_score >= 1: color, status = "#34d399", "AL (BUY)"
    elif ai_score <= -3: color, status = "#ef4444", "KESİN SAT (STRONG SELL)"
    elif ai_score <= -1: color, status = "#f87171", "SAT (SELL)"
    else: color, status = "#64748b", "TUT / NÖTR (HOLD)"

    st.markdown(f"<div class='ai-card' style='background:{color}'>AI ÖNERİSİ: {status}</div>", unsafe_allow_html=True)

    # --- PANEL DÜZENİ ---
    c_graph, c_stats = st.columns([2.5, 1])

    with c_graph:
        fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.05, row_heights=[0.7, 0.3])
        
        # Mum ve Bollinger
        fig.add_trace(go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'], name="Fiyat"), row=1, col=1)
        fig.add_trace(go.Scatter(x=df.index, y=df['Upper'], line=dict(color='rgba(173,216,230,0.2)'), showlegend=False), row=1, col=1)
        fig.add_trace(go.Scatter(x=df.index, y=df['Lower'], line=dict(color='rgba(173,216,230,0.2)'), fill='tonexty', showlegend=False), row=1, col=1)
        
        # MACD Histogram
        hist_colors = ['#10b981' if x >= 0 else '#ef4444' for x in df['Hist']]
        fig.add_trace(go.Bar(x=df.index, y=df['Hist'], marker_color=hist_colors, name="MACD"), row=2, col=1)
        
        fig.update_layout(height=500, margin=dict(l=0,r=40,t=0,b=0), template="plotly_white", xaxis_rangeslider_visible=False, yaxis=dict(side="right"), showlegend=False)
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

    with c_stats:
        st.markdown("### 🤖 AI Analiz Notları")
        for r in reasons:
            st.write(f"✅ {r}" if ai_score > 0 else f"❌ {r}")
        
        st.markdown("---")
        st.markdown(f"""
            <div class='metric-box'><span class='tech-label'>RSI</span><br><span class='tech-val'>{rsi:.1f}</span></div><br>
            <div class='metric-box'><span class='tech-label'>MACD Hist</span><br><span class='tech-val'>{macd_h:.2f}</span></div><br>
            <div class='metric-box'><span class='tech-label'>Fiyat/MA20</span><br><span class='tech-val'>%{((p/sma20)-1)*100:.2f}</span></div>
        """, unsafe_allow_html=True)

else:
    st.error("Veri çekilemedi.")
