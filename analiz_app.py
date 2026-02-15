import streamlit as st
import yfinance as yf
import pandas as pd

# --- 1. COMPACT TEMA ---
st.set_page_config(page_title="Vision AI | BIST Radar", layout="wide")

st.markdown("""
    <style>
    header {visibility: hidden !important;}
    [data-testid="stSidebar"] {display: none !important;}
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');
    
    html, body, [class*="st-"] { font-family: 'Inter', sans-serif; background-color: #f8fafc; font-size: 14px; }
    
    .terminal-card { background: white; border-radius: 12px; padding: 18px; border: 1px solid #e2e8f0; margin-bottom: 15px; }
    .v-row { display: flex; justify-content: space-between; padding: 5px 0; border-bottom: 1px dashed #f1f5f9; }
    
    /* BIST Fırsat Kartları */
    .bist-recom-grid { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 10px; margin-bottom: 15px; }
    .bist-item { 
        background: linear-gradient(135deg, #ffffff, #f0f9ff); 
        border: 1px solid #bae6fd; border-radius: 10px; padding: 12px; 
        text-align: center; border-bottom: 3px solid #0369a1;
    }
    .bist-symbol { font-weight: 800; color: #0369a1; font-size: 1.1rem; }
    .bist-signal { font-size: 0.7rem; font-weight: 700; color: #10b981; text-transform: uppercase; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. VERİ YÖNETİMİ ---
if 'portfolio' not in st.session_state:
    st.session_state.portfolio = ["THYAO.IS", "EREGL.IS", "SISE.IS", "BTC-USD"]

# --- 3. BIST GENEL TARAYICI (MARKET SCANNER) ---
@st.cache_data(ttl=900) # 15 dakikada bir güncellenir
def scan_bist_market():
    # Tarama yapılacak aday liste (BIST 30 ve hacimli kağıtlar)
    candidates = [
        "AKBNK.IS", "ARCLK.IS", "ASELS.IS", "BIMAS.IS", "EKGYO.IS", 
        "ENKAI.IS", "EREGL.IS", "FROTO.IS", "GARAN.IS", "GUBRF.IS", 
        "HALKB.IS", "HETSH.IS", "ISCTR.IS", "KCHOL.IS", "KOZAL.IS", 
        "KARDM.IS", "PETKM.IS", "PGSUS.IS", "SAHOL.IS", "SASA.IS", 
        "SISE.IS", "TAVHL.IS", "THYAO.IS", "TOASO.IS", "TUPRS.IS", 
        "YKBNK.IS", "DOHOL.IS", "KONTR.IS", "SMRTG.IS", "ODAS.IS"
    ]
    
    results = []
    for symbol in candidates:
        try:
            t = yf.Ticker(symbol)
            df = t.history(period="1mo")
            if len(df) < 15: continue
            
            # Teknik Metrikler
            last_p = df['Close'].iloc[-1]
            prev_p = df['Close'].iloc[-2]
            change = (last_p / prev_p - 1) * 100
            
            # RSI Hesaplama
            delta = df['Close'].diff()
            gain = (delta.where(delta > 0, 0)).tail(14).mean()
            loss = (-delta.where(delta < 0, 0)).tail(14).mean()
            rsi = 100 - (100 / (1 + (gain / loss)))
            
            # Hacim Kontrolü
            vol_ratio = df['Volume'].iloc[-1] / df['Volume'].tail(10).mean()
            
            # SİNYAL PUANLAMA
            score = 0
            signal_desc = ""
            
            if rsi < 35: score += 4; signal_desc = "Aşırı Satım / Dönüş"
            elif rsi > 50 and last_p > df['Close'].rolling(20).mean().iloc[-1]: score += 3; signal_desc = "Trend Başlangıcı"
            
            if vol_ratio > 1.5: score += 2; signal_desc += " + Hacim Onayı"
            
            if score >= 3:
                results.append({"symbol": symbol, "score": score, "desc": signal_desc, "change": change})
        except: continue
        
    return sorted(results, key=lambda x: x['score'], reverse=True)[:3]

bist_opportunities = scan_bist_market()

# --- 4. ARAYÜZ ---
st.markdown("<h3 style='margin:0 0 10px 0;'>💠 Vision AI <span style='font-weight:100;'>Market Scanner</span></h3>", unsafe_allow_html=True)

# Üst Bölüm: BIST Fırsatları
st.markdown("<p style='font-size:0.85rem; color:#64748b; margin-bottom:5px;'>📊 <b>BIST Genel Tarama:</b> Bugünün Kısa Vadeli Alım Sinyalleri</p>", unsafe_allow_html=True)
b_cols = st.columns(3)
for idx, opp in enumerate(bist_opportunities):
    with b_cols[idx]:
        st.markdown(f"""
            <div class="bist-item">
                <div class="bist-symbol">{opp['symbol'].replace('.IS', '')}</div>
                <div class="bist-signal">{opp['desc']}</div>
                <div style="color:{'#10b981' if opp['change'] > 0 else '#ef4444'}; font-size:0.8rem; font-weight:bold;">
                    {opp['change']:+.2f}%
                </div>
            </div>
        """, unsafe_allow_html=True)

# Alt Bölüm: Portföy ve Detay (Aynı Kompakt Yapı)
st.markdown("---")
c1, c2, c3, c4 = st.columns([2, 1.5, 0.7, 3.8])
with c1:
    selected = st.selectbox("İzlemedekiler", st.session_state.portfolio, label_visibility="collapsed")
with c2:
    new_h = st.text_input("Hisse Ekle", placeholder="+ Sembol", label_visibility="collapsed")
    if new_h:
        if new_h.upper() not in st.session_state.portfolio:
            st.session_state.portfolio.append(new_h.upper()); st.rerun()
with c3:
    if st.button("🗑️") and len(st.session_state.portfolio) > 1:
        st.session_state.portfolio.remove(selected); st.rerun()

# Detay Kartı
info_tick = yf.Ticker(selected)
info = info_tick.info
hist_data = info_tick.history(period="5d")

if not hist_data.empty:
    last_p = hist_data['Close'].iloc[-1]
    st.markdown("<div class='terminal-card'>", unsafe_allow_html=True)
    st.markdown(f"**{info.get('longName', selected)}** | <small>{info.get('sector', 'N/A')}</small>", unsafe_allow_html=True)
    
    g1, g2, g3 = st.columns(3)
    with g1:
        st.markdown(f"<div class='v-row'><span class='v-label'>Fiyat</span><span class='v-value'>{last_p:,.2f}</span></div>", unsafe_allow_html=True)
        st.markdown(f"<div class='v-row'><span class='v-label'>F/K</span><span class='v-value'>{info.get('trailingPE', 'N/A')}</span></div>", unsafe_allow_html=True)
    with g2:
        st.markdown(f"<div class='v-row'><span class='v-label'>Zirve</span><span class='v-value'>{info.get('fiftyTwoWeekHigh', 0):,.1f}</span></div>", unsafe_allow_html=True)
        st.markdown(f"<div class='v-row'><span class='v-label'>Beta</span><span class='v-value'>{info.get('beta', 'N/A')}</span></div>", unsafe_allow_html=True)
    with g3:
        st.markdown(f"<div class='v-row'><span class='v-label'>Hacim</span><span class='v-value'>{info.get('volume', 0)/1e6:.1f}M</span></div>", unsafe_allow_html=True)
        st.markdown(f"<div class='v-row'><span class='v-label'>Piyasa D.</span><span class='v-value'>{info.get('marketCap', 0)/1e9:.1f}B</span></div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)
