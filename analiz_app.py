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
st.set_page_config(page_title="Vision AI | Smart Terminal", layout="wide")
st.markdown("""
    <style>
    header {visibility: hidden !important;}
    [data-testid="stSidebar"] {display: none !important;}
    html, body, [class*="st-"] { font-family: 'Inter', sans-serif; background-color: #f8fafc; font-size: 13px; }
    .terminal-card { background: white; border-radius: 10px; padding: 15px; border: 1px solid #e2e8f0; margin-bottom: 10px; }
    .v-row { display: flex; justify-content: space-between; padding: 4px 0; border-bottom: 1px dashed #f1f5f9; }
    .bist-item { 
        background: #ffffff; border: 1px solid #e2e8f0; border-radius: 8px; padding: 10px; 
        text-align: center; border-bottom: 3px solid #f59e0b; /* Alt çizgi altın rengi: Fırsat simgesi */
    }
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

# --- 3. AI POTANSİYEL TARAYICI (ARKA PLAN ANALİZİ) ---
@st.cache_data(ttl=900)
def find_opportunity_hisseler():
    results = []
    # Geniş tarama listesi
    candidates = ["THYAO.IS", "EREGL.IS", "ASELS.IS", "TUPRS.IS", "GARAN.IS", 
                  "AKBNK.IS", "SISE.IS", "KCHOL.IS", "SASA.IS", "BIMAS.IS", "FROTO.IS"]
    
    for symbol in candidates:
        try:
            t = yf.Ticker(symbol)
            df = t.history(period="1mo")
            if len(df) < 20: continue
            
            # Teknik Metrikler
            last_p = df['Close'].iloc[-1]
            prev_p = df['Close'].iloc[-2]
            chg = ((last_p / prev_p) - 1) * 100
            sma20 = df['Close'].rolling(20).mean().iloc[-1]
            vol_avg = df['Volume'].tail(5).mean()
            last_vol = df['Volume'].iloc[-1]
            
            # RSI Hesaplama
            delta = df['Close'].diff()
            gain = (delta.where(delta > 0, 0)).tail(14).mean()
            loss = (-delta.where(delta < 0, 0)).tail(14).mean()
            rsi = 100 - (100 / (1 + (gain / (loss + 1e-9))))
            
            # POTANSİYEL PUANI (0-100)
            score = 0
            if last_p > sma20: score += 30 # Trend başı
            if last_vol > vol_avg: score += 40 # Hacim onayı
            if 40 < rsi < 60: score += 30 # Güçlenme bölgesi
            
            if score >= 60: # Sadece yüksek potansiyelli olanlar
                results.append({
                    "symbol": symbol, 
                    "price": last_p, 
                    "chg": chg, 
                    "score": score,
                    "label": "YÜKSELİŞ BEKLENTİSİ" if score > 70 else "TEKNİK TAKİP"
                })
        except: continue
    
    return sorted(results, key=lambda x: x['score'], reverse=True)[:3]

# --- 4. ARAYÜZ ÜST BÖLÜM ---
st.markdown("<h4 style='margin:0;'>⚡ AI Teknik Analiz: Kısa Vadeli Potansiyeller</h4>", unsafe_allow_html=True)

opps = find_opportunity_hisseler()
if opps:
    b_cols = st.columns(3)
    for idx, opp in enumerate(opps):
        with b_cols[idx]:
            st.markdown(f"""
                <div class="bist-item">
                    <div style="font-weight:800; color:#1e3a8a; font-size:0.9rem;">{opp['symbol'].replace('.IS', '')}</div>
                    <div style="font-size:0.7rem; font-weight:700; color:#f59e0b; margin-bottom:2px;">{opp['label']}</div>
                    <div style="font-weight:700; color:#0f172a;">{opp['price']:,.2f} TL</div>
                    <div style="color:#10b981; font-size:0.8rem;">GÜNLÜK: %{opp['chg']:+.2f}</div>
                </div>
            """, unsafe_allow_html=True)
else:
    st.info("Kriterlere uygun kısa vadeli fırsat şu an bulunamadı. Market taranıyor...")

st.markdown("---")

# Portföy Kontrolleri (Kayıt sistemi burada korunuyor)
c1, c2, c3, c4 = st.columns([2, 1.5, 0.5, 4.3])
with c1:
    selected = st.selectbox("Portföyüm", st.session_state.portfolio, label_visibility="collapsed")
with c2:
    new_h = st.text_input("Ekle", placeholder="+ Sembol", label_visibility="collapsed")
    if new_h:
        sym = new_h.upper().strip()
        if not sym.endswith(".IS") and "-" not in sym: sym += ".IS"
        if sym not in st.session_state.portfolio:
            st.session_state.portfolio.append(sym); save_portfolio(st.session_state.portfolio); st.rerun()
with c3:
    if st.button("🗑️") and len(st.session_state.portfolio) > 1:
        st.session_state.portfolio.remove(selected); save_portfolio(st.session_state.portfolio); st.rerun()

# --- 5. SEÇİLİ HİSSE DETAY ANALİZ ---
try:
    tick = yf.Ticker(selected)
    h_data = tick.history(period="1y")
    if not h_data.empty:
        last = h_data['Close'].iloc[-1]
        prev_close = h_data['Close'].iloc[-2]
        low_52, high_52 = h_data['Close'].min(), h_data['Close'].max()
        tavan, taban = prev_close * 1.10, prev_close * 0.90
        sma20 = h_data['Close'].rolling(20).mean().iloc[-1]
        karar, renk = ("BOĞA / AL", "#10b981") if last > sma20 else ("AYI / SAT", "#ef4444")

        st.markdown(f"<div class='recommendation-bar' style='background:{renk}'>{selected}: {karar}</div>", unsafe_allow_html=True)
        
        # ANA ANALİZ KARTI
        st.markdown("<div class='terminal-card'>", unsafe_allow_html=True)
        g1, g2, g3 = st.columns(3)
        with g1:
            st.markdown(f"<div class='v-row'><span>Fiyat</span><b>{last:,.2f}</b></div>", unsafe_allow_html=True)
            st.markdown(f"<div class='v-row'><span>Önc. Kapanış</span><b>{prev_close:,.2f}</b></div>", unsafe_allow_html=True)
        with g2:
            st.markdown(f"<div class='v-row'><span>12A En Düşük</span><b>{low_52:,.2f}</b></div>", unsafe_allow_html=True)
            st.markdown(f"<div class='v-row'><span>12A En Yüksek</span><b>{high_52:,.2f}</b></div>", unsafe_allow_html=True)
        with g3:
            try:
                inf = tick.info
                pe = f"{inf.get('trailingPE', 0):.2f}"
                mcap = f"{inf.get('marketCap', 0)/1e9:.1f}B"
                st.markdown(f"<div class='v-row'><span>F/K Oranı</span><b>{pe}</b></div>", unsafe_allow_html=True)
                st.markdown(f"<div class='v-row'><span>Piyasa Değeri</span><b>{mcap}</b></div>", unsafe_allow_html=True)
            except: st.write("Finansal veri bekleniyor...")
        st.markdown("</div>", unsafe_allow_html=True)

        # ANLIK PANEL
        st.markdown(f"""
            <div class="live-data-box">
                <div class="live-item"><span class="live-label">Tavan</span><span class="live-val" style="color:#4ade80;">{tavan:,.2f}</span></div>
                <div class="live-item"><span class="live-label">Taban</span><span class="live-val" style="color:#f87171;">{taban:,.2f}</span></div>
                <div class="live-item"><span class="live-label">Günlük Hacim</span><span class="live-val">{h_data['Volume'].iloc[-1]:,.0f}</span></div>
                <div class="live-item"><span class="live-label">Trend (20G)</span><span class="live-val">{'POZİTİF' if last > sma20 else 'NEGATİF'}</span></div>
            </div>
        """, unsafe_allow_html=True)
except Exception as e:
    st.error("Veri güncellenirken bir hata oluştu.")
