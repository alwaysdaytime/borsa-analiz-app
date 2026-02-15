import streamlit as st
import yfinance as yf
import pandas as pd

# --- 1. AYARLAR & TEMA ---
st.set_page_config(page_title="Vision Strategic AI", layout="wide")

# CSS ile "keyboard_double" ve diğer gereksiz ikon yazılarını kökten gizliyoruz
st.markdown("""
    <style>
    /* O inatçı yazıyı ve gereksiz ikon metinlerini gizle */
    [data-testid="stSidebarNav"] span, 
    .st-emotion-cache-6qob1r, 
    [data-testid="stSidebarNav"] svg {
        display: none !important;
    }
    
    @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;500;700&display=swap');
    html, body, [class*="st-"] { font-family: 'Space Grotesk', sans-serif; background-color: #f8fafc; }
    
    /* Yan Panel Tasarımı */
    section[data-testid="stSidebar"] { 
        background-color: #ffffff; 
        border-right: 1px solid #e2e8f0; 
    }
    
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
        border-left: 6px solid #4285f4; line-height: 1.6; color: #1e293b;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. PORTFÖY YÖNETİMİ (SOL PANEL) ---
if 'portfolio' not in st.session_state:
    st.session_state.portfolio = ["THYAO.IS", "SISE.IS", "EREGL.IS", "BTC-USD"]

with st.sidebar:
    st.markdown("<h2 style='color:#4285f4; margin-top:0;'>Portföyüm</h2>", unsafe_allow_html=True)
    
    # Hisse Ekleme
    c_in, c_bt = st.columns([3, 1])
    new_ticker = c_in.text_input("Sembol", placeholder="Örn: GARAN.IS", label_visibility="collapsed")
    if c_bt.button("➕"):
        if new_ticker and new_ticker.upper() not in st.session_state.portfolio:
            st.session_state.portfolio.append(new_ticker.upper())
            st.rerun()

    st.markdown("---")
    
    # Hisse Listesi
    for stock in st.session_state.portfolio:
        col_name, col_del = st.columns([4, 1])
        if col_name.button(f"📄 {stock}", use_container_width=True):
            st.session_state.selected_stock = stock
        if col_del.button("➖", key=f"del_{stock}"):
            st.session_state.portfolio.remove(stock)
            if st.session_state.selected_stock == stock and len(st.session_state.portfolio) > 0:
                st.session_state.selected_stock = st.session_state.portfolio[0]
            st.rerun()

# Varsayılan Seçim
if 'selected_stock' not in st.session_state:
    st.session_state.selected_stock = st.session_state.portfolio[0]

# --- 3. VERİ ÇEKME ---
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
    last_p = hist['Close'].iloc[-1]
    prev_p = hist['Close'].iloc[-2]
    degisim = ((last_p / prev_p) - 1) * 100
    
    # Teknik Analiz Verileri
    rsi = 100 - (100 / (1 + (hist['Close'].diff().clip(lower=0).rolling(14).mean() / -hist['Close'].diff().clip(upper=0).rolling(14).mean()).iloc[-1]))
    ma20 = hist['Close'].rolling(20).mean().iloc[-1]

    st.markdown("<div class='analysis-card'>", unsafe_allow_html=True)
    
    # Başlık Alanı
    st.markdown(f"### {info.get('longName', st.session_state.selected_stock)}")
    st.metric("Güncel Değer", f"{last_p:,.2f} {info.get('currency', '')}", f"{degisim:.2f}%")
    
    st.markdown("---")
    
    # AI KARAR MOTORU
    score = 0
    analiz_notlari = []
    if rsi < 35: 
        score += 2; analiz_notlari.append("Fiyat teknik olarak 'aşırı satım' bölgesinde; alıcıların iştahı artabilir.")
    elif rsi > 65: 
        score -= 2; analiz_notlari.append("Fiyat teknik olarak 'aşırı alım' bölgesinde; kâr satışları görülebilir.")
    
    if last_p > ma20: 
        score += 1; analiz_notlari.append("Fiyat 20 günlük hareketli ortalamanın üzerinde; trend pozitif.")
    else:
        score -= 1; analiz_notlari.append("Fiyat 20 günlük ortalamanın altında; kısa vadeli baskı hakim.")

    if score >= 2: karar, renk = "GÜÇLÜ AL SİNYALİ", "#10b981"
    elif score <= -2: karar, renk = "GÜÇLÜ SAT SİNYALİ", "#ef4444"
    else: karar, renk = "NÖTR / İZLEME", "#64748b"

    st.markdown(f"<div class='ai-decision' style='background:linear-gradient(90deg, {renk}, #9b72f3); -webkit-background-clip: text;'>{karar}</div>", unsafe_allow_html=True)
    
    st.markdown("#### 🤖 Strateji Özeti")
    for n in analiz_notlari:
        st.write(f"✅ {n}" if score >= 0 else f"⚠️ {n}")

    # ŞİRKET BİLGİLERİ
    st.markdown("---")
    st.markdown("#### 🏢 Şirket Profili")
    
    c1, c2, c3 = st.columns(3)
    c1.write(f"**Sektör:** {info.get('sector', 'Bilinmiyor')}")
    c2.write(f"**Piyasa Değeri:** {info.get('marketCap', 0)/1e9:.2f} Milyar")
    c3.write(f"**F/K Oranı:** {info.get('trailingPE', 'N/A')}")

    # İş Özeti (Türkçe Analizli)
    st.markdown("##### 📝 Şirket Hakkında (AI Analiz)")
    aciklama = info.get('longBusinessSummary', 'Açıklama bulunamadı.')
    st.markdown(f"<div class='info-box'><b>Özet:</b> Bu varlık {info.get('industry', 'sektöründe')} faaliyetlerini sürdürmektedir.<br><br><i>{aciklama[:700]}...</i></div>", unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)
else:
    st.error("Veri çekilemedi. Lütfen sembolü (Örn: THYAO.IS) kontrol edin.")
