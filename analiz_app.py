import streamlit as st
import yfinance as yf
import pandas as pd

# --- 1. AYARLAR & TEMA ---
st.set_page_config(page_title="Vision Strategic AI", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;500;700&display=swap');
    html, body, [class*="st-"] { font-family: 'Space Grotesk', sans-serif; background-color: #f8fafc; }
    
    /* Yan Panel Modernizasyonu */
    section[data-testid="stSidebar"] { background-color: #ffffff; border-right: 1px solid #e2e8f0; padding-top: 20px; }
    
    /* Analiz Kartı */
    .analysis-card {
        background: white; border-radius: 24px; padding: 35px;
        border: 1px solid #e2e8f0; box-shadow: 0 10px 25px rgba(0,0,0,0.03);
    }
    .ai-decision {
        font-size: 2.2rem; font-weight: 800; margin-bottom: 15px;
        background: linear-gradient(90deg, #4285f4, #9b72f3, #d96570);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    }
    .info-box {
        background: #f1f5f9; padding: 20px; border-radius: 15px;
        border-left: 6px solid #4285f4; line-height: 1.6;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. PORTFÖY YÖNETİMİ (SOL PANEL) ---
if 'portfolio' not in st.session_state:
    st.session_state.portfolio = ["THYAO.IS", "SISE.IS", "EREGL.IS", "BTC-USD"]

with st.sidebar:
    st.markdown("<h2 style='color:#4285f4; margin-bottom:20px;'>Portföyüm</h2>", unsafe_allow_html=True)
    
    # Hisse Ekleme
    with st.container():
        c_in, c_bt = st.columns([3, 1])
        new_ticker = c_in.text_input("Sembol", placeholder="Örn: GARAN.IS", label_visibility="collapsed")
        if c_bt.button("➕"):
            if new_ticker and new_ticker.upper() not in st.session_state.portfolio:
                st.session_state.portfolio.append(new_ticker.upper())
                st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)
    
    # Hisse Listesi
    for stock in st.session_state.portfolio:
        col_name, col_del = st.columns([4, 1])
        if col_name.button(f"📄 {stock}", use_container_width=True):
            st.session_state.selected_stock = stock
        if col_del.button("➖", key=f"del_{stock}"):
            st.session_state.portfolio.remove(stock)
            st.rerun()

# Varsayılan Seçim
if 'selected_stock' not in st.session_state:
    st.session_state.selected_stock = st.session_state.portfolio[0]

# --- 3. VERİ ÇEKME MOTORU ---
@st.cache_data(ttl=300)
def get_deep_data(symbol):
    try:
        tk = yf.Ticker(symbol)
        inf = tk.info
        h = tk.history(period="1y")
        return inf, h
    except:
        return None, None

info, hist = get_deep_data(st.session_state.selected_stock)

# --- 4. STRATEJİK ANALİZ PANELİ (SAĞ) ---
if info and not hist.empty:
    # Finansal Hesaplamalar
    last_close = hist['Close'].iloc[-1]
    prev_close = hist['Close'].iloc[-2]
    change = ((last_close / prev_close) - 1) * 100
    rsi = 100 - (100 / (1 + (hist['Close'].diff().clip(lower=0).rolling(14).mean() / -hist['Close'].diff().clip(upper=0).rolling(14).mean()).iloc[-1]))
    ma20 = hist['Close'].rolling(20).mean().iloc[-1]

    st.markdown("<div class='analysis-card'>", unsafe_allow_html=True)
    
    # Başlık Alanı
    st.markdown(f"### {info.get('longName', st.session_state.selected_stock)}")
    c_p1, c_p2 = st.columns([1, 4])
    c_p1.metric("Güncel Fiyat", f"{last_close:,.2f}", f"{change:.2f}%")
    
    # AI ANALİZ VE YORUM (TÜRKÇE)
    st.markdown("---")
    
    score = 0
    notlar = []
    if rsi < 35: 
        score += 2; notlar.append("RSI değeri aşırı satım bölgesinde, teknik bir tepki yükselişi gelebilir.")
    elif rsi > 65: 
        score -= 2; notlar.append("RSI değeri aşırı alım bölgesinde, kâr satışlarına dikkat edilmeli.")
    
    if last_close > ma20: 
        score += 1; notlar.append("Fiyat 20 günlük ortalamanın üzerinde, kısa vadeli görünüm pozitif.")
    else:
        score -= 1; notlar.append("Fiyat 20 günlük ortalamanın altında, baskı devam edebilir.")

    if score >= 2: karar = "GÜÇLÜ AL SİNYALİ"; renk = "#10b981"
    elif score <= -2: karar = "GÜÇLÜ SAT SİNYALİ"; renk = "#ef4444"
    else: karar = "NÖTR / İZLEME"; renk = "#64748b"

    st.markdown(f"<div class='ai-decision' style='background:linear-gradient(90deg, {renk}, #9b72f3); -webkit-background-clip: text;'>{karar}</div>", unsafe_allow_html=True)
    
    st.markdown("#### 🤖 Yapay Zeka Strateji Raporu")
    for n in notlar:
        st.write(f"• {n}")

    # ŞİRKET DETAYLARI VE TÜRKÇE ÖZET
    st.markdown("---")
    st.markdown("#### 🏢 Şirket Profili & Detaylar")
    
    col_inf1, col_inf2 = st.columns(2)
    with col_inf1:
        st.write(f"**Sektör:** {info.get('sector', 'Belirtilmemiş')}")
        st.write(f"**Piyasa Değeri:** {info.get('marketCap', 0)/1e9:.2f} Milyar")
    with col_inf2:
        st.write(f"**F/K Oranı:** {info.get('trailingPE', 'N/A')}")
        st.write(f"**Temettü Verimi:** %{info.get('dividendYield', 0)*100:.2f}")

    # Şirket Açıklaması (Türkçe Çeviri Gerektiren Alan)
    summary = info.get('longBusinessSummary', 'Açıklama mevcut değil.')
    st.markdown("##### 📝 İş Özeti")
    # Not: Yahoo Finance verileri İngilizcedir. Buraya küçük bir not ekleyelim:
    st.markdown(f"<div class='info-box'><b>Yapay Zeka Notu:</b> Bu şirket {info.get('industry', 'sektöründe')} faaliyet göstermektedir. <br><br> <i>{summary[:800]}...</i></div>", unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)

else:
    st.warning("Seçili sembol için veri yüklenemedi. Lütfen Borsa İstanbul hisseleri için sonuna '.IS' eklediğinizden emin olun (Örn: THYAO.IS).")
