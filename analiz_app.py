import streamlit as st
import yfinance as yf
import pandas as pd

# --- 1. AYARLAR & TEMA ---
st.set_page_config(page_title="Vision Strategic AI", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;500;700&display=swap');
    html, body, [class*="st-"] { font-family: 'Space Grotesk', sans-serif; background-color: #fcfdfe; }
    
    /* Sol Panel (Hisseler) */
    .ticker-card {
        background: white; padding: 10px 15px; border-radius: 12px;
        margin-bottom: 8px; border: 1px solid #eef2ff;
        display: flex; justify-content: space-between; align-items: center;
        box-shadow: 0 2px 4px rgba(0,0,0,0.02);
    }
    
    /* Sağ Panel (AI Analiz) */
    .analysis-card {
        background: rgba(255, 255, 255, 0.8); backdrop-filter: blur(10px);
        border-radius: 24px; padding: 30px; border: 1px solid #e2e8f0;
        box-shadow: 0 20px 40px rgba(0,0,0,0.05);
    }
    .ai-decision {
        font-size: 2rem; font-weight: 800; margin-bottom: 10px;
        background: linear-gradient(90deg, #4285f4, #9b72f3);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    }
    .profile-box {
        background: #f8faff; padding: 20px; border-radius: 15px;
        border-left: 5px solid #4285f4; margin-top: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. PORTFÖY YÖNETİMİ (SOL ÜST) ---
if 'portfolio' not in st.session_state:
    st.session_state.portfolio = ["THYAO.IS", "SISE.IS", "EREGL.IS", "BTC-USD"]

with st.sidebar:
    st.title("💠 Vision Portföy")
    
    # Hisse Ekleme Bölümü
    col_add, col_btn = st.columns([3, 1])
    new_stock = col_add.text_input("Sembol Ekle", placeholder="Örn: AAPL", label_visibility="collapsed")
    if col_btn.button("➕"):
        if new_stock and new_stock.upper() not in st.session_state.portfolio:
            st.session_state.portfolio.append(new_stock.upper())
            st.rerun()

    st.markdown("---")
    
    # Hisse Listesi ve Çıkartma
    for stock in st.session_state.portfolio:
        c1, c2 = st.columns([4, 1])
        if c1.button(f"🔍 {stock}", use_container_width=True):
            st.session_state.selected_stock = stock
        if c2.button("➖", key=f"del_{stock}"):
            st.session_state.portfolio.remove(stock)
            st.rerun()

# Varsayılan seçim
if 'selected_stock' not in st.session_state:
    st.session_state.selected_stock = st.session_state.portfolio[0]

# --- 3. VERİ ÇEKME VE ANALİZ ---
@st.cache_data(ttl=300)
def get_deep_data(symbol):
    try:
        ticker = yf.Ticker(symbol)
        info = ticker.info
        hist = ticker.history(period="1y")
        return info, hist
    except:
        return None, None

info, hist = get_deep_data(st.session_state.selected_stock)

# --- 4. ANALİZ EKRANI (SAĞ TARAF) ---
if info and not hist.empty:
    col_main = st.container()
    
    with col_main:
        st.markdown(f"<div class='analysis-card'>", unsafe_allow_html=True)
        
        # ÜST BAŞLIK: Şirket Kimliği
        name = info.get('longName', st.session_state.selected_stock)
        current_price = info.get('currentPrice', hist['Close'].iloc[-1])
        currency = info.get('currency', 'USD')
        
        st.markdown(f"### {name} ({st.session_state.selected_stock})")
        st.markdown(f"<h1 style='margin:0;'>{current_price:,.2f} <small style='font-size:1rem;'>{currency}</small></h1>", unsafe_allow_html=True)

        # AI ANALİZ VE KARAR MOTORU
        st.markdown("---")
        
        # Teknik Hesaplamalar
        rsi = 100 - (100 / (1 + (hist['Close'].diff().clip(lower=0).rolling(14).mean() / -hist['Close'].diff().clip(upper=0).rolling(14).mean()).iloc[-1]))
        ma20 = hist['Close'].rolling(20).mean().iloc[-1]
        ma50 = hist['Close'].rolling(50).mean().iloc[-1]
        vol_avg = hist['Volume'].tail(10).mean()
        vol_now = hist['Volume'].iloc[-1]

        # Karar Mekanizması
        score = 0
        reasons = []
        if rsi < 35: score += 2; reasons.append("Fiyat teknik olarak aşırı satım bölgesinde (Ucuz).")
        if rsi > 65: score -= 2; reasons.append("Fiyat teknik olarak doygunluğa ulaşmış (Pahalı).")
        if current_price > ma20: score += 1; reasons.append("Kısa vadeli trend yukarı yönlü (Pozitif).")
        if vol_now > vol_avg: score += 1; reasons.append("İşlem hacmi artıyor, ilgi yüksek.")
        
        if score >= 2: decision = "GÜÇLÜ AL (BULLISH)"; desc = "Veriler, yukarı yönlü bir kırılımın eşiğinde olduğumuzu gösteriyor."
        elif score <= -2: decision = "GÜÇLÜ SAT (BEARISH)"; desc = "Veriler, kâr satışı veya düşüş trendinin hızlanabileceğini fısıldıyor."
        else: decision = "BEKLE / NÖTR"; desc = "Piyasada net bir yön tayini yok, kademeli izleme önerilir."

        st.markdown(f"<div class='ai-decision'>{decision}</div>", unsafe_allow_html=True)
        st.write(f"**Gemini Strateji Notu:** {desc}")
        
        # Detaylı Veri Tablosu
        st.markdown("#### 📊 Finansal Detaylar")
        d1, d2, d3, d4 = st.columns(4)
        d1.metric("F/K Oranı", f"{info.get('trailingPE', 'N/A')}")
        d2.metric("Piyasa Değeri", f"{info.get('marketCap', 0)/1e9:.2f}B")
        d3.metric("52H Zirve", f"{info.get('fiftyTwoWeekHigh', 0):,.2f}")
        d4.metric("RSI Değeri", f"{rsi:.1f}")

        # ŞİRKET PROFİLİ
        st.markdown("#### 🏢 Şirket Profili")
        st.markdown(f"""
            <div class='profile-box'>
                <b>Sektör:</b> {info.get('sector', 'N/A')} <br>
                <b>Endüstri:</b> {info.get('industry', 'N/A')} <br><br>
                {info.get('longBusinessSummary', 'Şirket özeti bulunamadı.')[:600]}...
            </div>
        """, unsafe_allow_html=True)
        
        st.markdown("</div>", unsafe_allow_html=True)
else:
    st.error("Hisse verisi çekilemedi. Lütfen sembolün doğruluğunu kontrol edin (Örn: Borsa İstanbul için .IS ekleyin).")
