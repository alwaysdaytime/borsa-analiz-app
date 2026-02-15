import streamlit as st
import yfinance as yf
import os

# --- 1. KALICI KAYIT SİSTEMİ ---
DB_FILE = "portfolio.txt"

def load_portfolio():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r") as f:
            return [line.strip() for line in f.readlines() if line.strip()]
    return ["THYAO.IS", "EREGL.IS", "SISE.IS", "BTC-USD"]

def save_portfolio(portfolio):
    with open(DB_FILE, "w") as f:
        for stock in portfolio:
            f.write(f"{stock}\n")

if 'portfolio' not in st.session_state:
    st.session_state.portfolio = load_portfolio()

# --- 2. AYARLAR & TEMA ---
st.set_page_config(page_title="Vision AI | Live Terminal", layout="wide")
st.markdown("""
    <style>
    header {visibility: hidden !important;}
    [data-testid="stSidebar"] {display: none !important;}
    html, body, [class*="st-"] { font-family: 'Inter', sans-serif; background-color: #f8fafc; font-size: 13px; }
    .terminal-card { background: white; border-radius: 10px; padding: 15px; border: 1px solid #e2e8f0; margin-bottom: 10px; }
    .v-row { display: flex; justify-content: space-between; padding: 4px 0; border-bottom: 1px dashed #f1f5f9; }
    .bist-item { background: #ffffff; border: 1px solid #e2e8f0; border-radius: 8px; padding: 10px; text-align: center; border-bottom: 3px solid #3b82f6; }
    .recommendation-bar { padding: 8px; border-radius: 6px; text-align: center; font-weight: 800; font-size: 1.1rem; margin: 10px 0; color: white; }
    
    /* Anlık Veri Paneli Stili */
    .live-data-box { 
        background: #1e293b; color: #38bdf8; border-radius: 8px; padding: 12px; 
        margin-top: 15px; display: flex; justify-content: space-around; 
        font-family: 'JetBrains Mono', monospace; border-left: 5px solid #38bdf8;
    }
    .live-item { text-align: center; }
    .live-label { font-size: 0.7rem; color: #94a3b8; display: block; margin-bottom: 2px; }
    .live-val { font-size: 0.95rem; font-weight: 700; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. BIST GENEL AI TARAYICI ---
@st.cache_data(ttl=900)
def scan_bist_market():
    candidates = ["AKBNK.IS", "ASELS.IS", "BIMAS.IS", "EREGL.IS", "GARAN.IS", "ISCTR.IS", "KCHOL.IS", "THYAO.IS", "TUPRS.IS"]
    results = []
    for symbol in candidates:
        try:
            t = yf.Ticker(symbol); df = t.history(period="1mo")
            last_p = df['Close'].iloc[-1]; change = ((last_p / df['Close'].iloc[-2]) - 1) * 100
            if change > 0.5: results.append({"symbol": symbol, "chg": change})
        except: continue
    return sorted(results, key=lambda x: x['chg'], reverse=True)[:3]

# --- 4. ARAYÜZ ---
st.markdown("<h4 style='margin:0;'>🚀 AI Market Opportunities (BIST)</h4>", unsafe_allow_html=True)

try:
    bist_opps = scan_bist_market()
    b_cols = st.columns(3)
    for idx, opp in enumerate(bist_opps):
        with b_cols[idx]:
            st.markdown(f'<div class="bist-item"><div style="font-weight:800; color:#1e3a8a;">{opp["symbol"].replace(".IS", "")}</div><div style="color:#10b981; font-size:0.8rem;">%{opp["chg"]:+.2f}</div></div>', unsafe_allow_html=True)
except: st.info("Tarayıcı güncelleniyor...")

st.markdown("---")

# Portföy Kontrolleri
c1, c2, c3, c4 = st.columns([2, 1.5, 0.5, 4.3])
with c1:
    selected = st.selectbox("Kayıtlı Portföyüm", st.session_state.portfolio, label_visibility="collapsed")
with c2:
    new_h = st.text_input("Ekle", placeholder="+ Sembol", label_visibility="collapsed")
    if new_h:
        sym = new_h.upper().strip()
        if sym not in st.session_state.portfolio:
            st.session_state.portfolio.append(sym); save_portfolio(st.session_state.portfolio); st.rerun()
with c3:
    if st.button("🗑️") and len(st.session_state.portfolio) > 1:
        st.session_state.portfolio.remove(selected); save_portfolio(st.session_state.portfolio); st.rerun()

# --- 5. DERİN ANALİZ & ANLIK VERİ PANELİ ---
try:
    tick = yf.Ticker(selected)
    h_data = tick.history(period="1y")
    live_data = tick.history(period="1d") # Günlük anlık veri
    
    if not h_data.empty:
        last = h_data['Close'].iloc[-1]
        sma20 = h_data['Close'].rolling(20).mean().iloc[-1]
        karar, renk = ("BOĞA / AL", "#10b981") if last > sma20 else ("AYI / SAT", "#ef4444")

        st.markdown(f"<div class='recommendation-bar' style='background:{renk}'>{selected}: {karar}</div>", unsafe_allow_html=True)
        
        # Üst Veri Kartı
        st.markdown("<div class='terminal-card'>", unsafe_allow_html=True)
        g1, g2, g3 = st.columns(3)
        with g1: st.markdown(f"<div class='v-row'><span class='v-label'>Fiyat</span><span class='v-value'>{last:,.2f}</span></div>", unsafe_allow_html=True)
        with g2: st.markdown(f"<div class='v-row'><span class='v-label'>5G Değişim</span><span class='v-value'>%{((last/h_data['Close'].iloc[-5])-1)*100:+.2f}</span></div>", unsafe_allow_html=True)
        with g3: 
            try: mcap = f"{tick.info.get('marketCap', 0)/1e9:.1f}B"
            except: mcap = "N/A"
            st.markdown(f"<div class='v-row'><span class='v-label'>Piyasa D.</span><span class='v-value'>{mcap}</span></div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

        # --- YENİ: ANLIK VERİ PANELİ (ALT TARAF) ---
        if not live_data.empty:
            st.markdown(f"""
                <div class="live-data-box">
                    <div class="live-item"><span class="live-label">GÜNÜN EN DÜŞÜK</span><span class="live-val">{live_data['Low'].iloc[-1]:,.2f}</span></div>
                    <div class="live-item"><span class="live-label">GÜNÜN EN YÜKSEK</span><span class="live-val">{live_data['High'].iloc[-1]:,.2f}</span></div>
                    <div class="live-item"><span class="live-label">AÇILIŞ</span><span class="live-val">{live_data['Open'].iloc[-1]:,.2f}</span></div>
                    <div class="live-item"><span class="live-label">HACİM</span><span class="live-val">{live_data['Volume'].iloc[-1]:,.0f}</span></div>
                </div>
            """, unsafe_allow_html=True)

except: st.error("Canlı veri bağlantısı bekleniyor...")
