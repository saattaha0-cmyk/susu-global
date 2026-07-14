import streamlit as st
import time
import random
import hashlib

# --- SAYFA AYARLARI ---
st.set_page_config(page_title="Susu Global - Cüzdan", page_icon="📱", layout="centered")

# --- CSS İLE MOBİL GÖRÜNÜM ---
st.markdown("""
<style>
    .onboard-header { font-size: 2.5rem; font-weight: 800; text-align: center; color: #1E3A8A; margin-bottom: 0px;}
    .onboard-sub { font-size: 1.1rem; text-align: center; color: #64748B; margin-bottom: 30px;}
    .stButton>button { border-radius: 20px; font-weight: bold; background-color: #2563EB; color: white; }
    .stButton>button:hover { background-color: #1D4ED8; color: white;}
    .wallet-card { background-color: #F8FAFC; padding: 20px; border-radius: 15px; border: 1px solid #E2E8F0; margin-bottom: 20px; }
    .ledger-box { font-family: monospace; font-size: 0.85rem; background-color: #1E1E1E; color: #00FF00; padding: 15px; border-radius: 10px; margin-top: 10px;}
</style>
""", unsafe_allow_html=True)

# --- UYGULAMA HAFIZASI ---
if "onboarding_step" not in st.session_state:
    st.session_state.onboarding_step = 1
if "user_data" not in st.session_state:
    st.session_state.user_data = {}
if "has_paid" not in st.session_state:
    st.session_state.has_paid = False
if "draw_completed" not in st.session_state:
    st.session_state.draw_completed = False
if "winner_name" not in st.session_state:
    st.session_state.winner_name = ""
if "tx_hash" not in st.session_state:
    st.session_state.tx_hash = ""

def next_step():
    st.session_state.onboarding_step += 1

# ==========================================
# 📱 EKRAN 1 - 4: (ONBOARDING VE KYC AKIŞI)
# ==========================================
if st.session_state.onboarding_step == 1:
    st.markdown('<p class="onboard-header">Susu Global</p>', unsafe_allow_html=True)
    st.markdown('<p class="onboard-sub">Dünyanın Dijital Dayanışmalı Tasarruf Ağı</p>', unsafe_allow_html=True)
    st.image("https://cdn-icons-png.flaticon.com/512/7904/7904033.png", width=150) 
    st.write("---")
    if st.button("Hemen Başla 🚀", width="stretch"):
        next_step(); st.rerun()

elif st.session_state.onboarding_step == 2:
    st.markdown("### 👤 Profilinizi Oluşturun")
    with st.form("profile_form"):
        full_name = st.text_input("Ad Soyad", placeholder="Örn: Ahmet Yılmaz")
        country = st.selectbox("Yaşadığınız Ülke", ["Türkiye (Faz 1)", "Almanya", "Amerika", "Nijerya", "Meksika"])
        submit_profile = st.form_submit_button("Devam Et", width="stretch")
        if submit_profile and full_name:
            st.session_state.user_data["name"] = full_name
            st.session_state.user_data["country"] = country
            next_step(); st.rerun()

elif st.session_state.onboarding_step == 3:
    st.markdown("### 🛡️ Finansal Güvenlik (KYC)")
    id_doc = st.file_uploader("Nüfus Cüzdanı veya Pasaport Yükleyin", type=["jpg", "png"])
    if st.button("Kimliğimi Doğrula ve Analiz Et", width="stretch", type="primary"):
        if id_doc:
            with st.spinner("Sosyal Güven Puanınız hesaplanıyor..."):
                time.sleep(1) 
                st.session_state.user_data["trust_score"] = random.randint(800, 1450)
                next_step(); st.rerun()

elif st.session_state.onboarding_step == 4:
    st.balloons()
    st.success("✅ Doğrulama Başarılı!")
    st.metric("🌟 Sosyal Güven Puanı", st.session_state.user_data['trust_score'])
    if st.button("Cüzdanıma Git 💼", width="stretch"):
        next_step(); st.rerun()

