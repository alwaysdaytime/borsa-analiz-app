import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np

# --- 1. AYARLAR & TEMA ---
st.set_page_config(page_title="Vision Strategic AI | Deep Analysis", layout="wide")

st.markdown("""
    <style>
    header {visibility: hidden !important;}
    [data-testid="stSidebar"] {display: none !important;}
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');
    html, body, [class*="st-"] { font-family: 'Inter', sans-serif; background-color: #fcfdfe; }
    
    .main-card {
        background: white; border-radius: 24px; padding: 40px;
        border: 1px solid #eef2ff; box-shadow: 0 15px 35px rgba(0,0,0,0.02);
    }
    .status-badge {
        font-size: 2.5rem; font-weight: 800;
        background: linear-gradient(90deg, #1a73e8, #9b72f3, #d96570);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    }
    .score-meter {
        background: #f1f5f9; border-radius: 12px; height: 10px; width: 100%; margin: 10px 0;
    }
    .brief-box {
        background: #f8faff; padding: 25px; border-radius: 18px;
        border-left: 6px solid #1a73e8; color: #1e293b; line-height: 1.8;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. ÜST PANEL & PORTFÖY ---
if 'portfolio' not in st.session_state:
    st.session_state.portfolio = ["THYAO.IS", "EREGL.IS", "SISE.IS", "BTC-USD"]

st.markdown("<h2 style='color:#1a73e8; margin-top:0;'>💠 Vision AI Deep Analysis Terminal</h2>", unsafe_allow_html=True)
c1, c2, c3 = st.columns([2, 4, 2])

with c1:
    selected = st.selectbox("Hisse Seçimi", st.session_state.portfolio, label_visibility="collapsed")
    st.session_state.selected_stock = selected
with c2:
    sub_c1, sub_c2, sub_c3 = st.columns([3, 1, 1])
    new_s = sub_c1.text_input("Yeni Ekle", placeholder="Sembol (Örn: AAPL)", label_visibility="collapsed")
    if sub_c2.button("➕ Ekle"):
        if new_s and new_s.upper() not in st.session_state.portfolio:
            st.session_state.portfolio.append(new_s.upper())
            st.rerun()
    if sub_c3.button("➖ Sil"):
        if len(st.session_state.portfolio) > 1:
            st.session_state.portfolio.remove(st.session_state.selected_stock)
            st.session_state.selected_stock = st.session_state.portfolio[0]
            st.rerun()

# --- 3. DERİN ANALİZ MOTORU ---
@st.cache_data(ttl=300)
def get_deep_report(symbol):
    try:
        t = yf.Ticker(symbol)
        df = t.history(period="1y")
        if df.empty: return None, None
        
        # 1. RSI & Stokastik Yaklaşımı
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
        df['RSI'] = 100 - (100 / (1 + (gain / loss)))
        
        # 2. Trend Katmanları (EMA daha hassastır)
        df['EMA20'] = df['Close'].ewm(span=20, adjust=False).mean()
        df['EMA50'] = df['Close'].ewm(span=50, adjust=False).mean()
        
        # 3. Hacim Onayı (OBV Benzeri Basitleştirilmiş)
        df['Vol_Trend'] = df['Volume'].rolling(20).mean()
        
        # 4. Volatilite & Standart Sapma
        df['Std_Dev'] = df['Close'].rolling(20).std()
        
        return t.info, df
    except: return None, None

info, hist = get_deep_report(st.session_state.selected_stock)

# --- 4. ANALİZ PANELİ ---
if info and hist is not None:
    # Veri Çıkarımı
    last_p = hist['Close'].iloc[-1]
    rsi = hist['RSI'].iloc[-1]
    ema20 = hist['EMA20'].iloc[-1]
    ema50 = hist['EMA50'].iloc[-1]
    vol_now = hist['Volume'].iloc[-1]
    vol_avg = hist['Vol_Trend'].iloc[-1]
    std = hist['Std_Dev'].iloc[-1]

    st.markdown("<div class='main-card'>", unsafe_allow_html=True)
    st.markdown(f"### {info.get('longName', st.session_state.selected_stock)}")
    st.metric("Piyasa Fiyatı", f"{last_p:,.2f} {info.get('currency', '')}", f"{((last_p/hist['Close'].iloc[-2])-1)*100:.2f}%")
    
    st.markdown("---")

    # --- GELİŞMİŞ SKORLAMA SİSTEMİ ---
    score = 0
    max_score = 10
    detaylar = []

    # A. Momentum (3 Puan)
    if rsi < 30: score += 3; detaylar.append("🔵 **Momentum:** Aşırı satış bölgesi. Tarihsel olarak buradan dönüş ihtimali yüksek (%85).")
    elif rsi < 45: score += 1.5; detaylar.append("🟢 **Momentum:** Toparlanma bölgesinde, güç topluyor.")
    elif rsi > 70: score -= 3; detaylar.append("🔴 **Momentum:** Aşırı alım sinyali. Kar realizasyonu için kritik seviye.")

    # B. Trend Onayı (3 Puan)
    if last_p > ema20 and ema20 > ema50:
        score += 3; detaylar.append("📈 **Trend:** Tam boğa dizilimi (Golden Alignment). Yön yukarı.")
    elif last_p < ema20 and ema20 < ema50:
        score -= 3; detaylar.append("📉 **Trend:** Ayı piyasası baskısı altında. Düşüş trendi korunuyor.")

    # C. Hacim ve Para Girişi (2 Puan)
    if vol_now > vol_avg * 1.3 and last_p > hist['Close'].iloc[-2]:
        score += 2; detaylar.append("📊 **Hacim:** Fiyat artışı güçlü hacimle destekleniyor. Kurumsal ilgi olabilir.")
    elif vol_now > vol_avg * 1.3 and last_p < hist['Close'].iloc[-2]:
        score -= 2; detaylar.append("📊 **Hacim:** Satış baskısı yüksek hacimli. Dikkatli olunmalı.")

    # D. Volatilite (2 Puan)
    if std < (hist['Std_Dev'].mean()):
        score += 1; detaylar.append("⚖️ **Stabilite:** Düşük volatilite. Hareketin sağlıklı ve sürdürülebilir olduğunu gösterir.")

    # Karar Hesaplama
    confidence = (abs(score) / max_score) * 100
    if score >= 5: karar, renk = "KESİN AL (GÜÇLÜ)", "#10b981"
    elif score > 0: karar, renk = "TEMKİNLİ AL", "#34d399"
    elif score <= -5: karar, renk = "KESİN SAT (RİSKLİ)", "#ef4444"
    elif score < 0: karar, renk = "AZALT / BEKLE", "#f87171"
    else: karar, renk = "NÖTR / YÖNSÜZ", "#64748b"

    st.markdown(f"<div class='status-badge' style='background: linear-gradient(90deg, {renk}, #9b72f3); -webkit-background-clip: text;'>{karar}</div>", unsafe_allow_html=True)
    st.write(f"**Yapay Zeka Güven Skoru:** %{min(confidence, 100):.1f}")
    
    st.markdown("#### 🤖 Derin Strateji Raporu")
    for d in detaylar:
        st.write(d)

    st.markdown("---")
    # Finansal Özet
    st.markdown("#### 🏢 Şirket Röntgeni")
    f1, f2, f3, f4 = st.columns(4)
    f1.metric("F/K Oranı", f"{info.get('trailingPE', 'N/A')}")
    f2.metric("Piyasa Değeri", f"{info.get('marketCap', 0)/1e9:.2f}B")
    f3.metric("52H Zirve", f"{info.get('fiftyTwoWeekHigh', 0):,.2f}")
    f4.metric("Brüt Kar Marjı", f"%{info.get('grossMargins', 0)*100:.1f}")

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("##### 📝 Kurumsal Analiz ve Faaliyet")
    summary = info.get('longBusinessSummary', 'Veri yok.')
    st.markdown(f"<div class='brief-box'><b>Yapay Zeka Ö
