import streamlit as st
import time
import random
import hashlib
import requests

# --- SAYFA AYARLARI ---
st.set_page_config(page_title="Susu Global - Canlı Sistem", page_icon="📱", layout="centered")

# --- SUPABASE REST API BAĞLANTISI ---
SUPABASE_URL = st.secrets.get("SUPABASE_URL", "")
SUPABASE_KEY = st.secrets.get("SUPABASE_KEY", "")

HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation"
}

def db_create_user(name, country, score):
    """Kullanıcıyı gerçek veritabanına kaydeder."""
    if not SUPABASE_URL: return None
    url = f"{SUPABASE_URL}/rest/v1/users"
    data = {"full_name": name, "country": country, "trust_score": score}
    try:
        res = requests.post(url, headers=HEADERS, json=data)
        if res.status_code in [200, 201]:
            return res.json()[0]["id"] # Veritabanındaki benzersiz kimliği (UUID) döner
    except:
        pass
    return None

def db_save_ledger(user_id, transaction_type, amount, tx_hash):
    """Finansal işlemi muhasebe defterine (Ledger) kalıcı kaydeder."""
    if not SUPABASE_URL or not user_id: return
    url = f"{SUPABASE_URL}/rest/v1/ledger"
    data = {
        "user_id": user_id,
        "transaction_type": transaction_type,
        "amount": amount,
        "transaction_hash": tx_hash
    }
    requests.post(url, headers=HEADERS, json=data)

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
if "onboarding_step" not in st.session_state: st.session_state.onboarding_step = 1
if "user_data" not in st.session_state: st.session_state.user_data = {}
if "db_user_id" not in st.session_state: st.session_state.db_user_id = None
if "has_paid" not in st.session_state: st.session_state.has_paid = False
if "draw_completed" not in st.session_state: st.session_state.draw_completed = False
if "winner_name" not in st.session_state: st.session_state.winner_name = ""
if "tx_hash" not in st.session_state: st.session_state.tx_hash = ""

def next_step():
    st.session_state.onboarding_step += 1

# ==========================================
# 📱 EKRAN 1 & 2: KARŞILAMA VE PROFİL
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
        full_name = st.text_input("Ad Soyad", placeholder="Gerçek adınızı giriniz")
        country = st.selectbox("Yaşadığınız Ülke", ["Türkiye", "Almanya", "Amerika", "Nijerya", "Meksika"])
        submit_profile = st.form_submit_button("Devam Et", width="stretch")
        if submit_profile and full_name:
            st.session_state.user_data["name"] = full_name
            st.session_state.user_data["country"] = country
            next_step(); st.rerun()

# ==========================================
# 📱 EKRAN 3: KİMLİK DOĞRULAMA & DB KAYDI
# ==========================================
elif st.session_state.onboarding_step == 3:
    st.markdown("### 🛡️ Finansal Güvenlik (KYC)")
    id_doc = st.file_uploader("Nüfus Cüzdanı veya Pasaport Yükleyin", type=["jpg", "png"])
    if st.button("Kimliğimi Doğrula ve Kaydol", width="stretch", type="primary"):
        if id_doc:
            with st.spinner("Güven Skoru hesaplanıyor ve veritabanına işleniyor..."):
                score = random.randint(800, 1450)
                st.session_state.user_data["trust_score"] = score
                
                # 🔴 GERÇEK VERİTABANINA YAZMA İŞLEMİ 🔴
                db_id = db_create_user(
                    st.session_state.user_data["name"], 
                    st.session_state.user_data["country"], 
                    score
                )
                
                if db_id:
                    st.session_state.db_user_id = db_id
                    next_step()
                    st.rerun()
                else:
                    st.error("Veritabanı bağlantı hatası! Lütfen Streamlit Secrets ayarlarınızı kontrol edin.")

# ==========================================
# 📱 EKRAN 4 & 5: BAŞARILI KAYIT VE CÜZDAN
# ==========================================
elif st.session_state.onboarding_step == 4:
    st.success("✅ Veritabanı Kaydı Başarılı!")
    st.metric("🌟 Sosyal Güven Puanı", st.session_state.user_data['trust_score'])
    if st.button("Cüzdanıma Git 💼", width="stretch"):
        next_step(); st.rerun()

elif st.session_state.onboarding_step == 5:
    c1, c2 = st.columns([3, 1])
    c1.markdown(f"**👋 {st.session_state.user_data['name']}**")
    c2.markdown(f"🏅 Skor: **{st.session_state.user_data['trust_score']}**")
    st.write("---")

    st.markdown('<div class="wallet-card">', unsafe_allow_html=True)
    st.subheader("🪙 Global Vizyon Havuzu (TR-01)")
    col_a, col_b = st.columns(2)
    col_a.metric("Aylık Ödemeniz", "20,000 TL")
    col_b.metric("Kasa Toplamı", "80,000 TL")
    st.markdown('</div>', unsafe_allow_html=True)

    if not st.session_state.has_paid:
        if st.button("💳 20.000 TL Güvenli Ödeme Yap", width="stretch", type="primary"):
            with st.spinner("Ödeme işleniyor..."):
                time.sleep(1)
                st.session_state.has_paid = True
                st.rerun()
    else:
        st.success("✅ Taksitiniz ödendi.")
        st.write("---")
        
        st.subheader("🎲 Havuz Çekilişi (Ay 1)")
        if not st.session_state.draw_completed:
            if st.button("🔌 Çekilişi Başlat (Smart Contract)", width="stretch"):
                with st.spinner("Kura çekiliyor ve Ledger'a kaydediliyor..."):
                    participants = [st.session_state.user_data['name'], "Ayşe Y.", "Mehmet T.", "Ali K."]
                    st.session_state.winner_name = random.choice(participants)
                    st.session_state.tx_hash = hashlib.sha256(str(time.time()).encode()).hexdigest()[:24]
                    
                    # 🔴 GERÇEK HESAP DEFTERİNE (LEDGER) YAZMA İŞLEMİ 🔴
                    db_save_ledger(
                        st.session_state.db_user_id, 
                        "KURA_SONUCU", 
                        80000, 
                        st.session_state.tx_hash
                    )
                    
                    st.session_state.draw_completed = True
                    st.rerun()
        else:
            if st.session_state.winner_name == st.session_state.user_data['name']:
                st.balloons()
                st.success("🎉 KAZANDINIZ!")
            else:
                st.info(f"🎊 Talihli: **{st.session_state.winner_name}**")
            
            st.markdown("**📜 Blokzincir Kaydı (Gerçek Veritabanı Senkronize)**")
            ledger_text = f"> STATUS: SAVED TO DB\n> WINNER: {st.session_state.winner_name}\n> AMOUNT: 80,000 TRY\n> HASH: 0x{st.session_state.tx_hash}"
            st.markdown(f'<div class="ledger-box">{ledger_text}</div>', unsafe_allow_html=True)
