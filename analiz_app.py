import streamlit as st
import yfinance as yf
import pandas as pd

# --- 1. RADİKAL TEMİZLİK VE TASARIM ---
st.set_page_config(page_title="Vision Strategic AI", layout="wide", initial_sidebar_state="expanded")

# Tüm gereksiz Streamlit bileşenlerini ve o yazıları kökten kazıyan CSS
st.markdown("""
    <style>
    /* Üst menü, navigasyon ve gereksiz metinleri tamamen yok et */
    header {visibility: hidden !important;}
    [data-testid="stSidebarNav"] {display: none !important;}
    .st-emotion-cache-6qob1r {display: none !important;}
    div[role="nav"] {display: none !important;}
    
    /* Global Font ve Arka Plan */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');
    html, body, [class*="st-"] { font-family: 'Inter', sans-serif; }
    
    /* Ana Konteyner */
    .main-card {
        background: #ffffff;
        border-radius: 20px;
        padding: 40px;
        border: 1px solid #f0f2f6;
        box-shadow: 0 10px 30px rgba(0,0,0,0.02);
    }
    
    /* AI Karar Başlığı */
    .decision-title {
        font-size: 2.5rem; font-weight: 800;
        background: linear-gradient(120deg, #1a73e8, #9b72f3);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        margin-bottom: 20px;
    }

    /* Bilgi Kutuları */
    .brief-box {
        background: #f8faff;
        border-radius: 15px;
        padding: 25px;
        border-left: 5px solid #1a73e8;
        color: #3c4043;
        line-height: 1.7;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. PORTFÖY YÖNETİMİ (SOL PANEL) ---
if 'portfolio' not in st.session_state:
    st.session_state.portfolio = ["THYAO.IS", "EREGL.IS", "SISE.IS", "BTC-USD"]

with st.sidebar:
    st.markdown("<h1 style='color:#1a73e8; font-size:1.8rem;'>Vision AI</h1>", unsafe_allow_html=True)
    st.write("Profesyonel Analiz Sistemi")
    st.markdown("---")
    
    # Yeni Hisse Ekleme (+)
    c_in, c_bt = st.columns([3, 1])
    add_symbol = c_in.text_input("Sembol", placeholder="Örn: AAPL", label_visibility="collapsed")
    if c_bt.button("➕"):
        if add_symbol and add_symbol.upper() not in st.session_state.portfolio:
            st.session_state.portfolio.append(add_symbol.upper())
            st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)
    
    # Liste ve Hisse Çıkarma (-)
    for stock in st.session_state.portfolio:
        c_name, c_del = st.columns([4, 1])
        if c_name.button(f"📊 {stock}", use_container_width=True):
            st.session_state.selected_stock = stock
        if c_del.button("➖", key=f"del_{stock}"):
            st.session_state.portfolio.remove(stock)
            st.rerun()

# --- 3. VERİ ÇEKME VE TÜRKÇE ANALİZ ---
if 'selected_stock' not in st.session_state:
    st.session_state.selected_stock = st.session_state.portfolio[0]

@st.cache_data(ttl=600)
def get_stock_report(symbol):
    try:
        t = yf.Ticker(symbol)
        return t.info, t.history(period="1y")
    except: return None, None

info, hist = get_stock_report(st.session_state.selected_stock)

# --- 4. ANA EKRAN ---
if info and not hist.empty:
    last_p = hist['Close'].iloc[-1]
    
    # Teknik Motor
    rsi = 100 - (100 / (1 + (hist['Close'].diff().clip(lower=0).rolling(14).mean() / -hist['Close'].diff().clip(upper=0).rolling(14).mean()).iloc[-1]))
    ma20 = hist['Close'].rolling(20).mean().iloc[-1]
    
    st.markdown("<div class='main-card'>", unsafe_allow_html=True)
    
    # Şirket Kimliği
    st.markdown(f"### {info.get('longName', st.session_state.selected_stock)}")
    st.metric("Güncel Fiyat", f"{last_p:,.2f} {info.get('currency', '')}")

    # AI Karar Alanı
    st.markdown("---")
    score = 0
    reasons = []
    if rsi < 35: score += 2; reasons.append("Teknik veriler aşırı satıma işaret ediyor, alım fırsatı olabilir.")
    elif rsi > 65: score -= 2; reasons.append("Teknik veriler aşırı alıma işaret ediyor, kâr realizasyonu beklenebilir.")
    if last_p > ma20: score += 1; reasons.append("Fiyat kısa vadeli trendin (MA20) üzerinde seyrediyor.")
    
    karar = "GÜÇLÜ AL" if score >= 2 else "GÜÇLÜ SAT" if score <= -2 else "NÖTR / BEKLE"
    st.markdown(f"<div class='decision-title'>{karar}</div>", unsafe_allow_html=True)
    
    for r in reasons:
        st.write(f"✅ {r}")

    # Şirket Profili (Türkçe Analizli)
    st.markdown("---")
    st.markdown("#### 🏢 Şirket Profili & Temel Veriler")
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Piyasa Değeri", f"{info.get('marketCap', 0)/1e9:.2f}B")
    col2.metric("F/K Oranı", f"{info.get('trailingPE', 'N/A')}")
    col3.metric("Özkaynak Karlılığı", f"%{info.get('returnOnEquity', 0)*100:.2f}")

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("##### 📝 Faaliyet Özeti")
    desc = info.get('longBusinessSummary', 'Şirket bilgisi yüklenemedi.')
    st.markdown(f"<div class='brief-box'><b>Yapay Zeka Özeti:</b> {info.get('longName')} firması, {info.get('sector')} sektöründe faaliyet gösteren bir kuruluştur.<br><br><i>{desc[:800]}...</i></div>", unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)
else:
    st.error("Veri bağlantısı kurulamadı. Lütfen sembolü kontrol edin.")
