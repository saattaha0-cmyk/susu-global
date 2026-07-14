import streamlit as st
import time
import random
import hashlib
import requests

# --- SAYFA AYARLARI ---
st.set_page_config(page_title="Susu Global - Canlı Sistem", page_icon="📱", layout="centered")

# --- SUPABASE REST API BAĞLANTISI ---
SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]

HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation"
}

def db_create_user(name, country, score):
    """Kullanıcıyı veritabanına kaydeder."""
    url = f"{SUPABASE_URL}/rest/v1/users"
    data = {"full_name": name, "country": country, "trust_score": score}
    res = requests.post(url, headers=HEADERS, json=data)
    if res.status_code in [200, 201]:
        return res.json()[0]["id"]
    return None

def db_save_ledger(user_id, transaction_type, amount, tx_hash):
    """İşlemi kalıcı deftere (Ledger) kaydeder."""
    url = f"{SUPABASE_URL}/rest/v1/ledger"
    data = {
        "user_id": user_id,
        "transaction_type": transaction_type,
        "amount": amount,
        "transaction_hash": tx_hash
    }
    requests.post(url, headers=HEADERS, json=data)

# --- UYGULAMA MANTIĞI ---
if "onboarding_step" not in st.session_state: st.session_state.onboarding_step = 1

if st.session_state.onboarding_step == 1:
    st.title("Susu Global")
    if st.button("Hemen Başla"):
        st.session_state.onboarding_step = 2
        st.rerun()

elif st.session_state.onboarding_step == 2:
    st.subheader("Profil Bilgileri")
    name = st.text_input("Ad Soyad")
    if st.button("Kaydet"):
        st.session_state.user_name = name
        # Basit bir skor üretip DB'ye gönderiyoruz
        db_id = db_create_user(name, "Türkiye", 1000)
        st.session_state.db_user_id = db_id
        st.session_state.onboarding_step = 3
        st.rerun()

elif st.session_state.onboarding_step == 3:
    st.success("Kayıt Başarılı! Sistem artık veritabanı ile konuşuyor.")
    st.write(f"Kullanıcı ID: {st.session_state.db_user_id}")
    if st.button("Ledger Testi Yap (Ödeme Kaydet)"):
        tx_hash = hashlib.sha256(str(time.time()).encode()).hexdigest()[:16]
        db_save_ledger(st.session_state.db_user_id, "DENEME_ODEME", 20000, tx_hash)
        st.write("İşlem veritabanına başarıyla kaydedildi!")
