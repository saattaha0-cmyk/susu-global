import streamlit as st
import requests
import json

# --- AYARLAR ---
SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation"
}

st.title("Susu Global - FinTech Platform")

# --- PANEL (DASHBOARD) ---
st.subheader("Finansal Durumum")
# SQL'den gelen veriyi çek
try:
    res_summary = requests.get(f"{SUPABASE_URL}/rest/v1/user_summary?user_id=eq.9741f74f-c083-4832-b54b-4662cd8b0cc8", headers=HEADERS)
    data = res_summary.json()
    if data:
        st.metric(label="Toplam Birikimim", value=f"{data[0]['total_saved']} TL")
except:
    st.write("Veri panelini yüklerken sorun oluştu.")

# --- HAVUZLAR VE KURA ---
st.subheader("Aktif Havuzlar")
res = requests.get(f"{SUPABASE_URL}/rest/v1/pools", headers=HEADERS)
pools = res.json()

for pool in pools:
    st.write(f"**{pool['pool_name']}** - Aylık: {pool['monthly_amount']} TL")
    if st.button(f"Havuza Katıl: {pool['pool_name']}", key=f"katil_{pool['pool_name']}"):
        katilim_data = {
            "user_id": "9741f74f-c083-4832-b54b-4662cd8b0cc8",
            "transaction_type": "HAVUZ_KATILIM",
            "amount": pool['monthly_amount']
        }
        requests.post(f"{SUPABASE_URL}/rest/v1/ledger", headers=HEADERS, json=katilim_data)
        st.rerun()

# --- KURA MOTORU ---
st.divider()
st.subheader("🎲 Kura Çekilişi")
if st.button("Kura Çekilişini Başlat"):
    res = requests.post(f"{SUPABASE_URL}/rest/v1/rpc/run_draw", headers=HEADERS, json={"target_pool_id": 1})
    if res.status_code == 200:
        st.success(f"Kazanan belirlendi! ID: {res.json()}")
        st.balloons()
    else:
        st.error("Kura çekilemedi, katılımcı kontrol et.")
