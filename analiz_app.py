# --- ÜST PANEL: METRİKLER (HATA DÜZELTİLMİŞ) ---
    son_fiyat = float(df['Close'].iloc[-1])
    onceki_fiyat = float(df['Close'].iloc[-2])
    degisim = ((son_fiyat - onceki_fiyat) / onceki_fiyat) * 100
    
    # Hacim verisini güvenli bir şekilde sayıya çeviriyoruz
    try:
        hacim_degeri = float(df['Volume'].iloc[-1])
    except:
        hacim_degeri = 0

    st.title(f"📊 {sembol} Analiz Paneli")
    
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Anlık Fiyat", f"{son_fiyat:,.2f}", f"{degisim:+.2f}%")
    m2.metric("Günlük Hacim", f"{hacim_degeri:,.0f}")
    m3.metric("RSI (14)", f"{float(df['RSI'].iloc[-1]):.1f}")
    m4.metric("20 Günlük Ort.", f"{float(df['MA20'].iloc[-1]):,.2f}")
