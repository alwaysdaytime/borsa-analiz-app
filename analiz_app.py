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

# --- 2. ÜST PANEL YÖNETİMİ ---
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
        
        # --- TEKNİK VERİ GENİŞLETME ---
        # 1. RSI
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
        df['RSI'] = 100 - (100 / (1 + (gain / loss)))
        
        # 2. Hareketli Ortalamalar (Trend)
        df['SMA20'] = df['Close'].rolling(20).mean()
        df['SMA50'] = df['Close'].rolling(50).mean()
        
        # 3. Volatilite (ATR - Ortalama Gerçek Aralık)
        high_low = df['High'] - df['Low']
        df['ATR'] = high_low.rolling(14).mean()
        
        # 4. Hacim Trendi
        df['Vol_MA'] = df['Volume'].rolling(20).mean()
        
        return t.info, df
    except: return None, None

info, hist = get_advanced_report(st.session_state.selected_stock)

# --- 4. ANALİZ PANELİ ---
if info and hist is not None:
    # Son değerleri al
    p = hist['Close'].iloc[-1]
    rsi = hist['RSI'].iloc[-1]
    sma20 = hist['SMA20'].iloc[-1]
    sma50 = hist['SMA50'].iloc[-1]
    vol_now = hist['Volume'].iloc[-1]
    vol_avg = hist['Vol_MA'].iloc[-1]
    atr = hist['ATR'].iloc[-1]

    st.markdown("<div class='main-card'>", unsafe_allow_html=True)
    st.markdown(f"### {info.get('longName', st.session_state.selected_stock)}")
    st.metric("Piyasa Fiyatı", f"{p:,.2f} {info.get('currency', '')}", f"{((p/hist['Close'].iloc[-2])-1)*100:.2f}%")
    
    st.markdown("---")

    # --- AI KARAR ALGORİTMASI (Gelişmiş) ---
    score = 0
    notlar = []

    # A. Momentum Analizi
    if rsi < 30: score += 3; notlar.append("🔥 **Aşırı Ucuz:** RSI değeri kritik seviyenin altında, sert bir tepki gelebilir.")
    elif rsi < 45: score += 1; notlar.append("🟢 **Pozitif Birikim:** Momentum toparlanma emareleri gösteriyor.")
    elif rsi > 70: score -= 3; notlar.append("⚠️ **Aşırı Alım:** RSI doygunlukta, kâr satışları an meselesi olabilir.")
    
    # B. Trend ve Hacim Onayı
    if p > sma20 and sma20 > sma50:
        score += 2; notlar.append("📈 **Güçlü Trend:** Fiyat kısa ve orta vade ortalamaların üzerinde; 'Golden Cross' etkisi.")
    if vol_now > vol_avg * 1.5:
        score *= 1.2; notlar.append("📊 **Hacim Onayı:** Fiyat hareketi yüksek işlem hacmiyle destekleniyor, sinyal güvenilir.")

    # C. Volatilite Kontrolü
    if atr > hist['ATR'].mean() * 1.5:
        notlar.append("📉 **Dikkat:** Volatilite çok yüksek, ani fiyat hareketlerine karşı stop-loss kullanılmalı.")

    # Karar Sonucu
    if score >= 3: karar, renk = "GÜÇLÜ AL SİNYALİ", "#10b981"
    elif score >= 1: karar, renk = "AL (Kademeli)", "#34d399"
    elif score <= -3: karar, renk = "GÜÇLÜ SAT SİNYALİ", "#ef4444"
    elif score <= -1: karar, renk = "SAT (Azalt)", "#f87171"
    else: karar, renk = "NÖTR / BEKLE", "#64748b"

    st.markdown(f"<div class='status-badge' style='background: linear-gradient(90deg, {renk}, #9b72f3); -webkit-background-clip: text;'>{karar}</div>", unsafe_allow_html=True)
    
    st.markdown("#### 🤖 Gelişmiş Strateji Raporu")
    for n in notlar:
        st.write(n)

    # Temel Veriler
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
    st.markdown(f"<div class='brief-box'><b>Yapay Zeka Notu:</b> Bu varlık {info.get('industry', 'sektörü')} genelinde risk/getiri dengesini korumaktadır.<br><br><i>{summary[:900]}...</i></div>", unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)
else:
    st.error("Veri analiz motoru bu sembolü işleyemedi.")
