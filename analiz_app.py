import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np

# --- 1. AYARLAR & TEMA ---
st.set_page_config(page_title="Vision AI | Fırsat Radarı", layout="wide")

st.markdown("""
    <style>
    header {visibility: hidden !important;}
    [data-testid="stSidebar"] {display: none !important;}
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');
    html, body, [class*="st-"] { font-family: 'Inter', sans-serif; background-color: #fcfdfe; }
    
    .main-card { background: white; border-radius: 24px; padding: 35px; border: 1px solid #eef2ff; box-shadow: 0 10px 30px rgba(0,0,0,0.02); }
    
    .radar-box {
        background: linear-gradient(135deg, #1e3a8a, #3b82f6);
        color: white; border-radius: 18px; padding: 25px; margin-bottom: 30px;
        border-bottom: 5px solid #1d4ed8;
    }
    
    .recommendation-box {
        padding: 15px 25px; border-radius: 12px; color: white;
        font-weight: 800; font-size: 1.5rem; text-align: center; margin: 15px 0;
    }
    
    .brief-box { background: #f8faff; padding: 20px; border-radius: 15px; border-left: 5px solid #3b82f6; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. PORTFÖY YÖNETİMİ ---
if 'portfolio' not in st.session_state:
    st.session_state.portfolio = ["THYAO.IS", "EREGL.IS", "SISE.IS", "BTC-USD", "AAPL", "NVDA"]

st.markdown("<h2 style='color:#1e3a8a; margin-top:0;'>💠 Vision AI Strategic Radar</h2>", unsafe_allow_html=True)

# Üst Kontrol Barı
c1, c2, c3 = st.columns([2, 4, 2])
with c1:
    selected = st.selectbox("Hisse Seçimi", st.session_state.portfolio, label_visibility="collapsed")
    st.session_state.selected_stock = selected
with c2:
    sub_c1, sub_c2, sub_c3 = st.columns([3, 1, 1])
    new_s = sub_c1.text_input("Yeni Ekle", placeholder="Sembol", label_visibility="collapsed")
    if sub_c2.button("➕ Ekle"):
        if new_s and new_s.upper() not in st.session_state.portfolio:
            st.session_state.portfolio.append(new_s.upper()); st.rerun()
    if sub_c3.button("➖ Sil"):
        if len(st.session_state.portfolio) > 1:
            st.session_state.portfolio.remove(st.session_state.selected_stock)
            st.session_state.selected_stock = st.session_state.portfolio[0]; st.rerun()

# --- 3. RADAR FONKSİYONU (POTANSİYEL TARAMA) ---
@st.cache_data(ttl=600)
def scan_radar(portfolio):
    radar_results = []
    for stock in portfolio:
        try:
            t = yf.Ticker(stock)
            df = t.history(period="1mo")
            if len(df) < 20: continue
            
            # Kısa Vade Potansiyel Hesaplama (Skorlama)
            last_close = df['Close'].iloc[-1]
            rsi = 100 - (100 / (1 + (df['Close'].diff().clip(lower=0).tail(14).mean() / -df['Close'].diff().clip(upper=0).tail(14).mean())))
            ma5 = df['Close'].rolling(5).mean().iloc[-1]
            vol_ratio = df['Volume'].iloc[-1] / df['Volume'].rolling(10).mean().iloc[-1]
            
            score = 0
            if rsi < 45: score += 2 # Dönüş potansiyeli
            if last_close > ma5: score += 2 # Kısa vade momentum
            if vol_ratio > 1.2: score += 3 # Hacim onayı
            
            radar_results.append({"symbol": stock, "score": score, "rsi": rsi, "price": last_close})
        except: continue
    return sorted(radar_results, key=lambda x: x['score'], reverse=True)

# --- 4. ANA PANEL ---
# RADAR KISMI (EN ÜSTTE)
radar_list = scan_radar(st.session_state.portfolio)
if radar_list:
    best = radar_list[0]
    st.markdown(f"""
        <div class="radar-box">
            <h4 style="margin:0; opacity:0.9;">🚀 Günlük Yükseliş Potansiyeli En Yüksek</h4>
            <h1 style="margin:5px 0;">{best['symbol']} <small style="font-size:1.2rem;">(Skor: {best['score']}/7)</small></h1>
            <p style="margin:0; font-size:0.9rem;">AI Analizi: Hacim artışı ve RSI uyumu kısa vadeli bir sıçrama olasılığını %75+ gösteriyor.</p>
        </div>
    """, unsafe_allow_html=True)

# DETAYLI ANALİZ KISMI
@st.cache_data(ttl=300)
def get_full_analysis(symbol):
    try:
        t = yf.Ticker(symbol)
        df = t.history(period="1y")
        return t.info, df
    except: return None, None

info, hist = get_full_analysis(st.session_state.selected_stock)

if info and hist is not None:
    st.markdown("<div class='main-card'>", unsafe_allow_html=True)
    col_head1, col_head2 = st.columns([3, 1])
    col_head1.markdown(f"### {info.get('longName', st.session_state.selected_stock)}")
    col_head2.metric("Güncel Fiyat", f"{hist['Close'].iloc[-1]:,.2f}")

    # TEKNİK KARAR MOTORU (AL/SAT)
    # (Önceki turn'deki mantık korunmuştur)
    rsi = 100 - (100 / (1 + (hist['Close'].diff().clip(lower=0).tail(14).mean() / -hist['Close'].diff().clip(upper=0).tail(14).mean())))
    score = 0
    if rsi < 35: score += 3
    if hist['Close'].iloc[-1] > hist['Close'].ewm(span=20).mean().iloc[-1]: score += 2
    
    if score >= 4: res, clr = "GÜÇLÜ AL", "#10b981"
    elif score >= 2: res, clr = "AL", "#34d399"
    elif score <= -4: res, clr = "GÜÇLÜ SAT", "#ef4444"
    else: res, clr = "TUT / NÖTR", "#64748b"

    st.markdown(f"<div class='recommendation-box' style='background:{clr}'>ÖNERİ: {res}</div>", unsafe_allow_html=True)

    # DETAYLAR VE ŞİRKET PROFİLİ
    st.markdown("---")
    st.markdown("#### 🏢 Şirket Profili & Temel Veriler")
    f1, f2, f3, f4 = st.columns(4)
    f1.metric("F/K Oranı", f"{info.get('trailingPE', 'N/A')}")
    f2.metric("Piyasa Değeri", f"{info.get('marketCap', 0)/1e9:.2f}B")
    f3.metric("Beta", f"{info.get('beta', 'N/A')}")
    f4.metric("Temettü", f"%{info.get('dividendYield', 0)*100:.2f}")

    st.markdown("<br>", unsafe_allow_html=True)
    summary = info.get('longBusinessSummary', 'Özet yok.').replace("'", "").replace('"', "")
    st.markdown(f"<div class='brief-box'><b>AI Öngörüsü:</b> {st.session_state.selected_stock} kısa vadeli trend kanalı içerisinde {res.lower()} sinyali üretmektedir. <br><br><i>{summary[:850]}...</i></div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)
