import streamlit as st
import yfinance as yf
import pandas as pd
import time

# --- 1. COMPACT TEMA ---
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

# --- 2. PORTFÖY YÖNETİMİ ---
if 'portfolio' not in st.session_state:
    st.session_state.portfolio = ["THYAO.IS", "EREGL.IS", "SISE.IS", "BTC-USD"]

# --- 3. BIST GENEL TARAYICI (GÜVENLİ MOD) ---
@st.cache_data(ttl=1200)
def scan_bist_market():
    # Liste limitlere takılmamak için biraz daraltıldı
    candidates = ["AKBNK.IS", "ASELS.IS", "BIMAS.IS", "EREGL.IS", "FROTO.IS", "GARAN.IS", 
                  "ISCTR.IS", "KCHOL.IS", "KOZAL.IS", "PGSUS.IS", "SAHOL.IS", "THYAO.IS", "TUPRS.IS"]
    results = []
    for symbol in candidates:
        try:
            t = yf.Ticker(symbol)
            df = t.history(period="1mo", interval="1d")
            if len(df) < 10: continue
            
            last_p = df['Close'].iloc[-1]
            change = ((last_p / df['Close'].iloc[-2]) - 1) * 100
            
            # Basit RSI ve Hacim analizi
            delta = df['Close'].diff()
            gain = (delta.where(delta > 0, 0)).tail(14).mean()
            loss = (-delta.where(delta < 0, 0)).tail(14).mean()
            rsi = 100 - (100 / (1 + (gain / loss)))
            
            if rsi < 40: sig = "DİP DÖNÜŞÜ"
            elif last_p > df['Close'].rolling(20).mean().iloc[-1]: sig = "TREND YUKARI"
            else: continue

            results.append({"symbol": symbol, "sig": sig, "chg": change})
        except: continue
    return results[:3]

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
                    <div class="bist-symbol">{opp['symbol'].replace('.IS', '')}</div>
                    <div style="font-size:0.7rem; font-weight:700; color:#10b981;">{opp['sig']}</div>
                    <div style="color:{'#10b981' if opp['chg'] > 0 else '#ef4444'}; font-size:0.8rem;">%{opp['chg']:+.2f}</div>
                </div>
            """, unsafe_allow_html=True)
except:
    st.info("Market tarayıcı şu an dinleniyor (Rate Limit)...")

st.markdown("---")

# Portföy Kontrolleri
c1, c2, c3, c4 = st.columns([2, 1.5, 0.5, 4])
with c1:
    selected = st.selectbox("Hisse", st.session_state.portfolio, label_visibility="collapsed")
with c2:
    new_h = st.text_input("Ekle", placeholder="+ Sembol", label_visibility="collapsed")
    if new_h:
        if new_h.upper() not in st.session_state.portfolio:
            st.session_state.portfolio.append(new_h.upper()); st.rerun()
with c3:
    if st.button("🗑️"):
        st.session_state.portfolio.remove(selected); st.rerun()

# Detay Kartı (Hata Korumalı)
try:
    tick = yf.Ticker(selected)
    h_data = tick.history(period="5d")
    
    # info verisini çekemezsek hata vermemesi için koruma
    try:
        inf = tick.info
        name = inf.get('longName', selected)
        mcap = f"{inf.get('marketCap', 0)/1e9:.1f}B"
    except:
        name = selected
        mcap = "N/A"

    if not h_data.empty:
        last = h_data['Close'].iloc[-1]
        st.markdown("<div class='terminal-card'>", unsafe_allow_html=True)
        st.markdown(f"**{name}**", unsafe_allow_html=True)
        
        g1, g2, g3 = st.columns(3)
        with g1:
            st.markdown(f"<div class='v-row'><span class='v-label'>Fiyat</span><span class='v-value'>{last:,.2f}</span></div>", unsafe_allow_html=True)
        with g2:
            st.markdown(f"<div class='v-row'><span class='v-label'>Piyasa D.</span><span class='v-value'>{mcap}</span></div>", unsafe_allow_html=True)
        with g3:
            change_5d = ((last / h_data['Close'].iloc[0]) - 1) * 100
            st.markdown(f"<div class='v-row'><span class='v-label'>5G Değişim</span><span class='v-value'>%{change_5d:+.2f}</span></div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
except Exception as e:
    st.error("Yahoo Finance geçici olarak veri gönderimini durdurdu. Lütfen 1-2 dakika bekleyip sayfayı yenileyin.")
