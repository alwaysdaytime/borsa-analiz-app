import streamlit as st
import yfinance as yf
import pandas as pd

# --- 1. AYARLAR & TEMA ---
st.set_page_config(page_title="Vision AI | Pro Terminal", layout="wide")

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
    .recommendation-bar {
        padding: 8px; border-radius: 6px; text-align: center; font-weight: 800; 
        font-size: 1.1rem; margin: 10px 0; color: white;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. HİSSE KAYIT SİSTEMİ ---
if 'portfolio' not in st.session_state:
    st.session_state.portfolio = ["THYAO.IS", "EREGL.IS", "SISE.IS", "BTC-USD"]

# --- 3. MARKET SCANNER ---
@st.cache_data(ttl=1200)
def scan_bist_market():
    candidates = ["AKBNK.IS", "ASELS.IS", "BIMAS.IS", "EREGL.IS", "GARAN.IS", "ISCTR.IS", "KCHOL.IS", "THYAO.IS", "TUPRS.IS"]
    results = []
    for symbol in candidates:
        try:
            t = yf.Ticker(symbol); df = t.history(period="1mo")
            if len(df) < 5: continue
            last_p = df['Close'].iloc[-1]
            change = ((last_p / df['Close'].iloc[-2]) - 1) * 100
            results.append({"symbol": symbol, "chg": change})
        except: continue
    return sorted(results, key=lambda x: x['chg'], reverse=True)[:3]

# --- 4. ARAYÜZ ---
st.markdown("<h4 style='margin:0;'>💠 Vision AI Market Scanner</h4>", unsafe_allow_html=True)

# Market Sinyalleri
try:
    bist_opps = scan_bist_market()
    b_cols = st.columns(3)
    for idx, opp in enumerate(bist_opps):
        with b_cols[idx]:
            st.markdown(f"""
                <div class="bist-item">
                    <div style="font-weight:800; color:#1e3a8a;">{opp['symbol'].replace('.IS', '')}</div>
                    <div style="color:#10b981; font-size:0.8rem;">GÜNLÜK: %{opp['chg']:+.2f}</div>
                </div>
            """, unsafe_allow_html=True)
except: st.info("Tarayıcı beklemede...")

st.markdown("---")

# Kontroller
c1, c2, c3, c4 = st.columns([2, 1.5, 0.5, 4.3])
with c1:
    selected = st.selectbox("Hisselerim", st.session_state.portfolio, label_visibility="collapsed")
with c2:
    new_h = st.text_input("Ekle", placeholder="+ Sembol", label_visibility="collapsed")
    if new_h:
        sym = new_h.upper().strip()
        if sym not in st.session_state.portfolio:
            st.session_state.portfolio.append(sym); st.rerun()
with c3:
    if st.button("🗑️") and len(st.session_state.portfolio) > 1:
        st.session_state.portfolio.remove(selected); st.rerun()

# --- 5. DETAYLI ANALİZ VE ÖNERİ (GERİ EKLENEN KISIM) ---
try:
    tick = yf.Ticker(selected)
    h_data = tick.history(period="1y")
    
    if not h_data.empty:
        # Teknik Hesaplamalar
        last = h_data['Close'].iloc[-1]
        change_5d = ((last / h_data['Close'].iloc[-5]) - 1) * 100
        
        # RSI (14 Günlük)
        delta = h_data['Close'].diff()
        gain = (delta.where(delta > 0, 0)).tail(14).mean()
        loss = (-delta.where(delta < 0, 0)).tail(14).mean()
        rsi = 100 - (100 / (1 + (gain / loss)))
        
        # Trend (SMA20)
        sma20 = h_data['Close'].rolling(20).mean().iloc[-1]
        
        # Öneri Karar Motoru
        score = 0
        if rsi < 35: score += 3 # Ucuz
        if last > sma20: score += 2 # Trend pozitif
        if change_5d > 0: score += 1 # Momentum var
        
        if score >= 4: karar, renk = "GÜÇLÜ AL", "#10b981"
        elif score >= 2: karar, renk = "KADEMELİ AL / TUT", "#3b82f6"
        elif score <= 0: karar, renk = "GÜÇLÜ SAT / RİSKLİ", "#ef4444"
        else: karar, renk = "İZLE / NÖTR", "#64748b"

        # Görünüm
        st.markdown(f"<div class='recommendation-bar' style='background:{renk}'>{selected} KARAR: {karar}</div>", unsafe_allow_html=True)
        
        st.markdown("<div class='terminal-card'>", unsafe_allow_html=True)
        st.markdown(f"**{selected} Analiz Notları**", unsafe_allow_html=True)
        
        g1, g2, g3 = st.columns(3)
        with g1:
            st.markdown(f"<div class='v-row'><span class='v-label'>Güncel Fiyat</span><span class='v-value'>{last:,.2f}</span></div>", unsafe_allow_html=True)
            st.markdown(f"<div class='v-row'><span class='v-label'>RSI (Momentum)</span><span class='v-value'>{rsi:.1f}</span></div>", unsafe_allow_html=True)
        with g2:
            st.markdown(f"<div class='v-row'><span class='v-label'>Trend (20G)</span><span class='v-value'>{'ÜZERİNDE' if last > sma20 else 'ALTINDA'}</span></div>", unsafe_allow_html=True)
            st.markdown(f"<div class='v-row'><span class='v-label'>5G Değişim</span><span class='v-value'>%{change_5d:+.2f}</span></div>", unsafe_allow_html=True)
        with g3:
            # Info verisi (Limit korumalı)
            try:
                inf = tick.info
                fk = inf.get('trailingPE', 'N/A')
                mcap = f"{inf.get('marketCap', 0)/1e9:.1f}B"
            except: fk, mcap = "N/A", "N/A"
            st.markdown(f"<div class='v-row'><span class='v-label'>F/K Oranı</span><span class='v-value'>{fk}</span></div>", unsafe_allow_html=True)
            st.markdown(f"<div class='v-row'><span class='v-label'>Piyasa D.</span><span class='v-value'>{mcap}</span></div>", unsafe_allow_html=True)
            
        st.markdown("</div>", unsafe_allow_html=True)
except:
    st.error("Veri çekilemedi, lütfen tekrar deneyin.")
