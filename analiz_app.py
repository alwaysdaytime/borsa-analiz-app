import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# --- 1. SAYFA AYARLARI ---
st.set_page_config(page_title="Vision Finans Terminali", layout="wide")

# --- 2. VARSAYILAN LİSTE (DEĞİŞTİREBİLİRSİN) ---
VARSAYILAN_LISTEM = "THYAO.IS, EREGL.IS, SISE.IS, BTC-USD, GC=F, FROTO.IS"

# --- 3. TASARIM (AYDINLIK & KOMPAKT) ---
st.markdown("""
    <style>
    .stApp { background-color: #f8f9fa; }
    .compact-card {
        background-color: #ffffff; padding: 10px; border-radius: 8px;
        border: 1px solid #e9ecef; text-align: center; box-shadow: 0 2px 4px rgba(0,0,0,0.03);
    }
    .compact-card h4 { margin: 0; font-size: 0.8rem; color: #6c757d; }
    .compact-card h2 { margin: 5px 0; font-size: 1.2rem; color: #1a73e8; }
    .kademe-box {
        background-color: #ffffff; padding: 15px; border-radius: 8px;
        border: 1px solid #dee2e6; font-family: monospace; font-size: 0.85rem; height: 100%;
    }
    .signal-mini {
        padding: 8px; border-radius: 5px; color: white; text-align: center;
        font-weight: bold; font-size: 0.9rem; margin-bottom: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 4. YAN PANEL (SIDEBAR) ---
with st.sidebar:
    st.title("🛡️ Vision Pro")
    if 'my_list' not in st.session_state:
        st.session_state.my_list = VARSAYILAN_LISTEM
    
    user_input = st.text_area("İzleme Listesini Yönet:", value=st.session_state.my_list)
    if st.button("Listeyi Kaydet"):
        st.session_state.my_list = user_input
        st.rerun()

    izleme_listesi = [x.strip().upper() for x in st.session_state.my_list.split(",")]
    
    if 'secilen_hisse' not in st.session_state:
        st.session_state.secilen_hisse = izleme_listesi[0]

    st.markdown("---")
    for f in izleme_listesi:
        if st.button(f"🔍 {f}", use_container_width=True):
            st.session_state.secilen_hisse = f
    
    periyot = st.selectbox("Dönem", ["1mo", "3mo", "6mo", "1y", "2y"], index=2)

# --- 5. VERİ ÇEKME FONKSİYONU ---
@st.cache_data(ttl=60)
def verileri_getir(symbol, period):
    try:
        data = yf.download(symbol, period=period)
        if data.empty: return None
        # Teknik Göstergeler
        data['MA20'] = data['Close'].rolling(window=20).mean()
        delta = data['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
        data['RSI'] = 100 - (100 / (1 + (gain / loss)))
        return data
    except:
        return None

# Veriyi Çek
df = verileri_getir(st.session_state.secilen_hisse, periyot)

# --- 6. GÖRSELLEŞTİRME VE ANALİZ ---
if df is not None:
    # Sayısal veri çevrimi için güvenlik fonksiyonu
    def to_val(val):
        try:
            v = val.iloc[-1] if hasattr(val, 'iloc') else val
            return float(v.iloc[0]) if hasattr(v, 'iloc') else float(v)
        except:
            return 0.0
    
    son_fiyat = to_val(df['Close'])
    rsi_son = to_val(df['RSI'])
    ma20_son = to_val(df['MA20'])
    yuksek = to_val(df['High'].max())
    hacim_son = to_val(df['Volume'])

    st.subheader(f"📊 {st.session_state.secilen_hisse} Finansal Terminal")
    
    col_cards, col_kademe = st.columns([3, 1])
    
    with col_cards:
        # Sinyal Durumu
        if rsi_son < 35: sig_col, sig_txt = "#28a745", "ALIM BÖLGESİ (UCUZ)"
        elif rsi_son > 65: sig_col, sig_txt = "#dc3545", "SATIŞ BÖLGESİ (PAHALI)"
        else: sig_col, sig_txt = "#6c757d", "NÖTR / İZLE"
        
        st.markdown(f"<div class='signal-mini' style='background-color:{sig_col}'>{sig_txt}</div>", unsafe_allow_html=True)

        # Kartlar
        c1, c2, c3, c4 = st.columns(4)
        c1.markdown(f"<div class='compact-card'><h4>Fiyat</h4><h2>{son_fiyat:,.2f}</h2></div>", unsafe_allow_html=True)
        c2.markdown(f"<div class='compact-card'><h4>RSI (14)</h4><h2>{rsi_son:.1f}</h2></div>", unsafe_allow_html=True)
        c3.markdown(f"<div class='compact-card'><h4>MA20</h4><h2>{ma20_son:,.2f}</h2></div>", unsafe_allow_html=True)
        c4.markdown(f"<div class='compact-card'><h4>Zirve</h4><h2>{yuksek:,.2f}</h2></div>", unsafe_allow_html=True)

    with col_kademe:
        # Kademeler ve Pivotlar
        st.markdown("<div class='kademe-box'><b>TEKNİK KADEMELER</b><br><hr>" + 
                    f"<span style='color:green'>⬆️ Direnç: {son_fiyat*1.02:,.2f}</span><br>" +
                    f"<span style='color:gray'>⚪ Pivot: {son_fiyat:,.2f}</span><br>" +
                    f"<span style='color:red'>⬇️ Destek: {son_fiyat*0.98:,.2f}</span><br><hr>" +
                    f"📊 Hacim: {hacim_son/1e6:.1f}M</div>", unsafe_allow_html=True)

    # Grafik
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.05, row_heights=[0.75, 0.25])
    fig.add_trace(go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'], name="Mum"), row=1, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=df['MA20'], name="MA20", line=dict(color='orange', width=1.5)), row=1, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=df['RSI'], name="RSI", line=dict(color='purple')), row=2, col=1)
    
    fig.update_layout(height=550, template="plotly_white", xaxis_rangeslider_visible=False, margin=dict(l=0,r=0,t=0,b=0))
    st.plotly_chart(fig, use_container_width=True)

else:
    st.error("Sembol bulunamadı veya veri çekme hatası. Lütfen yan panelden sembolü kontrol edin.")
