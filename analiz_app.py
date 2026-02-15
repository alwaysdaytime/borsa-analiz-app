import streamlit as st
import yfinance as yf
import pandas as pd

# --- 1. AYARLAR & TEMA ---
st.set_page_config(page_title="Vision AI | BIST Terminal", layout="wide")

st.markdown("""
    <style>
    header {visibility: hidden !important;}
    [data-testid="stSidebar"] {display: none !important;}
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');
    html, body, [class*="st-"] { font-family: 'Inter', sans-serif; background-color: #f8fafc; font-size: 13px; }
    .terminal-card { background: white; border-radius: 10px; padding: 15px; border: 1px solid #e2e8f0; margin-bottom: 10px; }
    .v-row { display: flex; justify-content: space-between; padding: 4px 0; border-bottom: 1px dashed #f1f5f9; }
    .bist-item { 
        background: #ffffff; border: 1px solid #e2e8f0; border-radius: 8px; padding: 10px; 
        text-align: center; border-bottom: 3px solid #3b82f6;
    }
    .bist-symbol { font-weight: 800; color: #1e3a8a; font-size: 1rem; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. HİSSE KAYIT SİSTEMİ (Oturum Boyunca Kalıcı) ---
if 'portfolio' not in st.session_state:
    # İlk açılışta varsayılan liste
    st.session_state.portfolio = ["THYAO.IS", "EREGL.IS", "SISE.IS", "BTC-USD"]

# --- 3. BIST MARKET SCANNER (Hata Korumalı) ---
@st.cache_data(ttl=1200)
def scan_bist_market():
    candidates = ["AKBNK.IS", "ASELS.IS", "BIMAS.IS", "EREGL.IS", "FROTO.IS", "GARAN.IS", 
                  "ISCTR.IS", "KCHOL.IS", "KOZAL.IS", "PGSUS.IS", "SAHOL.IS", "THYAO.IS"]
    results = []
    for symbol in candidates:
        try:
            t = yf.Ticker(symbol)
            df = t.history(period="1mo")
            if len(df) < 5: continue
            last_p = df['Close'].iloc[-1]
            change = ((last_p / df['Close'].iloc[-2]) - 1) * 100
            
            # Basit RSI hesaplama
            delta = df['Close'].diff()
            gain = (delta.where(delta > 0, 0)).tail(14).mean()
            loss = (-delta.where(delta < 0, 0)).tail(14).mean()
            rsi = 100 - (100 / (1 + (gain / loss)))
            
            sig = "TREND YUKARI" if last_p > df['Close'].rolling(20).mean().iloc[-1] else "İZLEMEDE"
            if rsi < 35: sig = "AŞIRI UCUZ"
            
            results.append({"symbol": symbol, "sig": sig, "chg": change, "score": rsi})
        except: continue
    return sorted(results, key=lambda x: x['score'])[:3]

# --- 4. ARAYÜZ YERLEŞİMİ ---
st.markdown("<h4 style='margin:0;'>💠 Vision AI Market Scanner</h4>", unsafe_allow_html=True)

# Üst Sinyaller
try:
    bist_opps = scan_bist_market()
    b_cols = st.columns(3)
    for idx, opp in enumerate(bist_opps):
        with b_cols[idx]:
            st.markdown(f"""
                <div class="bist-item">
                    <div class="bist-symbol">{opp['symbol'].replace('.IS', '')}</div>
                    <div style="font-size:0.7rem; font-weight:700; color:#10b981;">{opp['sig']}</div>
                    <div style="color:{'#10b981' if opp['chg'] > 0 else '#ef4444'}; font-size:0.8rem;">%{opp['chg']:+.2f}</div>
                </div>
            """, unsafe_allow_html=True)
except:
    st.info("Market tarayıcı şu an dinleniyor...")

st.markdown("---")

# Portföy Yönetimi (Kayıt ve Silme)
c1, c2, c3, c4 = st.columns([2, 1.5, 0.5, 4])
with c1:
    selected = st.selectbox("Hisse Kayıtlarım", st.session_state.portfolio, label_visibility="collapsed")
with c2:
    new_h = st.text_input("Hisse Ekle", placeholder="+ Sembol (Örn: SASA.IS)", label_visibility="collapsed")
    if new_h:
        sym = new_h.upper().strip()
        if sym not in st.session_state.portfolio:
            st.session_state.portfolio.append(sym)
            st.rerun()
with c3:
    if st.button("🗑️"):
        if len(st.session_state.portfolio) > 1:
            st.session_state.portfolio.remove(selected)
            st.rerun()

# Detay Analiz (Hata Korumalı)
try:
    tick = yf.Ticker(selected)
    h_data = tick.history(period="5d")
    
    # Bilgi çekme (Rate Limit Koruması)
    try:
        inf = tick.info
        name = inf.get('longName', selected)
        mcap = f"{inf.get('marketCap', 0)/1e9:.1f}B"
        sector = inf.get('sector', 'N/A')
    except:
        name = selected
        mcap = "N/A"
        sector = "N/A"

    if not h_data.empty:
        last = h_data['Close'].iloc[-1]
        st.markdown("<div class='terminal-card'>", unsafe_allow_html=True)
        st.markdown(f"**{name}** | <small>{sector}</small>", unsafe_allow_html=True)
        
        g1, g2, g3 = st.columns(3)
        with g1:
            st.markdown(f"<div class='v-row'><span class='v-label'>Fiyat</span><span class='v-value'>{last:,.2f}</span></div>", unsafe_allow_html=True)
        with g2:
            st.markdown(f"<div class='v-row'><span class='v-label'>Piyasa D.</span><span class='v-value'>{mcap}</span></div>", unsafe_allow_html=True)
        with g3:
            change_5d = ((last / h_data['Close'].iloc[0]) - 1) * 100
            st.markdown(f"<div class='v-row'><span class='v-label'>5G Performans</span><span class='v-value'>%{change_5d:+.2f}</span></div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
except:
    st.error("Veri bağlantısı kurulamadı. Lütfen bekleyin.")
