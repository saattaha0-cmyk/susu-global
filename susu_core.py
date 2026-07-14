import streamlit as st
import requests

# --- AYARLAR ---
SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
HEADERS = {"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}"}

st.title("Susu Global - FinTech Platform")

# --- GÜVEN KARNESİ ---
st.subheader("Güven Karnem")
try:
    res_score = requests.get(f"{SUPABASE_URL}/rest/v1/users?id=eq.9741f74f-c083-4832-b54b-4662cd8b0cc8", headers=HEADERS)
    user_data = res_score.json()
    if user_data:
        skor = user_data[0].get('trust_score', 100)
        st.progress(min(skor / 200, 1.0))
        st.write(f"Güven Puanın: **{skor} / 200**")
except:
    st.write("Güven karnesi verisi çekilemedi.")

# --- HAVUZLAR ---
res = requests.get(f"{SUPABASE_URL}/rest/v1/pools", headers=HEADERS)
pools = res.json()
st.subheader("Aktif Havuzlar")
for pool in pools:
    st.write(f"**{pool['pool_name']}** - Aylık: {pool['monthly_amount']} TL")
    if st.button(f"Havuza Katıl: {pool['pool_name']}", key=pool['pool_name']):
        st.success("İşlem başlatıldı...")
        st.rerun()

# --- İŞLEM GEÇMİŞİ (LEDGER) ---
st.divider()
st.subheader("İşlem Geçmişim")
try:
    res_ledger = requests.get(f"{SUPABASE_URL}/rest/v1/ledger?user_id=eq.9741f74f-c083-4832-b54b-4662cd8b0cc8", headers=HEADERS)
    ledger_data = res_ledger.json()

    if ledger_data:
        for tx in ledger_data:
            st.write(f"- {tx['transaction_type']}: **{tx['amount']} TL**")
    else:
        st.write("Henüz bir işlem hareketin yok.")
except:
    st.write("İşlem geçmişi yüklenirken bir sorun oluştu.")
