import streamlit as st
import time
import random

# --- SAYFA AYARLARI ---
st.set_page_config(page_title="Susu Global - Onboarding", page_icon="📱", layout="centered")

# --- CSS İLE MOBİL GÖRÜNÜM (ŞIKLIK) KATIYORUZ ---
st.markdown("""
<style>
    .onboard-header { font-size: 2.5rem; font-weight: 800; text-align: center; color: #1E3A8A; margin-bottom: 0px;}
    .onboard-sub { font-size: 1.1rem; text-align: center; color: #64748B; margin-bottom: 30px;}
    .stButton>button { border-radius: 20px; font-weight: bold; background-color: #2563EB; color: white; }
    .stButton>button:hover { background-color: #1D4ED8; color: white;}
</style>
""", unsafe_allow_html=True)

# --- UYGULAMA HAFIZASI (SESSION STATE) ---
if "onboarding_step" not in st.session_state:
    st.session_state.onboarding_step = 1
if "user_data" not in st.session_state:
    st.session_state.user_data = {}

# --- FONKSİYONLAR ---
def next_step():
    st.session_state.onboarding_step += 1

def reset_app():
    st.session_state.onboarding_step = 1
    st.session_state.user_data = {}
    st.rerun()

# ==========================================
# 📱 EKRAN 1: KARŞILAMA VE VİZYON
# ==========================================
if st.session_state.onboarding_step == 1:
    st.markdown('<p class="onboard-header">Susu Global</p>', unsafe_allow_html=True)
    st.markdown('<p class="onboard-sub">Dünyanın Dijital Dayanışmalı Tasarruf Ağı</p>', unsafe_allow_html=True)
    
    st.image("https://cdn-icons-png.flaticon.com/512/7904/7904033.png", width=150, use_container_width=True) # İkon
    st.write("---")
    
    st.info("💡 **Neden Susu?**\nTek başınıza para biriktirmekte zorlanıyor musunuz? Dünyanın dört bir yanından insanlarla güvenilir havuzlarda buluşun, hedeflerinize birlikte ulaşın.")
    
    # Uyarıyı çözdüğümüz yeni buton formatı (width="stretch")
    if st.button("Hemen Başla 🚀", width="stretch"):
        next_step()
        st.rerun()

# ==========================================
# 📱 EKRAN 2: TEMEL PROFİL (KİMLİK)
# ==========================================
elif st.session_state.onboarding_step == 2:
    st.markdown("### 👤 Profilinizi Oluşturun")
    st.write("Yasal uyum (AML) gereği gerçek bilgilerinizi giriniz.")
    
    with st.form("profile_form"):
        full_name = st.text_input("Ad Soyad", placeholder="Örn: Ahmet Yılmaz")
        country = st.selectbox("Yaşadığınız Ülke (Bölge)", ["Türkiye (Faz 1)", "Almanya (Faz 6)", "Amerika Birleşik Devletleri", "Nijerya", "Meksika"])
        phone = st.text_input("Telefon Numarası", placeholder="+90 5XX XXX XX XX")
        
        submit_profile = st.form_submit_button("Devam Et", width="stretch")
        
        if submit_profile:
            if not full_name or not phone:
                st.error("Lütfen adınızı ve telefonunuzu eksiksiz girin!")
            else:
                st.session_state.user_data["name"] = full_name
                st.session_state.user_data["country"] = country
                st.session_state.user_data["phone"] = phone
                next_step()
                st.rerun()

# ==========================================
# 📱 EKRAN 3: KİMLİK DOĞRULAMA (KYC) VE GÜVEN SKORU
# ==========================================
elif st.session_state.onboarding_step == 3:
    st.markdown("### 🛡️ Finansal Güvenlik (KYC)")
    st.write("Susu'nun güvene dayalı ekosistemine katılmak için kimliğinizi doğrulayın.")
    
    id_doc = st.file_uploader("Nüfus Cüzdanı veya Pasaport Yükleyin", type=["jpg", "png", "pdf"])
    
    if st.button("Kimliğimi Doğrula ve Analiz Et", width="stretch", type="primary"):
        if id_doc is None:
            st.warning("Devam etmek için bir belge yüklemeniz gerekiyor.")
        else:
            with st.spinner("Finansal geçmişiniz taranıyor ve Sosyal Güven Puanınız (Trust Score) hesaplanıyor..."):
                # Banka API Simülasyonu
                time.sleep(3) 
                
                # Algoritma: 500-1500 arası rastgele gerçekçi bir kredi/güven skoru atıyoruz
                trust_score = random.randint(600, 1450)
                st.session_state.user_data["trust_score"] = trust_score
                
                next_step()
                st.rerun()

# ==========================================
# 📱 EKRAN 4: BAŞARILI KAYIT & DASHBOARD'A GEÇİŞ
# ==========================================
elif st.session_state.onboarding_step == 4:
    st.balloons()
    st.success("✅ Doğrulama Başarılı!")
    
    st.markdown(f"### Hoş Geldin, {st.session_state.user_data['name']}!")
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Bölge / Kültür", st.session_state.user_data['country'].split(' ')[0])
    with col2:
        # Puan 1000 üzeriyse yeşil, altındaysa turuncu gösterme taktiği
        score_color = "normal" if st.session_state.user_data['trust_score'] > 1000 else "inverse"
        st.metric("🌟 Sosyal Güven Puanı", st.session_state.user_data['trust_score'], delta="Sisteme Giriş", delta_color=score_color)
    
    st.write("---")
    st.info("Güven puanınız, yüksek bütçeli (örneğin aylık 20.000 TL) havuzlara girebilmeniz için yeterlidir. Sistemimizde herhangi bir ödeme gecikmesinde banka garantörlüğü devreye girer, ancak güven puanınız düşer.")
    
    if st.button("Havuzları Keşfet (Ana Ekrana Git)", width="stretch"):
        # Burada ileride Cüzdan ekranına yönlendireceğiz
        reset_app()
