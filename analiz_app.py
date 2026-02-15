if df is not None:
    # Sayısal veri çevrimi için en güvenli fonksiyon
    def to_val(val):
        try:
            # Eğer veri bir seri ise ilk elemanını al, değilse doğrudan float'a çevir
            v = val.iloc[-1] if hasattr(val, 'iloc') else val
            return float(v.iloc[0]) if hasattr(v, 'iloc') else float(v)
        except:
            return 0.0
    
    son_fiyat = to_val(df['Close'])
    rsi_son = to_val(df['RSI'])
    ma20_son = to_val(df['MA20'])
    yuksek = df['High'].max()
    hacim_son = to_val(df['Volume']) # Hacmi burada güvenlice alıyoruz

    # --- ÜST PANEL ---
    st.subheader(f"📊 {st.session_state.secilen_hisse} Terminal")
    
    col_cards, col_kademe = st.columns([3, 1])
    
    with col_cards:
        if rsi_son < 35: sig_col, sig_txt = "#28a745", "ALIM BÖLGESİ"
        elif rsi_son > 65: sig_col, sig_txt = "#dc3545", "SATIŞ BÖLGESİ"
        else: sig_col, sig_txt = "#6c757d", "NÖTR / İZLE"
        st.markdown(f"<div class='signal-mini' style='background-color:{sig_col}'>{sig_txt}</div>", unsafe_allow_html=True)

        c1, c2, c3, c4 = st.columns(4)
        c1.markdown(f"<div class='compact-card'><h4>Fiyat</h4><h2>{son_fiyat:,.2f}</h2></div>", unsafe_allow_html=True)
        c2.markdown(f"<div class='compact-card'><h4>RSI</h4><h2>{rsi_son:.1f}</h2></div>", unsafe_allow_html=True)
        c3.markdown(f"<div class='compact-card'><h4>MA20</h4><h2>{ma20_son:,.2f}</h2></div>", unsafe_allow_html=True)
        # Yüksek değerini de güvenli çeviriyoruz
        c4.markdown(f"<div class='compact-card'><h4>Zirve</h4><h2>{to_val(yuksek):,.2f}</h2></div>", unsafe_allow_html=True)

    with col_kademe:
        # Hacim bölme işlemini burada güvenli değişkenden yapıyoruz
        hacim_milyon = hacim_son / 1e6
        st.markdown("<div class='kademe-box'><b>KADEMELER (Pivot)</b><br>" + 
                    f"🟢 Direnç: {son_fiyat*1.02:,.2f}<br>" +
                    f"⚪ Pivot: {son_fiyat:,.2f}<br>" +
                    f"🔴 Destek: {son_fiyat*0.98:,.2f}<br>" +
                    f"📉 Hacim: {hacim_milyon:.1f}M</div>", unsafe_allow_html=True)
