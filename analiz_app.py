import streamlit as st
import yfinance as yf
import pandas as pd

# --- 1. AYARLAR & TEMA (FULL CLEAN) ---
st.set_page_config(page_title="Vision Strategic AI", layout="wide")

st.markdown("""
    <style>
    /* Üst ve Yan Menü Kalıntılarını Temizle */
    header {visibility: hidden !important;}
    [data-testid="stSidebar"] {display: none !important;}
    .st-emotion-cache-16idsys {display: none !important;}
    
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');
    html, body, [class*="st-"] { font-family: 'Inter', sans-serif; background-color: #fcfdfe; }
    
    /* Üst Panel (Hisse Seçim Alanı) */
    .top-bar {
        background: #ffffff;
        padding: 15px 25px;
        border-radius: 15px;
        border: 1px solid #e2e8f0;
        margin-bottom: 25px;
        display: flex;
        align-items: center;
        gap: 15px;
    }
    
    /* Karar Kartı */
    .main-card {
        background: white;
        border-radius: 24px;
        padding: 35px;
        border: 1px solid #eef2ff;
        box-shadow: 0 10px 30px rgba(0,0,0,0.02);
    }
    
    .status-badge {
        font-size: 2.2rem; font-weight: 800;
        background: linear-gradient(90deg, #1a73e8, #9b72f3);
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

# Üst Bar Tasarımı
with st.container():
    st.markdown("<h2 style='color:#1a73e8; margin-top:0;'>💠 Vision AI Strategic Terminal</h2>", unsafe_allow_html=True)
    
    c1, c2, c3 = st.columns([2, 4, 2])
    
    # Hisse Seçimi (Dropdown - Üstte)
    with c1:
        selected = st.selectbox("İzleme Listeniz", st.session_state.portfolio, label_visibility="collapsed")
        st.session_state.selected_stock = selected
        
    # Yeni Hisse Ekle/Çıkar
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

# --- 3. VERİ VE ANALİZ ---
@st.cache_data(ttl=300)
def get_report(symbol):
    try:
        t = yf.Ticker(symbol)
        return t.info, t.history(period="1y")
    except: return None, None

info, hist = get_report(st.session_state.selected_stock)

# --- 4. ANALİZ EKRANI ---
if info and not hist.empty:
    p = hist['Close'].iloc[-1]
    prev_p = hist['Close'].iloc[-2]
    chg = ((p / prev_p) - 1) * 100
    
    # Teknik Reçete
    rsi = 100 - (100 / (1 + (hist['Close'].diff().clip(lower=0).rolling(14).mean() / -hist['Close'].diff().clip(upper=0).rolling(14).mean()).iloc[-1]))
    ma20 = hist['Close'].rolling(20).mean().iloc[-1]
    
    st.markdown("<div class='main-card'>", unsafe_allow_html=True)
    
    # Üst Bilgi
    st.markdown(f"### {info.get('longName', st.session_state.selected_stock)}")
    st.metric("Piyasa Değeri", f"{p:,.2f} {info.get('currency', '')}", f"{chg:.2f}%")
    
    st.markdown("---")
    
    # AI Karar Motoru
    score = 0
    notes = []
    if rsi < 35: score += 2; notes.append("RSI aşırı satımda: Teknik bir düzeltme/yükseliş muhtemel.")
    elif rsi > 65: score -= 2; notes.append("RSI aşırı alımda: Fiyat doygunluğa ulaştı, kâr satışı riski.")
    if p > ma20: score += 1; notes.append("Trend Pozitif: Fiyat kısa vade ortalamanın üzerinde.")
    else: score -= 1; notes.append("Trend Negatif: Satış baskısı kısa vadede devam ediyor.")

    karar = "GÜÇLÜ AL SİNYALİ" if score >= 2 else "GÜÇLÜ SAT SİNYALİ" if score <= -2 else "NÖTR / BEKLE"
    st.markdown(f"<div class='status-badge'>{karar}</div>", unsafe_allow_html=True)
    
    st.markdown("#### 🤖 Strateji Notları")
    for n in notes:
        st.write(f"• {n}")

    # Şirket Profili
    st.markdown("---")
    st.markdown("#### 🏢 Kurumsal Profil & Temel Veriler")
    
    d1, d2, d3, d4 = st.columns(4)
    d1.metric("Piyasa Değeri", f"{info.get('marketCap', 0)/1e9:.2f}B")
    d2.metric("F/K Oranı", f"{info.get('trailingPE', 'N/A')}")
    d3.metric("F/DD Oranı", f"{info.get('priceToBook', 'N/A')}")
    d4.metric("Temettü Verimi", f"%{info.get('dividendYield', 0)*100:.2f}")

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("##### 📝 İş Özeti (AI Analiz)")
    desc = info.get('longBusinessSummary', 'Açıklama mevcut değil.')
    st.markdown(f"<div class='brief-box'><b>Özet:</b> {info.get('longName')} kuruluşu, {info.get('sector')} sektöründe liderlik/operasyon yürütmektedir.<br><br><i>{desc[:900]}...</i></div>", unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)
else:
    st.error("Veri çekilemedi. Lütfen sembolü (Örn: THYAO.IS) kontrol edip tekrar deneyin.")
