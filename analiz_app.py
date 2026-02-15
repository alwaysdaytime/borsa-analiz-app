import streamlit as st
import yfinance as yf

# --- 1. ULTRA COMPACT TEMA ---
st.set_page_config(page_title="Vision AI Terminal", layout="wide")

st.markdown("""
    <style>
    header {visibility: hidden !important;}
    [data-testid="stSidebar"] {display: none !important;}
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&display=swap');
    
    html, body, [class*="st-"] { 
        font-family: 'Inter', sans-serif; 
        background-color: #f8fafc;
        font-size: 14px;
    }
    
    /* Radar Bar: Daha ince ve kompakt */
    .radar-mini {
        background: #0f172a; color: #38bdf8; border-radius: 8px;
        padding: 8px 15px; display: flex; align-items: center;
        justify-content: space-between; margin-bottom: 15px;
        font-family: 'JetBrains Mono', monospace; font-size: 0.85rem;
    }

    /* Ana Terminal Kartı */
    .terminal-card {
        background: white; border-radius: 12px; padding: 20px;
        border: 1px solid #e2e8f0;
    }

    /* Veri Satırları */
    .v-row {
        display: flex; justify-content: space-between; 
        padding: 6px 0; border-bottom: 1px dashed #f1f5f9;
    }
    .v-label { color: #64748b; font-weight: 500; }
    .v-value { font-weight: 700; color: #1e293b; }
    
    /* Karar Rozeti */
    .status-pill {
        padding: 2px 10px; border-radius: 4px; font-weight: 700; font-size: 0.75rem;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. VERİ YÖNETİMİ ---
if 'portfolio' not in st.session_state:
    st.session_state.portfolio = ["THYAO.IS", "EREGL.IS", "SISE.IS", "BTC-USD", "NVDA"]

# Üst Bar (Seçim ve Ekleme Yan Yana)
st.markdown("<h3 style='margin:0 0 15px 0;'>💠 Terminal <span style='font-weight:100;'>v10</span></h3>", unsafe_allow_html=True)

head_c1, head_c2, head_c3 = st.columns([2, 2, 4])
with head_c1:
    selected = st.selectbox("Hisse", st.session_state.portfolio, label_visibility="collapsed")
with head_c2:
    new_h = st.text_input("Ekle", placeholder="+ Sembol ekle", label_visibility="collapsed")
    if new_h:
        if new_h.upper() not in st.session_state.portfolio:
            st.session_state.portfolio.append(new_h.upper()); st.rerun()

# --- 3. RADAR MİNİ ---
@st.cache_data(ttl=600)
def get_mini_radar(portfolio):
    try:
        t = yf.Ticker(portfolio[0]); h = t.history(period="2d")
        chg = ((h['Close'].iloc[-1] / h['Close'].iloc[-2]) - 1) * 100
        return portfolio[0], chg
    except: return "N/A", 0

top_s, top_v = get_mini_radar(st.session_state.portfolio)
st.markdown(f"""
    <div class="radar-mini">
        <span>● RADAR: <b>{top_s}</b> Aktif Sinyal İzleniyor</span>
        <span style="color:{'#10b981' if top_v > 0 else '#ef4444'}">Günlük Değişim: {'+' if top_v > 0 else ''}{top_v:.2f}%</span>
    </div>
""", unsafe_allow_html=True)

# --- 4. ANA TERMİNAL ---
info_tick = yf.Ticker(selected)
info = info_tick.info
hist = info_tick.history(period="5d")

if not hist.empty:
    last_p = hist['Close'].iloc[-1]
    prev_p = hist['Close'].iloc[-2]
    day_chg = ((last_p / prev_p) - 1) * 100
    
    st.markdown("<div class='terminal-card'>", unsafe_allow_html=True)
    
    # Başlık Alanı
    col_t1, col_t2 = st.columns([3, 1])
    with col_t1:
        st.markdown(f"**{info.get('longName', selected)}**")
        color = "#10b981" if day_chg > 0 else "#ef4444"
        st.markdown(f"<span class='status-pill' style='background:{color}20; color:{color};'>AI ANALİZ: AKTİF</span>", unsafe_allow_html=True)
    with col_t2:
        st.markdown(f"<div style='text-align:right; font-size:1.2rem; font-weight:800;'>{last_p:,.2f}</div>", unsafe_allow_html=True)
        st.markdown(f"<div style='text-align:right; color:{color}; font-size:0.8rem;'>{day_chg:+.2f}%</div>", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    
    # Veri Gridleri
    g1, g2, g3 = st.columns(3)
    
    with g1:
        st.markdown(f"<div class='v-row'><span class='v-label'>F/K Oranı</span><span class='v-value'>{info.get('trailingPE', 'N/A')}</span></div>", unsafe_allow_html=True)
        st.markdown(f"<div class='v-row'><span class='v-label'>Piyasa Değeri</span><span class='v-value'>{info.get('marketCap', 0)/1e9:.1f}B</span></div>", unsafe_allow_html=True)
    
    with g2:
        st.markdown(f"<div class='v-row'><span class='v-label'>Beta (Risk)</span><span class='v-value'>{info.get('beta', 'N/A')}</span></div>", unsafe_allow_html=True)
        st.markdown(f"<div class='v-row'><span class='v-label'>52H Zirve</span><span class='v-value'>{info.get('fiftyTwoWeekHigh', 0):,.1f}</span></div>", unsafe_allow_html=True)

    with g3:
        st.markdown(f"<div class='v-row'><span class='v-label'>Temettü</span><span class='v-value'>%{info.get('dividendYield', 0)*100:.1f}</span></div>", unsafe_allow_html=True)
        st.markdown(f"<div class='v-row'><span class='v-label'>Sektör</span><span class='v-value'>{info.get('sector', 'N/A')[:10]}..</span></div>", unsafe_allow_html=True)

    # Mini Özet (Yalnızca 2 satır)
    st.markdown("<br><div style='font-size:0.85rem; color:#475569; border-top:1px solid #f1f5f9; pt-10;'>", unsafe_allow_html=True)
    summary = info.get('longBusinessSummary', 'Özet yok.')[:250]
    st.markdown(f"<b>Not:</b> {summary}...", unsafe_allow_html=True)
    st.markdown("</div></div>", unsafe_allow_html=True)

else:
    st.warning("Veri yüklenemedi.")
