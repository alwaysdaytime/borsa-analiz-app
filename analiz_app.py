import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np

# --- 1. AYARLAR VE PROFESYONEL TEMA ---
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
        margin-bottom: 10px;
    }
    .brief-box {
        background: #f8faff; padding: 25px; border-radius: 18px;
        border-left: 6px solid #1a73e8; color: #1e293b; line-height: 1.8;
    }
    .metric-card {
        background: #ffffff; border: 1px solid #f0f2f6; border-radius: 12px; padding: 15px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. PORTFÖY YÖNETİMİ (Kalıcı Liste) ---
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
        
        # Teknik Göstergeler (Derinleştirilmiş)
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
        df['RSI'] = 100 - (100 / (1 + (gain / loss)))
        df['EMA20'] = df['Close'].ewm(span=20, adjust=False).mean()
        df['EMA50'] = df['Close'].ewm(span=50, adjust=False).mean()
        df['Vol_Trend'] = df['Volume'].rolling(20).mean()
        
        return t.info, df
    except: return None, None

info, hist = get_deep_report(st.session_state.selected_stock)

# --- 4. ANA PANEL ---
if info and hist is not None:
    last_p = hist['Close'].iloc[-1]
    rsi = hist['RSI'].iloc[-1]
    ema20 = hist['EMA20'].iloc[-1]
    ema50 = hist['EMA50'].iloc[-1]
    vol_now = hist['Volume'].iloc[-1]
    vol_avg = hist['Vol_Trend'].iloc[-1]

    st.markdown("<div class='main-card'>", unsafe_allow_html=True)
    
    # Fiyat ve Değişim
    change = ((last_p / hist['Close'].iloc[-2]) - 1) * 100
    st.markdown(f"### {info.get('longName', st.session_state.selected_stock)}")
    st.metric("Piyasa Fiyatı", f"{last_p:,.2f} {info.get('currency', '')}", f"{change:.2f}%")
    
    st.markdown("---")

    # --- GELİŞMİŞ SKORLAMA (KARAR MOTORU) ---
    score = 0
    max_score = 10
    detaylar = []

    # 1. Momentum (RSI)
    if rsi < 30: score += 3; detaylar.append("🔵 **Momentum:** Aşırı satış bölgesi. Tarihsel dönüş potansiyeli yüksek.")
    elif rsi > 70: score -= 3; detaylar.append("🔴 **Momentum:** Aşırı alım sinyali. Kar realizasyonu riski var.")
    else: score += 1; detaylar.append("🟡 **Momentum:** Nötr bölge, trend yönü bekleniyor.")

    # 2. Trend (EMA Cross)
    if last_p > ema20 and ema20 > ema50:
        score += 3; detaylar.append("📈 **Trend:** Güçlü Boğa dizilimi. Fiyat tüm ortalamaların üzerinde.")
    elif last_p < ema20:
        score -= 2; detaylar.append("📉 **Trend:** Ayı baskısı. Kısa vadeli ortalamanın altına sarkma var.")

    # 3. Hacim Onayı
    if vol_now > vol_avg * 1.2 and last_p > hist['Close'].iloc[-2]:
        score += 2; detaylar.append("📊 **Hacim:** Yükseliş güçlü para girişiyle destekleniyor.")
    
    # Karar ve Güven Skoru
    conf = (abs(score) / max_score) * 100
    if score >= 4: karar, renk = "GÜÇLÜ AL SİNYALİ", "#10b981"
    elif score <= -4: karar, renk = "GÜÇLÜ SAT SİNYALİ", "#ef4444"
    else: karar, renk = "NÖTR / İZLEME", "#64748b"

    st.markdown(f"<div class='status-badge' style='background: linear-gradient(90deg, {renk}, #9b72f3); -webkit-background-clip: text;'>{karar}</div>", unsafe_allow_html=True)
    st.write(f"**Yapay Zeka Güven Skoru:** %{min(conf, 100):.1f}")

    st.markdown("#### 🤖 Derin Strateji Raporu")
    for d in detaylar:
        st.write(d)

    st.markdown("---")
    
    # Şirket Röntgeni
    st.markdown("#### 🏢 Finansal Röntgen")
    f1, f2, f3, f4 = st.columns(4)
    f1.metric("F/K Oranı", f"{info.get('trailingPE', 'N/A')}")
    f2.metric("Piyasa Değeri", f"{info.get('marketCap', 0)/1e9:.2f}B")
    f3.metric("52H Zirve", f"{info.get('fiftyTwoWeekHigh', 0):,.2f}")
    f4.metric("Brüt Kar Marjı", f"%{info.get('grossMargins', 0)*100:.1f}")

    # İş Özeti (Syntax Hatası Giderilen Bölüm)
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("##### 📝 Kurumsal Analiz ve Faaliyet")
    raw_summary = info.get('longBusinessSummary', 'Şirket özeti mevcut değil.')
    clean_summary = raw_summary[:900].replace("'", "").replace('"', "") # Hatalı karakterleri temizle
    
    st.markdown(f"""
        <div class='brief-box'>
            <b>Yapay Zeka Öngörüsü:</b> {st.session_state.selected_stock} için teknik puanlama 
            10 üzerinden {score+5:.1f} olarak hesaplanmıştır. <br><br>
            <i>{clean_summary}...</i>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)
else:
    st.info("Veri analizi yapılıyor, lütfen bekleyin...")
