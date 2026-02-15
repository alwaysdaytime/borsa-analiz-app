import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np

# --- 1. AYARLAR & TEMA ---
st.set_page_config(page_title="Vision Strategic AI", layout="wide")

st.markdown("""
    <style>
    header {visibility: hidden !important;}
    [data-testid="stSidebar"] {display: none !important;}
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');
    html, body, [class*="st-"] { font-family: 'Inter', sans-serif; background-color: #fcfdfe; }
    
    .main-card {
        background: white; border-radius: 24px; padding: 35px;
        border: 1px solid #eef2ff; box-shadow: 0 10px 30px rgba(0,0,0,0.02);
    }
    .status-badge {
        font-size: 2.2rem; font-weight: 800;
        background: linear-gradient(90deg, #1a73e8, #9b72f3, #d96570);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    }
    .brief-box {
        background: #f8faff; padding: 25px; border-radius: 15px;
        border-left: 5px solid #1a73e8; color: #3c4043; line-height: 1.7;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. ÜST PANEL & PORTFÖY YÖNETİMİ ---
# Not: Local ortamda kalıcılık için session_state kullanılır. 
if 'portfolio' not in st.session_state:
    st.session_state.portfolio = ["THYAO.IS", "EREGL.IS", "SISE.IS", "BTC-USD"]

st.markdown("<h2 style='color:#1a73e8; margin-top:0;'>💠 Vision AI Strategic Terminal</h2>", unsafe_allow_html=True)
c1, c2, c3 = st.columns([2, 4, 2])

with c1:
    selected = st.selectbox("İzleme Listeniz", st.session_state.portfolio, label_visibility="collapsed")
    st.session_state.selected_stock = selected
with c2:
    sub_c1, sub_c2, sub_c3 = st.columns([3, 1, 1])
    new_s = sub_c1.text_input("Yeni Sembol Ekle", placeholder="Örn: AAPL", label_visibility="collapsed")
    if sub_c2.button("➕ Ekle"):
        if new_s and new_s.upper() not in st.session_state.portfolio:
            st.session_state.portfolio.append(new_s.upper())
            st.rerun()
    if sub_c3.button("➖ Sil"):
        if len(st.session_state.portfolio) > 1:
            st.session_state.portfolio.remove(st.session_state.selected_stock)
            st.session_state.selected_stock = st.session_state.portfolio[0]
            st.rerun()

# --- 3. GELİŞMİŞ ANALİZ MOTORU ---
@st.cache_data(ttl=300)
def get_advanced_report(symbol):
    try:
        t = yf.Ticker(symbol)
        df = t.history(period="1y")
        if df.empty: return None, None
        
        # RSI
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
        df['RSI'] = 100 - (100 / (1 + (gain / loss)))
        
        # SMA & Volatilite & Hacim
        df['SMA20'] = df['Close'].rolling(20).mean()
        df['SMA50'] = df['Close'].rolling(50).mean()
        df['ATR'] = (df['High'] - df['Low']).rolling(14).mean()
        df['Vol_MA'] = df['Volume'].rolling(20).mean()
        
        return t.info, df
    except: return None, None

info, hist = get_advanced_report(st.session_state.selected_stock)

# --- 4. ANALİZ PANELİ ---
if info and hist is not None:
    p = hist['Close'].iloc[-1]
    rsi = hist['RSI'].iloc[-1]
    sma20 = hist['SMA20'].iloc[-1]
    sma50 = hist['SMA50'].iloc[-1]
    vol_now = hist['Volume'].iloc[-1]
    vol_avg = hist['Vol_MA'].iloc[-1]

    st.markdown("<div class='main-card'>", unsafe_allow_html=True)
    st.markdown(f"### {info.get('longName', st.session_state.selected_stock)}")
    st.metric("Piyasa Fiyatı", f"{p:,.2f} {info.get('currency', '')}", f"{((p/hist['Close'].iloc[-2])-1)*100:.2f}%")
    
    st.markdown("---")

    # AI Karar Algoritması
    score = 0
    notlar = []
    if rsi < 30: score += 3; notlar.append("🔥 **Aşırı Ucuz:** Tepki alımları beklenebilir.")
    elif rsi > 70: score -= 3; notlar.append("⚠️ **Aşırı Alım:** Kâr realizasyonu riski yüksek.")
    if p > sma20 and sma20 > sma50: score += 2; notlar.append("📈 **Güçlü Trend:** Yön yukarı, ortalamalar destekliyor.")
    if vol_now > vol_avg * 1.5: score *= 1.2; notlar.append("📊 **Hacim Onayı:** Hareket güçlü bir işlem hacmiyle destekleniyor.")

    if score >= 3: karar, renk = "GÜÇLÜ AL SİNYALİ", "#10b981"
    elif score <= -3: karar, renk = "GÜÇLÜ SAT SİNYALİ", "#ef4444"
    else: karar, renk = "NÖTR / BEKLE", "#64748b"

    st.markdown(f"<div class='status-badge' style='background: linear-gradient(90deg, {renk}, #9b72f3); -webkit-background-clip: text;'>{karar}</div>", unsafe_allow_html=True)
    
    st.markdown("#### 🤖 Gelişmiş Strateji Raporu")
    for n in notlar:
        st.write(n)

    st.markdown("---")
    st.markdown("#### 🏢 Finansal Röntgen")
    d1, d2, d3, d4 = st.columns(4)
    d1.metric("F/K Oranı", f"{info.get('trailingPE', 'N/A')}")
    d2.metric("Piyasa Değeri", f"{info.get('marketCap', 0)/1e9:.2f}B")
    d3.metric("Beta (Risk)", f"{info.get('beta', 'N/A')}")
    d4.metric("Özsermaye Kârı", f"%{info.get('returnOnEquity', 0)*100:.2f}")

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("##### 📝 Kurumsal Faaliyet Analizi")
    summary = info.get('longBusinessSummary', 'Özet bilgisi çekilemedi.')
    st.markdown(f"<div class='brief-box'><b>Yapay Zeka Notu:</b> {info.get('longName')}, {info.get('sector')} sektöründeki yerini korumaktadır.<br><br><i>{summary[:900]}...</i></div>", unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)
else:
    st.info("Analiz için bir hisse seçin.")
