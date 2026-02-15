import streamlit as st
import yfinance as yf
import pandas as pd

# --- 1. AYARLAR & COMPACT TEMA ---
st.set_page_config(page_title="Vision AI | Strategic Radar", layout="wide")

st.markdown("""
    <style>
    header {visibility: hidden !important;}
    [data-testid="stSidebar"] {display: none !important;}
    
    /* Global Stil */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
    html, body, [class*="st-"] { font-family: 'Inter', sans-serif; background-color: #f4f7f9; }
    
    /* Mini Fırsat Radarı (Üstteki İnce Bar) */
    .radar-bar {
        background: #1e3a8a; color: white; border-radius: 12px;
        padding: 10px 20px; display: flex; align-items: center;
        justify-content: space-between; margin-bottom: 20px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    }
    .radar-tag { background: #10b981; padding: 2px 10px; border-radius: 6px; font-size: 0.8rem; font-weight: 700; }

    /* Ana Kart Tasarımı */
    .main-card {
        background: white; border-radius: 16px; padding: 25px;
        border: 1px solid #e2e8f0; box-shadow: 0 4px 20px rgba(0,0,0,0.03);
    }

    /* Öneri Rozetleri */
    .badge {
        padding: 4px 12px; border-radius: 8px; font-size: 0.85rem; font-weight: 700;
        display: inline-block; margin-right: 8px;
    }
    .badge-buy { background: #dcfce7; color: #166534; border: 1px solid #bbf7d0; }
    .badge-neutral { background: #f1f5f9; color: #475569; border: 1px solid #e2e8f0; }
    
    /* Finansal Tablo Görünümü */
    .stat-row {
        display: flex; justify-content: space-between; padding: 12px 0;
        border-bottom: 1px solid #f1f5f9; align-items: center;
    }
    .stat-label { color: #64748b; font-size: 0.9rem; }
    .stat-value { font-weight: 700; color: #1e293b; font-size: 0.95rem; }
    .stat-green { color: #10b981; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. PORTFÖY YÖNETİMİ ---
if 'portfolio' not in st.session_state:
    st.session_state.portfolio = ["THYAO.IS", "EREGL.IS", "SISE.IS", "BTC-USD", "NVDA"]

# Üst Başlık ve Kontroller
st.markdown("<h2 style='color:#1e293b; margin-bottom:20px;'>💠 Vision AI | <span style='font-weight:400; font-size:1.2rem;'>Strategic Radar (v9)</span></h2>", unsafe_allow_html=True)

# --- 3. RADAR & ANALİZ MOTORU ---
@st.cache_data(ttl=600)
def get_best_opportunity(portfolio):
    try:
        results = []
        for s in portfolio[:4]: # Hız için ilk 4 hisseyi tara
            t = yf.Ticker(s)
            h = t.history(period="5d")
            score = (h['Close'].iloc[-1] / h['Close'].iloc[0]) - 1
            results.append((s, score))
        return sorted(results, key=lambda x: x[1], reverse=True)[0]
    except: return ("N/A", 0)

best_s, best_v = get_best_opportunity(st.session_state.portfolio)

# --- 4. ARAYÜZ YERLEŞİMİ ---

# KÜÇÜLTÜLMÜŞ RADAR BAR
st.markdown(f"""
    <div class="radar-bar">
        <span>🚀 <b>Kısa Vade Fırsatı:</b> {best_s} <span style="opacity:0.7; margin-left:10px;">Skor: 7/7</span></span>
        <span class="radar-tag">POTANSİYEL VAR</span>
    </div>
""", unsafe_allow_html=True)

# KONTROL PANELİ
c_sel, c_add, c_empty = st.columns([2, 2, 4])
with c_sel:
    selected_stock = st.selectbox("Hisse", st.session_state.portfolio, label_visibility="collapsed")
with c_add:
    new_h = st.text_input("Ekle", placeholder="Sembol...", label_visibility="collapsed")
    if new_h:
        if new_h.upper() not in st.session_state.portfolio:
            st.session_state.portfolio.append(new_h.upper()); st.rerun()

# ANA ANALİZ KARTI
info_tick = yf.Ticker(selected_stock)
info = info_tick.info
hist = info_tick.history(period="1y")

if not hist.empty:
    last_p = hist['Close'].iloc[-1]
    
    st.markdown("<div class='main-card'>", unsafe_allow_html=True)
    
    # Rozetler ve Başlık
    st.markdown(f"""
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:20px;">
            <div>
                <span class="badge badge-buy">ÖNERİ: GÜÇLÜ AL</span>
                <span class="badge badge-neutral">TUT / NÖTR</span>
                <h3 style="margin:10px 0 0 0;">{info.get('longName', selected_stock)}</h3>
            </div>
            <div style="text-align:right;">
                <div style="color:#64748b; font-size:0.8rem;">Güncel Fiyat</div>
                <div style="font-size:1.5rem; font-weight:700; color:#1e3a8a;">{last_p:,.2f}</div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    # DETAYLI VERİ TABLOSU
    st.markdown("#### 📊 Şirket Profili & Temel Veriler")
    
    col_a, col_b = st.columns(2)
    
    stats_left = [
        ("F/K Oranı (P/E)", f"{info.get('trailingPE', 'N/A')}"),
        ("Piyasa Değeri", f"{info.get('marketCap', 0)/1e9:.2f}B"),
        ("Beta (Risk)", f"{info.get('beta', 'N/A')}")
    ]
    
    stats_right = [
        ("Fiyat/Defter Değeri", f"{info.get('priceToBook', 'N/A')}"),
        ("Temettü Verimi", f"%{info.get('dividendYield', 0)*100:.2f}"),
        ("52 Hafta Zirve", f"{info.get('fiftyTwoWeekHigh', 0):,.2f}")
    ]

    with col_a:
        for label, val in stats_left:
            st.markdown(f"<div class='stat-row'><span class='stat-label'>{label}</span><span class='stat-value'>{val}</span></div>", unsafe_allow_html=True)
    
    with col_b:
        for label, val in stats_right:
            st.markdown(f"<div class='stat-row'><span class='stat-label'>{label}</span><span class='stat-value stat-green'>{val}</span></div>", unsafe_allow_html=True)

    # İŞ ÖZETİ (DAHA KISA)
    st.markdown("<br><b>AI Analizi:</b>", unsafe_allow_html=True)
    summary = info.get('longBusinessSummary', 'Veri yok.')[:400]
    st.markdown(f"<p style='color:#475569; font-size:0.9rem; line-height:1.6;'>{summary}...</p>", unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)
