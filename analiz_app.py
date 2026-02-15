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
    
    .terminal-card {
        background: white; border-radius: 12px; padding: 20px;
        border: 1px solid #e2e8f0;
    }

    .v-row {
        display: flex; justify-content: space-between; 
        padding: 6px 0; border-bottom: 1px dashed #f1f5f9;
    }
    .v-label { color: #64748b; font-weight: 500; }
    .v-value { font-weight: 700; color: #1e293b; }
    
    /* Silme Butonu Stili */
    .stButton > button {
        border-radius: 6px;
        padding: 2px 10px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. VERİ YÖNETİMİ ---
if 'portfolio' not in st.session_state:
    st.session_state.portfolio = ["THYAO.IS", "EREGL.IS", "SISE.IS", "BTC-USD", "NVDA"]

st.markdown("<h3 style='margin:0 0 15px 0;'>💠 Terminal <span style='font-weight:100;'>v10.1</span></h3>", unsafe_allow_html=True)

# Kontrol Paneli (Seç, Ekle, Sil)
head_c1, head_c2, head_c3, head_c4 = st.columns([2, 1.5, 0.7, 3.8])

with head_c1:
    selected = st.selectbox("Hisse", st.session_state.portfolio, label_visibility="collapsed")

with head_c2:
    new_h = st.text_input("Ekle", placeholder="+ Sembol", label_visibility="collapsed")
    if new_h:
        if new_h.upper() not in st.session_state.portfolio:
            st.session_state.portfolio.append(new_h.upper())
            st.rerun()

with head_c3:
    # SEÇİLİ HİSSEYİ SİLME BUTONU
    if st.button("🗑️", help="Seçili hisseyi listeden kaldır"):
        if len(st.session_state.portfolio) > 1:
            st.session_state.portfolio.remove(selected)
            # Silme sonrası listenin ilk elemanına dön
            st.session_state.selected_stock = st.session_state.portfolio[0]
            st.rerun()
        else:
            st.warning("Son hisseyi silemezsiniz.")

# --- 3. ANA TERMİNAL İŞLEME ---
info_tick = yf.Ticker(selected)
info = info_tick.info
hist = info_tick.history(period="5d")

if not hist.empty:
    last_p = hist['Close'].iloc[-1]
    prev_p = hist['Close'].iloc[-2]
    day_chg = ((last_p / prev_p) - 1) * 100
    
    st.markdown("<div class='terminal-card'>", unsafe_allow_html=True)
    
    col_t1, col_t2 = st.columns([3, 1])
    with col_t1:
        st.markdown(f"**{info.get('longName', selected)}**")
        color = "#10b981" if day_chg > 0 else "#ef4444"
        st.markdown(f"<span style='font-size:0.75rem; font-weight:700; background:{color}20; color:{color}; padding:2px 8px; border-radius:4px;'>AI ANALİZ: AKTİF</span>", unsafe_allow_html=True)
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

    st.markdown("<br><div style='font-size:0.85rem; color:#475569; border-top:1px solid #f1f5f9; padding-top:10px;'>", unsafe_allow_html=True)
    summary = info.get('longBusinessSummary', 'Özet yok.')[:250]
    st.markdown(f"<b>Not:</b> {summary}...", unsafe_allow_html=True)
    st.markdown("</div></div>", unsafe_allow_html=True)
