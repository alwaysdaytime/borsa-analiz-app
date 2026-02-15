import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from datetime import datetime
import requests

# --- 1. AYARLAR VE GÜVENLİK ---
st.set_page_config(page_title="Gemini Finans Pro", layout="wide", page_icon="📈")

# Telegram Bilgileri (Streamlit Secrets'tan çekilmesi önerilir)
# Yerel test için buraya doğrudan yazabilirsin.
def telegram_gonder(mesaj):
    try:
        token = st.secrets["TELEGRAM_TOKEN"]
        chat_id = st.secrets["TELEGRAM_CHAT"]
        url = f"https://api.telegram.org/bot{token}/sendMessage?chat_id={chat_id}&text={mesaj}"
        requests.get(url)
    except:
        pass # Secrets ayarlanmamışsa hata vermemesi için

# --- 2. FONKSİYONLAR ---

@st.cache_data(ttl=3600) # Veriyi 1 saat önbelleğe alarak hızı artırır
def veri_yukle(ticker, period="1y"):
    data = yf.Ticker(ticker).history(period=period)
    return data

def ai_tahmin_modeli(df):
    # Basit Feature Engineering
    df['MA5'] = df['Close'].rolling(5).mean()
    df['MA20'] = df['Close'].rolling(20).mean()
    df['RSI'] = 100 - (100 / (1 + (df['Close'].diff().gt(0).rolling(14).sum() / 14)))
    df['Target'] = (df['Close'].shift(-1) > df['Close']).astype(int)
    
    train_df = df.dropna()
    if len(train_df) < 30: return None, None # Yetersiz veri
    
    X = train_df[['MA5', 'MA20', 'RSI']]
    y = train_df['Target']
    
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X[:-1], y[:-1])
    
    prediction = model.predict(X.tail(1))[0]
    probability = model.predict_proba(X.tail(1))[0][1]
    return prediction, probability

# --- 3. ARAYÜZ (SIDEBAR) ---
st.sidebar.title("🚀 Finansal Kontrol")
sembol = st.sidebar.text_input("Hisse/Metal Sembolü (Örn: THYAO.IS, GC=F):", "THYAO.IS").upper()
zaman_araligi = st.sidebar.selectbox("Grafik Aralığı:", ["1mo", "3mo", "6mo", "1y", "2y"])

st.sidebar.markdown("---")
st.sidebar.info("📌 **BIST** hisseleri için sonuna **.IS** ekleyin. **Altın** için **GC=F** kullanın.")

# --- 4. ANA PANEL ---
df = veri_yukle(sembol, zaman_araligi)

if not df.empty:
    # Güncel Verileri Hesapla
    son_gun = df.iloc[-1]
    onceki_gun = df.iloc[-2]
    H, L, C = son_gun['High'], son_gun['Low'], son_gun['Close']
    
    # Pivot Hesaplama
    P = (H + L + C) / 3
    R1 = (2 * P) - L
    S1 = (2 * P) - H
    R2 = P + (H - L)
    S2 = P - (H - L)

    # Üst Bilgi Kartları
    col1, col2, col3, col4 = st.columns(4)
    degisim = ((C - onceki_gun['Close']) / onceki_gun['Close']) * 100
    col1.metric("Son Fiyat", f"{C:.2f}", f"{degisim:.2f}%")
    col2.metric("Pivot Seviyesi", f"{P:.2f}")
    col3.metric("Direnç 1 (R1)", f"{R1:.2f}", f" Fark: {R1-C:.2f}", delta_color="inverse")
    col4.metric("Destek 1 (S1)", f"{S1:.2f}", f" Fark: {S1-C:.2f}")

    # Grafik Bölümü
    fig = go.Figure(data=[go.Candlestick(x=df.index,
                open=df['Open'], high=df['High'],
                low=df['Low'], close=df['Close'], name="Fiyat")])
    
    fig.add_hline(y=P, line_dash="dash", line_color="orange", annotation_text="Pivot")
    fig.add_hline(y=R1, line_dash="dot", line_color="red", annotation_text="R1")
    fig.add_hline(y=S1, line_dash="dot", line_color="green", annotation_text="S1")
    
    fig.update_layout(template="plotly_dark", height=500, xaxis_rangeslider_visible=False,
                      title=f"{sembol} Teknik Analiz Görünümü")
    st.plotly_chart(fig, use_container_width=True)

    # Analiz ve Tahmin Bölümü
    tab1, tab2 = st.tabs(["🤖 Yapay Zeka Tahmini", "📊 İstatistiksel Veriler"])
    
    with tab1:
        yon, olasılık = ai_tahmin_modeli(df)
        if yon is not None:
            c1, c2 = st.columns(2)
            if yon == 1:
                c1.success(f"### Tahmin: YÜKSELİŞ 🚀")
                c2.write(f"**Güven Oranı:** %{olasılık*100:.2f}")
                st.write("Algoritma, geçmiş benzer formasyonlara dayanarak yarın için pozitif bir kapanış bekliyor.")
            else:
                c1.error(f"### Tahmin: DÜŞÜŞ 📉")
                c2.write(f"**Güven Oranı:** %{(1-olasılık)*100:.2f}")
                st.write("Dikkat: Model satış baskısının devam edebileceğini öngörüyor.")
        else:
            st.warning("Yapay zeka tahmini için yeterli veri oluşmadı.")

    with tab2:
        st.write(f"**Son 5 Günlük Hareket Tablosu**")
        st.dataframe(df.tail(5).style.highlight_max(axis=0))

    # Telegram Alarm Butonu (Opsiyonel Manuel Kontrol)
    if st.button("Fiyat Alarmını Telegram'a Gönder"):
        mesaj = f"🔔 {sembol} Analizi:\nFiyat: {C:.2f}\nDestek: {S1:.2f}\nDirenç: {R1:.2f}\nTahmin: {'Pozitif' if yon==1 else 'Negatif'}"
        telegram_gonder(mesaj)
        st.toast("Alarm gönderildi!")

else:
    st.error("Sembol bulunamadı. Lütfen kontrol edip tekrar deneyin.")

st.markdown("---")
st.caption(f"Veriler Yahoo Finance üzerinden anlık çekilmektedir. Son güncelleme: {datetime.now().strftime('%H:%M:%S')}")