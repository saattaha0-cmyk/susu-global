import streamlit as st
import pandas as pd
import random
import time

# Sayfa Ayarları
st.set_page_config(page_title="Susu Global - The World's Savings Network", page_icon="🌍", layout="wide")

# ==========================================
# 🌍 KÜRESEL FAZLAR & KÜLTÜREL YERELLEŞTİRME
# ==========================================
# Vizyondaki Fazlara göre yerelleştirilmiş terminoloji
CULTURE_MAP = {
    "Türkiye (Faz 1)": {"term": "Altın Günü", "currency": "TRY", "icon": "🇹🇷"},
    "Orta Doğu (Faz 2)": {"term": "Jam’iyya / Committee", "currency": "AED", "icon": "🇦🇪"},
    "Hindistan (Faz 3)": {"term": "Chit Fund", "currency": "INR", "icon": "🇮🇳"},
    "Afrika (Faz 4)": {"term": "Susu", "currency": "NGN", "icon": "🇳🇬"},
    "Latin Amerika (Faz 5)": {"term": "Tanda", "currency": "MXN", "icon": "🇲🇽"},
    "Global (Faz 6)": {"term": "Savings Circle", "currency": "USD", "icon": "🌐"}
}

# ==========================================
# 🎯 ÜRÜN EKOSİSTEMİ: HEDEF ODAKLI BİRİKİM
# ==========================================
SAVING_GOALS = {
    "Genel Birikim": "💰",
    "Ev Peşinatı": "🏠",
    "Araba Alımı": "🚗",
    "Eğitim / Okul": "🎓",
    "İş Kurma Sermayesi": "💼",
    "Tatil / Seyahat": "✈️"
}

# (Veritabanı fonksiyonları önceki versiyondaki gibi varsayılmıştır...)
if 'pools_dict' not in st.session_state:
    st.session_state.pools_dict = {}

# ==========================================
# WEB PORTAL ARAYÜZÜ (STREAMLIT ENGINE)
# ==========================================
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2953/2953363.png", width=70)
    st.title("Susu Core Engine")
    st.caption("🌍 Global Financial Inclusion Platform")
    st.write("---")
    
    st.subheader("🆕 Yeni Küresel Havuz Kur")
    with st.expander("Platform & Hedef Ayarları", expanded=True):
        new_id = st.text_input("Havuz ID (Örn: EV-TR-01)").strip()
        region = st.selectbox("Bölge & Kültür", list(CULTURE_MAP.keys()))
        goal = st.selectbox("Birikim Hedefi", list(SAVING_GOALS.keys()))
        
        region_data = CULTURE_MAP[region]
        st.info(f"Sistem Terimi: **{region_data['term']}** | Para Birimi: **{region_data['currency']}**")
        
        new_contrib = st.number_input(f"Aylık Katkı Payı ({region_data['currency']})", min_value=10, value=1000)
        new_duration = st.slider("Katılımcı Sayısı (Ay)", 3, 24, 10)
        
        if st.button("🚀 Küresel Ağa Dağıt (Deploy)"):
            if new_id:
                pool_name = f"{region_data['icon']} {SAVING_GOALS[goal]} {region.split(' ')[0]} {goal} {region_data['term']}"
                st.session_state.pools_dict[new_id] = {
                    "pool_id": new_id, 
                    "pool_name": pool_name,
                    "region": region,
                    "term": region_data['term'],
                    "goal": goal,
                    "currency": region_data['currency'],
                    "monthly_contribution": new_contrib,
                    "total_months": new_duration,
                    "users": []
                }
                st.success(f"✅ {pool_name} başarıyla oluşturuldu!")
                st.rerun()

# ==========================================
# ANA PANEL: YATIRIMCI VE VİZYON ÖZETİ
# ==========================================
st.title("🌍 Dünyanın Dijital Dayanışmalı Tasarruf Altyapısı")
st.markdown("""
*Bugün insanlar Uber ile taksi çağırıyor, Airbnb ile ev kiralıyor. Bizim platformumuzla ise dünyanın her yerindeki insanlar ortak hedefler için güvenle birikim yapıyor.*
""")
st.write("---")

if not st.session_state.pools_dict:
    st.warning("👈 Sol menüden ilk küresel havuzunuzu oluşturarak platformu başlatın.")
else:
    st.subheader("Aktif Global Havuzlar")
    cols = st.columns(3)
    idx = 0
    for pid, pdata in st.session_state.pools_dict.items():
        with cols[idx % 3]:
            st.card_title = pdata['pool_name']
            st.info(f"""
            **{pdata['pool_name']}**
            * **Tür:** {pdata['term']} ({pdata['region']})
            * **Hedef:** {pdata['goal']}
            * **Hacim:** {(pdata['monthly_contribution'] * pdata['total_months']):,} {pdata['currency']}
            * **Kapasite:** 0 / {pdata['total_months']} Kişi
            """)
        idx += 1