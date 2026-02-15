import streamlit as st
import yfinance as yf
import os

# --- 1. DOSYA TABANLI KALICI KAYIT SİSTEMİ ---
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
st.set_page_config(page_title="Vision AI | Permanent Terminal", layout="wide")
st.markdown("""
    <style>
    header {visibility: hidden !important;}
    [data-testid="stSidebar"] {display: none !important;}
    html, body, [class*="st-"] { font-family: 'Inter', sans-serif; background-color: #f8fafc; font-size: 13px; }
    .terminal-card { background: white; border-radius: 10px; padding: 15px; border: 1px solid #e2e8f0; margin-bottom: 10px; }
    .v-row { display: flex; justify-content: space-between; padding: 4px 0; border-bottom: 1px dashed #f1f5f9; }
    .recommendation-bar { padding: 8px; border-radius: 6px; text-align: center; font-weight: 800; font-size: 1.1rem; margin: 10px 0; color: white; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. ARAYÜZ ---
st.markdown("<h4 style='margin:0;'>💠 Vision AI | Kalıcı Portföy Terminali</h4>", unsafe_allow_html=True)
st.markdown("---")

# Kontroller (Seç, Ekle, Sil)
c1, c2, c3, c4 = st.columns([2, 1.5, 0.5, 4.3])
with c1:
    selected = st.selectbox("Hisselerim", st.session_state.portfolio, label_visibility="collapsed")
with c2:
    new_h = st.text_input("Ekle", placeholder="+ Sembol", label_visibility="collapsed")
    if new_h:
        sym = new_h.upper().strip()
        if sym not in st.session_state.portfolio:
            st.session_state.portfolio.append(sym)
            save_portfolio(st.session_state.portfolio) # Dosyaya yaz
            st.rerun()
with c3:
    if st.button("🗑️") and len(st.session_state.portfolio) > 1:
        st.session_state.portfolio.remove(selected)
        save_portfolio(st.session_state.portfolio) # Dosyadan sil
        st.rerun()

# --- 4. DERİN ANALİZ & ÖNERİ MOTORU ---
try:
    tick = yf.Ticker(selected)
    h_data = tick.history(period="1y")
    
    if not h_data.empty:
        last = h_data['Close'].iloc[-1]
        change_5d = ((last / h_data['Close'].iloc[-5]) - 1) * 100
        
        # Karar Mekanizması
        sma20 = h_data['Close'].rolling(20).mean().iloc[-1]
        if last > sma20: karar, renk = "GÜÇLÜ AL / TREND YUKARI", "#10b981"
        else: karar, renk = "ZAYIF / İZLEMEDE", "#ef4444"

        st.markdown(f"<div class='recommendation-bar' style='background:{renk}'>{selected}: {karar}</div>", unsafe_allow_html=True)
        
        st.markdown("<div class='terminal-card'>", unsafe_allow_html=True)
        g1, g2, g3 = st.columns(3)
        with g1:
            st.markdown(f"<div class='v-row'><span class='v-label'>Fiyat</span><span class='v-value'>{last:,.2f}</span></div>", unsafe_allow_html=True)
        with g2:
            st.markdown(f"<div class='v-row'><span class='v-label'>5G Değişim</span><span class='v-value'>%{change_5d:+.2f}</span></div>", unsafe_allow_html=True)
        with g3:
            try:
                mcap = f"{tick.info.get('marketCap', 0)/1e9:.1f}B"
            except: mcap = "N/A"
            st.markdown(f"<div class='v-row'><span class='v-label'>Piyasa Değeri</span><span class='v-value'>{mcap}</span></div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
except:
    st.error("Veri güncelleniyor...")
