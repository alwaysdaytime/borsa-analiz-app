import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np

# --- 1. AYARLAR VE PROFESYONEL TEMA ---
st.set_page_config(page_title="Vision Strategic AI | Kesin Karar", layout="wide")

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
    
    /* Öneri Butonu Tasarımı */
    .recommendation-box {
        padding: 20px 30px;
        border-radius: 15px;
        color: white;
        font-weight: 800;
        font-size: 1.8rem;
        text-align: center;
        margin-bottom: 25px;
        text-transform: uppercase;
        letter-spacing: 2px;
        box-shadow: 0 8px 20px rgba(0,0,0,0.1);
    }
    
    .brief-box {
        background: #f8faff; padding: 25px; border-radius: 18px;
        border-left: 6px solid #1a73e8; color: #1e293b; line-height: 1.8;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. PORTFÖY YÖNETİMİ ---
if 'portfolio' not in st.session_state:
    st.session_state.portfolio = ["THYAO.IS", "EREGL.IS", "SISE.IS", "BTC-USD"]

st.markdown("<h2 style='color:#1a73e8; margin-top:0;'>💠 Vision AI Strategic Terminal</h2>", unsafe_allow_html=True)
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

# --- 3. ANALİZ MOTORU ---
@st.cache_data(ttl=300)
def get_analysis(symbol):
    try:
        t = yf.Ticker(symbol)
        df = t.history(period="1y")
        if df.empty: return None, None
        
        # Teknik Göstergeler
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
        df['RSI'] = 100 - (100 / (1 + (gain / loss)))
        df['EMA20'] = df['Close'].ewm(span=20, adjust=False).mean()
        df['EMA50'] = df['Close'].ewm(span=50, adjust=False).mean()
        df['Vol_MA'] = df['Volume'].rolling(20).mean()
        
        return t.info, df
    except: return None, None

info, hist = get_analysis(st.session_state.selected_stock)

# --- 4. ANA PANEL ---
if info and hist is not None:
    last_p = hist['Close'].iloc[-1]
    rsi = hist['RSI'].iloc[-1]
    ema20 = hist['EMA20'].iloc[-1]
    ema50 = hist['EMA50'].iloc[-1]
    vol_now = hist['Volume'].iloc[-1]
    vol_avg = hist['Vol_MA'].iloc[-1]

    st.markdown("<div class='main-card'>", unsafe_allow_html=True)
    
    # Başlık ve Fiyat
    st.markdown(f"### {info.get('longName', st.session_state.selected_stock)}")
    st.metric("Piyasa Fiyatı", f"{last_p:,.2f} {info.get('currency', '')}")
    
    st.markdown("---")

    # --- KARAR SKORLAMA (PUANLAMA) ---
    score = 0
    notlar = []

    # RSI Puanlaması
    if rsi < 30: score += 4; notlar.append("🔵 RSI: Aşırı Satım (Potansiyel Dönüş)")
    elif rsi < 45: score += 1; notlar.append("🟢 RSI: Alım Bölgesi")
    elif rsi > 70: score -= 4; notlar.append("🔴 RSI: Aşırı Alım (Riskli)")
    elif rsi > 55: score -= 1; notlar.append("🟠 RSI: Doygunluk Bölgesi")

    # Trend Puanlaması
    if last_p > ema20 and ema20 > ema50: score += 3; notlar.append("📈 Trend: Güçlü Boğa (EMA 20 > 50)")
    elif last_p < ema20: score -= 2; notlar.append("📉 Trend: Ayı Baskısı (EMA 20 Altında)")

    # Hacim Onayı
    if vol_now > vol_avg * 1.2:
        if last_p > hist['Close'].iloc[-2]: score += 2; notlar.append("📊 Hacim: Güçlü Alıcı Girişi")
        else: score -= 2; notlar.append("📊 Hacim: Güçlü Satıcı Baskısı")

    # --- KESİN ÖNERİ BELİRLEME ---
    if score >= 6: 
        oneri, renk = "GÜÇLÜ AL", "linear-gradient(135deg, #10b981, #059669)"
    elif 2 <= score < 6: 
        oneri, renk = "AL", "linear-gradient(135deg, #34d399, #10b981)"
    elif -2 < score < 2: 
        oneri, renk = "TUT / NÖTR", "linear-gradient(135deg, #64748b, #475569)"
    elif -6 < score <= -2: 
        oneri, renk = "SAT", "linear-gradient(135deg, #f87171, #ef4444)"
    else: 
        oneri, renk = "GÜÇLÜ SAT", "linear-gradient(135deg, #ef4444, #b91c1c)"

    # Öneri Kutusunu Göster
    st.markdown(f"""
        <div class="recommendation-box" style="background: {renk};">
            Yapay Zeka Önerisi: {oneri}
        </div>
    """, unsafe_allow_html=True)

    # Strateji Raporu
    st.markdown("#### 🤖 Strateji Detay Notları")
    for n in notlar:
        st.write(n)

    st.markdown("---")
    
    # Şirket Röntgeni
    st.markdown("#### 🏢 Finansal Röntgen")
    f1, f2, f3, f4 = st.columns(4)
    f1.metric("F/K Oranı", f"{info.get('trailingPE', 'N/A')}")
    f2.metric("Piyasa Değeri", f"{info.get('marketCap', 0)/1e9:.2f}B")
    f3.metric("52H Zirve", f"{info.get('fiftyTwoWeekHigh', 0):,.2f}")
    f4.metric("Brüt Kar Marjı", f"%{info.get('grossMargins', 0)*100:.1f}")

    st.markdown("<br>", unsafe_allow_html=True)
    
    # İş Özeti
    st.markdown("##### 📝 Kurumsal Profil")
    raw_desc = info.get('longBusinessSummary', 'Özet mevcut değil.')
    clean_desc = raw_desc[:900].replace("'", "").replace('"', "")
    st.markdown(f"""
        <div class='brief-box'>
            <b>AI Analizi:</b> Seçili hisse için hesaplanan net puan 10 üzerinden {score+5:.1f} seviyesindedir. <br><br>
            <i>{clean_desc}...</i>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)
else:
    st.info("Veriler getiriliyor...")
