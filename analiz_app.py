import streamlit as st
import yfinance as yf
import os

# --- 1. KALICI KAYIT SİSTEMİ ---
DB_FILE = "portfolio.txt"

def load_portfolio():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r") as f:
            lines = f.readlines()
            return [line.strip() for line in lines if line.strip()]
    return ["THYAO.IS", "EREGL.IS", "SISE.IS", "BTC-USD"]

def save_portfolio(portfolio):
    with open(DB_FILE, "w") as f:
        for stock in portfolio:
            f.write(f"{stock}\n")

if 'portfolio' not in st.session_state:
    st.session_state.portfolio = load_portfolio()

# --- 2. AYARLAR & TEMA ---
st.set_page_config(page_title="Vision AI | Pro Terminal", layout="wide")
st.markdown("""
    <style>
    header {visibility: hidden !important;}
    [data-testid="stSidebar"] {display: none !important;}
    html, body, [class*="st-"] { font-family: 'Inter', sans-serif; background-color: #f8fafc; font-size: 13px; }
    .terminal-card { background: white; border-radius: 10px; padding: 15px; border: 1px solid #e2e8f0; margin-bottom: 10px; }
    .v-row { display: flex; justify-content: space-between; padding: 4px 0; border-bottom: 1px dashed #f1f5f9; }
    .bist-item { background: #ffffff; border: 1px solid #e2e8f0; border-radius: 8px; padding: 10px; text-align: center; border-bottom: 3px solid #3b82f6; }
    .recommendation-bar { padding: 8px; border-radius: 6px; text-align: center; font-weight: 800; font-size: 1.1rem; margin: 10px 0; color: white; }
    .live-data-box { 
        background: #0f172a; color: #f8fafc; border-radius: 8px; padding: 15px; 
        margin-top: 10px; display: grid; grid-template-columns: repeat(4, 1fr); gap: 15px;
        font-family: 'JetBrains Mono', monospace;
    }
    .live-item { border-right: 1px solid #334155; padding: 0 5px; }
    .live-item:last-child { border-right: none; }
    .live-label { font-size: 0.65rem; color: #94a3b8; display: block; text-transform: uppercase; }
    .live-val { font-size: 0.9rem; font-weight: 700; color: #38bdf8; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. BIST GENEL AI TARAYICI ---
@st.cache_data(ttl=600)
def scan_bist_market():
    results = []
    candidates = ["THYAO.IS", "EREGL.IS", "ASELS.IS", "TUPRS.IS", "GARAN.IS"]
    for symbol in candidates:
        try:
            t = yf.Ticker(symbol)
            df = t.history(period="2d")
            if len(df) > 1:
                chg = ((df['Close'].iloc[-1] / df['Close'].iloc[-2]) - 1) * 100
                results.append({"symbol": symbol, "chg": chg})
        except: continue
    return sorted(results, key=lambda x: x['chg'], reverse=True)[:3]

# --- 4. ARAYÜZ ---
st.markdown("<h4 style='margin:0;'>🚀 AI Market Opportunities (BIST)</h4>", unsafe_allow_html=True)

opps = scan_bist_market()
if opps:
    b_cols = st.columns(3)
    for idx, opp in enumerate(opps):
        with b_cols[idx]:
            st.markdown(f'<div class="bist-item"><div style="font-weight:800; color:#1e3a8a;">{opp["symbol"].replace(".IS", "")}</div><div style="color:#10b981; font-size:0.8rem;">%{opp["chg"]:+.2f}</div></div>', unsafe_allow_html=True)

st.markdown("---")

# Kontroller
c1, c2, c3, c4 = st.columns([2, 1.5, 0.5, 4.3])
with c1:
    selected = st.selectbox("Portföyüm", st.session_state.portfolio, label_visibility="collapsed")
with c2:
    new_h = st.text_input("Ekle", placeholder="+ Sembol", label_visibility="collapsed")
    if new_h:
        sym = new_h.upper().strip()
        if not sym.endswith(".IS") and "-" not in sym: sym += ".IS"
        if sym not in st.session_state.portfolio:
            st.session_state.portfolio.append(sym)
            save_portfolio(st.session_state.portfolio)
            st.rerun()
with c3:
    if st.button("🗑️") and len(st.session_state.portfolio) > 1:
        st.session_state.portfolio.remove(selected)
        save_portfolio(st.session_state.portfolio)
        st.rerun()

# --- 5. DERİN ANALİZ (GELİŞTİRİLMİŞ HATA YÖNETİMİ) ---
try:
    tick = yf.Ticker(selected)
    # Veri çekme denemesi (period="1y" bazen hata verebilir, period="max" veya "2y" daha stabildir)
    h_data = tick.history(period="2y")
    
    if h_data.empty:
        # Alternatif deneme
        h_data = tick.history(period="1mo")

    if not h_data.empty:
        last = h_data['Close'].iloc[-1]
        prev_close = h_data['Close'].iloc[-2] if len(h_data) > 1 else last
        low_52 = h_data['Close'].tail(252).min()
        high_52 = h_data['Close'].tail(252).max()
        
        tavan, taban = prev_close * 1.10, prev_close * 0.90
        sma20 = h_data['Close'].rolling(20).mean().iloc[-1]
        karar, renk = ("BOĞA / AL", "#10b981") if last > sma20 else ("AYI / SAT", "#ef4444")

        st.markdown(f"<div class='recommendation-bar' style='background:{renk}'>{selected}: {karar}</div>", unsafe_allow_html=True)
        
        # ANA ANALİZ KARTI
        st.markdown("<div class='terminal-card'>", unsafe_allow_html=True)
        g1, g2, g3 = st.columns(3)
        with g1:
            st.markdown(f"<div class='v-row'><span class='v-label'>Fiyat</span><span class='v-value'>{last:,.2f}</span></div>")
            st.markdown(f"<div class='v-row'><span class='v-label'>Önc. Kapanış</span><span class='v-value'>{prev_close:,.2f}</span></div>")
        with g2:
            st.markdown(f"<div class='v-row'><span class='v-label'>12A En Düşük</span><span class='v-value'>{low_52:,.2f}</span></div>")
            st.markdown(f"<div class='v-row'><span class='v-label'>12A En Yüksek</span><span class='v-value'>{high_52:,.2f}</span></div>")
        with g3:
            try:
                inf = tick.info
                pe = inf.get('trailingPE', 'N/A')
                mcap = f"{inf.get('marketCap', 0)/1e9:.1f}B"
            except: pe, mcap = "N/A", "N/A"
            st.markdown(f"<div class='v-row'><span class='v-label'>F/K Oranı</span><span class='v-value'>{pe}</span></div>")
            st.markdown(f"<div class='v-row'><span class='v-label'>Piyasa Değeri</span><span class='v-value'>{mcap}</span></div>")
        st.markdown("</div>", unsafe_allow_html=True)

        # ALT PANEL
        st.markdown(f"""
            <div class="live-data-box">
                <div class="live-item"><span class="live-label">Tavan</span><span class="live-val" style="color:#4ade80;">{tavan:,.2f}</span></div>
                <div class="live-item"><span class="live-label">Taban</span><span class="live-val" style="color:#f87171;">{taban:,.2f}</span></div>
                <div class="live-item"><span class="live-label">Hacim</span><span class="live-val">{h_data['Volume'].iloc[-1]:,.0f}</span></div>
                <div class="live-item"><span class="live-label">20G Ort.</span><span class="live-val">{sma20:,.2f}</span></div>
            </div>
        """, unsafe_allow_html=True)
    else:
        st.warning(f"{selected} için veri şu an çekilemiyor. Yahoo limitlerine takılmış olabilirsiniz.")
except Exception as e:
    st.error(f"Sistem Hatası: {e}")
