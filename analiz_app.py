import streamlit as st
import yfinance as yf

# --- 1. COMPACT TEMA ---
st.set_page_config(page_title="Vision AI Terminal", layout="wide")

st.markdown("""
    <style>
    header {visibility: hidden !important;}
    [data-testid="stSidebar"] {display: none !important;}
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
    
    html, body, [class*="st-"] { font-family: 'Inter', sans-serif; background-color: #f8fafc; font-size: 14px; }
    
    .terminal-card { background: white; border-radius: 12px; padding: 20px; border: 1px solid #e2e8f0; margin-bottom: 15px; }
    .v-row { display: flex; justify-content: space-between; padding: 5px 0; border-bottom: 1px dashed #f1f5f9; }
    .v-label { color: #64748b; }
    .v-value { font-weight: 700; color: #1e293b; }
    
    /* Öneri Kartları */
    .recom-grid { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 10px; margin-top: 10px; }
    .recom-item { background: #eff6ff; border: 1px solid #dbeafe; border-radius: 8px; padding: 10px; text-align: center; }
    .recom-symbol { font-weight: 800; color: #1e40af; display: block; }
    .recom-tag { font-size: 0.7rem; font-weight: 700; padding: 2px 6px; border-radius: 4px; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. VERİ YÖNETİMİ ---
if 'portfolio' not in st.session_state:
    st.session_state.portfolio = ["THYAO.IS", "EREGL.IS", "SISE.IS", "BTC-USD", "NVDA", "AAPL"]

st.markdown("<h3 style='margin:0 0 15px 0;'>💠 Terminal <span style='font-weight:100;'>v11 | AI Advisor</span></h3>", unsafe_allow_html=True)

# Kontrol Barı
head_c1, head_c2, head_c3, head_c4 = st.columns([2, 1.5, 0.7, 3.8])
with head_c1:
    selected = st.selectbox("Hisse", st.session_state.portfolio, label_visibility="collapsed")
with head_c2:
    new_h = st.text_input("Ekle", placeholder="+ Sembol", label_visibility="collapsed")
    if new_h:
        if new_h.upper() not in st.session_state.portfolio:
            st.session_state.portfolio.append(new_h.upper()); st.rerun()
with head_c3:
    if st.button("🗑️") and len(st.session_state.portfolio) > 1:
        st.session_state.portfolio.remove(selected); st.rerun()

# --- 3. AI TAVSİYE MOTORU (TÜM LİSTEYİ TARAR) ---
@st.cache_data(ttl=600)
def get_ai_recommendations(portfolio):
    scored_list = []
    for stock in portfolio:
        try:
            t = yf.Ticker(stock)
            hist = t.history(period="1mo")
            if hist.empty: continue
            
            # Teknik Skorlama (Basit AI Mantığı)
            last_p = hist['Close'].iloc[-1]
            rsi = 100 - (100 / (1 + (hist['Close'].diff().clip(lower=0).tail(14).mean() / -hist['Close'].diff().clip(upper=0).tail(14).mean())))
            sma20 = hist['Close'].rolling(20).mean().iloc[-1]
            
            score = 0
            if rsi < 40: score += 3  # Ucuzluk
            if last_p > sma20: score += 2  # Trend gücü
            if (last_p / hist['Close'].iloc[0]) < 1.05: score += 1 # Aşırı yükselmemiş
            
            scored_list.append({"symbol": stock, "score": score, "reason": "DİP DÖNÜŞÜ" if rsi < 40 else "TREND GÜCÜ"})
        except: continue
    return sorted(scored_list, key=lambda x: x['score'], reverse=True)[:3]

recoms = get_ai_recommendations(st.session_state.portfolio)

# --- 4. ANA PANEL ---
# Üst Kısım: AI Önerileri
st.markdown("<b>🤖 AI Portföy Taraması: En İyi 3 Fırsat</b>", unsafe_allow_html=True)
cols = st.columns(3)
for i, r in enumerate(recoms):
    with cols[i]:
        color = "#10b981" if r['score'] >= 4 else "#3b82f6"
        st.markdown(f"""
            <div class="recom-item" style="border-top: 4px solid {color}">
                <span class="recom-symbol">{r['symbol']}</span>
                <span class="recom-tag" style="background:{color}20; color:{color}">{r['reason']}</span>
            </div>
        """, unsafe_allow_html=True)

# Orta Kısım: Seçili Hisse Detayı
info_tick = yf.Ticker(selected)
info = info_tick.info
hist_data = info_tick.history(period="5d")

if not hist_data.empty:
    last_p = hist_data['Close'].iloc[-1]
    day_chg = ((last_p / hist_data['Close'].iloc[-2]) - 1) * 100
    st.markdown("<br><div class='terminal-card'>", unsafe_allow_html=True)
    
    col_t1, col_t2 = st.columns([3, 1])
    with col_t1:
        st.markdown(f"**{info.get('longName', selected)}**")
        color_p = "#10b981" if day_chg > 0 else "#ef4444"
        st.markdown(f"<span style='font-size:0.75rem; font-weight:700; color:{color_p};'>GÜNLÜK DEĞİŞİM: {day_chg:+.2f}%</span>", unsafe_allow_html=True)
    with col_t2:
        st.markdown(f"<div style='text-align:right; font-size:1.2rem; font-weight:800;'>{last_p:,.2f}</div>", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    g1, g2, g3 = st.columns(3)
    with g1:
        st.markdown(f"<div class='v-row'><span class='v-label'>F/K</span><span class='v-value'>{info.get('trailingPE', 'N/A')}</span></div>", unsafe_allow_html=True)
        st.markdown(f"<div class='v-row'><span class='v-label'>Beta</span><span class='v-value'>{info.get('beta', 'N/A')}</span></div>", unsafe_allow_html=True)
    with g2:
        st.markdown(f"<div class='v-row'><span class='v-label'>Hacim</span><span class='v-value'>{info.get('volume', 0)/1e6:.1f}M</span></div>", unsafe_allow_html=True)
        st.markdown(f"<div class='v-row'><span class='v-label'>52H Zirve</span><span class='v-value'>{info.get('fiftyTwoWeekHigh', 0):,.1f}</span></div>", unsafe_allow_html=True)
    with g3:
        st.markdown(f"<div class='v-row'><span class='v-label'>Temettü</span><span class='v-value'>%{info.get('dividendYield', 0)*100:.1f}</span></div>", unsafe_allow_html=True)
        st.markdown(f"<div class='v-row'><span class='v-label'>Piyasa D.</span><span class='v-value'>{info.get('marketCap', 0)/1e9:.1f}B</span></div>", unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)
