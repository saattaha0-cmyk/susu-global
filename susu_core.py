import streamlit as st
import time
import random

# --- SAYFA AYARLARI ---
st.set_page_config(page_title="Susu Global", page_icon="📱", layout="centered")

# --- CSS İLE MOBİL GÖRÜNÜM ---
st.markdown("""
<style>
    .onboard-header { font-size: 2.5rem; font-weight: 800; text-align: center; color: #1E3A8A; margin-bottom: 0px;}
    .onboard-sub { font-size: 1.1rem; text-align: center; color: #64748B; margin-bottom: 30px;}
    .stButton>button { border-radius: 20px; font-weight: bold; background-color: #2563EB; color: white; }
    .stButton>button:hover { background-color: #1D4ED8; color: white;}
    .wallet-card { background-color: #F8FAFC; padding: 20px; border-radius: 15px; border: 1px solid #E2E8F0; margin-bottom: 20px; }
</style>
""", unsafe_allow_html=True)

# --- UYGULAMA HAFIZASI ---
if "onboarding_step" not in st.session_state:
    st.session_state.onboarding_step = 1
if "user_data" not in st.session_state:
    st.session_state.user_data = {}
if "has_paid" not in st.session_state:
    st.session_state.has_paid = False

def next_step():
    st.session_state.onboarding_step += 1

# ==========================================
# 📱 EKRAN 1: KARŞILAMA VE VİZYON
# ==========================================
if st.session_state.onboarding_step == 1:
    st.markdown('<p class="onboard-header">Susu Global</p>', unsafe_allow_html=True)
    st.markdown('<p class="onboard-sub">Dünyanın Dijital Dayanışmalı Tasarruf Ağı</p>', unsafe_allow_html=True)
    st.image("https://cdn-icons-png.flaticon.com/512/7904/7904033.png", width=150) 
    st.write("---")
    st.info("💡 **Neden Susu?**\nDünyanın dört bir yanından insanlarla güvenilir havuzlarda buluşun, hedeflerinize birlikte ulaşın.")
    
    if st.button("Hemen Başla 🚀", width="stretch"):
        next_step()
        st.rerun()

# ==========================================
# 📱 EKRAN 2: TEMEL PROFİL
# ==========================================
elif st.session_state.onboarding_step == 2:
    st.markdown("### 👤 Profilinizi Oluşturun")
    with st.form("profile_form"):
        full_name = st.text_input("Ad Soyad", placeholder="Örn: Ahmet Yılmaz")
        country = st.selectbox("Yaşadığınız Ülke", ["Türkiye (Faz 1)", "Almanya (Faz 6)", "Amerika", "Nijerya", "Meksika"])
        submit_profile = st.form_submit_button("Devam Et", width="stretch")
        
        if submit_profile and full_name:
            st.session_state.user_data["name"] = full_name
            st.session_state.user_data["country"] = country
            next_step()
            st.rerun()

# ==========================================
# 📱 EKRAN 3: KİMLİK DOĞRULAMA (KYC)
# ==========================================
elif st.session_state.onboarding_step == 3:
    st.markdown("### 🛡️ Finansal Güvenlik (KYC)")
    id_doc = st.file_uploader("Nüfus Cüzdanı veya Pasaport Yükleyin", type=["jpg", "png"])
    
    if st.button("Kimliğimi Doğrula ve Analiz Et", width="stretch", type="primary"):
        if id_doc:
            with st.spinner("Sosyal Güven Puanınız (Trust Score) hesaplanıyor..."):
                time.sleep(2) 
                st.session_state.user_data["trust_score"] = random.randint(800, 1450)
                next_step()
                st.rerun()
        else:
            st.warning("Lütfen bir belge yükleyin.")

# ==========================================
# 📱 EKRAN 4: BAŞARILI KAYIT
# ==========================================
elif st.session_state.onboarding_step == 4:
    st.balloons()
    st.success("✅ Doğrulama Başarılı!")
    st.markdown(f"### Hoş Geldin, {st.session_state.user_data['name']}!")
    
    st.metric("🌟 Sosyal Güven Puanı", st.session_state.user_data['trust_score'])
    st.info("Güven puanınız yüksek bütçeli havuzlara girmek için yeterli!")
    
    if st.button("Cüzdanıma Git 💼", width="stretch"):
        next_step()
        st.rerun()

# ==========================================
# 📱 EKRAN 5: ANA CÜZDAN (DASHBOARD)
# ==========================================
elif st.session_state.onboarding_step == 5:
    # Üst Bilgi Barı
    c1, c2 = st.columns([3, 1])
    c1.markdown(f"**👋 {st.session_state.user_data['name']}**")
    c2.markdown(f"🏅 Skor: **{st.session_state.user_data['trust_score']}**")
    st.write("---")

    # Havuz Kartı Tasarımı
    st.markdown('<div class="wallet-card">', unsafe_allow_html=True)
    st.subheader("🪙 Global Vizyon Havuzu (TR-01)")
    st.caption("Durum: 🟢 Aktif | Ay: 1/4 | Toplam Kapasite: 4 Kişi")
    
    st.write("")
    col_a, col_b = st.columns(2)
    col_a.metric("Aylık Ödemeniz", "20,000 TL")
    col_b.metric("Kasa (Havuz) Toplamı", "80,000 TL")
    st.markdown('</div>', unsafe_allow_html=True)

    st.write("---")
    st.markdown("### ⚡ İşlemler")
    
    # Ödeme Simülasyonu
    if not st.session_state.has_paid:
        st.warning("⏳ Bu ayki ödemenizi henüz yapmadınız.")
        if st.button("💳 20.000 TL Güvenli Ödeme Yap", width="stretch", type="primary"):
            with st.spinner("Bankanızla iletişim kuruluyor, akıllı kontrata aktarılıyor..."):
                time.sleep(2)
                st.session_state.has_paid = True
                st.rerun()
    else:
        st.success("✅ Bu ayki taksitiniz ödendi! Kura çekilişini bekliyorsunuz.")
        st.progress(100)
        st.info("Eğer diğer üyeler ödeme yapamazsa, Susu Banka Garantisi devreye girerek havuzu tamamlayacaktır.")