# ==========================================
# 📱 EKRAN 5: ANA CÜZDAN VE AKILLI KONTRAT KURA ÇEKİMİ
# ==========================================
elif st.session_state.onboarding_step == 5:
    c1, c2 = st.columns([3, 1])
    c1.markdown(f"**👋 {st.session_state.user_data['name']}**")
    c2.markdown(f"🏅 Skor: **{st.session_state.user_data['trust_score']}**")
    st.write("---")

    # Havuz Kartı Tasarımı
    st.markdown('<div class="wallet-card">', unsafe_allow_html=True)
    st.subheader("🪙 Global Vizyon Havuzu (TR-01)")
    st.caption("Durum: 🟢 Aktif | Ay: 1/4 | Toplam Kapasite: 4 Kişi")
    
    col_a, col_b = st.columns(2)
    col_a.metric("Aylık Ödemeniz", "20,000 TL")
    col_b.metric("Kasa Toplamı", "80,000 TL")
    st.markdown('</div>', unsafe_allow_html=True)

    # ⚡ ÖDEME VE KURA İŞLEMLERİ
    st.markdown("### ⚡ İşlemler")
    
    if not st.session_state.has_paid:
        st.warning("⏳ Bu ayki ödemenizi henüz yapmadınız.")
        if st.button("💳 20.000 TL Güvenli Ödeme Yap", width="stretch", type="primary"):
            with st.spinner("Bankanızla iletişim kuruluyor..."):
                time.sleep(2)
                st.session_state.has_paid = True
                st.rerun()
    else:
        # Ödeme yapıldıysa kura paneli açılır
        st.success("✅ Taksitiniz ödendi. (Tüm üyelerin ödemesi veya Banka Garantisi tamamlandı).")
        st.write("---")
        
        st.subheader("🎲 Havuz Çekilişi (Ay 1)")
        if not st.session_state.draw_completed:
            st.info("Akıllı kontrat kura çekimi için hazır.")
            if st.button("🔌 Çekilişi Başlat (Smart Contract)", width="stretch"):
                with st.spinner("Şifrelenmiş kura algoritması çalışıyor... Lütfen bekleyin."):
                    time.sleep(3) # Heyecan yaratmak için bekleme süresi
                    
                    # Rastgele kazanan belirleme (Kullanıcı veya 3 bottan biri)
                    participants = [st.session_state.user_data['name'], "Ayşe Y. (Banka Destekli)", "Mehmet T.", "Ali K."]
                    st.session_state.winner_name = random.choice(participants)
                    
                    # Gerçekçi bir dijital cüzdan hash kodu üretme
                    st.session_state.tx_hash = hashlib.sha256(str(time.time()).encode()).hexdigest()[:24]
                    st.session_state.draw_completed = True
                    st.rerun()
        else:
            # Çekiliş Sonucu Ekranı
            if st.session_state.winner_name == st.session_state.user_data['name']:
                st.balloons()
                st.success("🎉 İNANILMAZ! BU AYIN KAZANANI SİZSİNİZ!")
                st.metric("💸 Cüzdanınıza Aktarılan Tutar", "+80,000 TL")
            else:
                st.info(f"🎊 Bu ayın talihlisi: **{st.session_state.winner_name}**")
                st.write("Havuz tutarı talihlinin hesabına aktarıldı. Sonraki ay şansınız artacak!")
            
            # Kurumsal Hesap Defteri (Ledger) Özeti
            st.write("---")
            st.markdown("**📜 Blokzincir Kaydı (Smart Ledger)**")
            ledger_text = f"""
> STATUS: VERIFIED
> POOL ID: TR-01
> WINNER: {st.session_state.winner_name}
> AMOUNT: 80,000 TRY
> TRANSACTION HASH: 0x{st.session_state.tx_hash}
> TIMESTAMP: {time.strftime('%Y-%m-%d %H:%M:%S')}
            """
            st.markdown(f'<div class="ledger-box">{ledger_text}</div>', unsafe_allow_html=True)
            
            if st.button("Sonraki Aya Geç (Test) ⏭️", width="stretch"):
                # Simülasyonu resetleyip tekrar denemek için
                st.session_state.has_paid = False
                st.session_state.draw_completed = False
                st.rerun()
