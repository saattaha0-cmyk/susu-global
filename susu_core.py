import streamlit as st
import requests

# --- AYARLAR ---
SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
HEADERS = {"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}"}

st.title("Susu Global")

# --- PANEL (DASHBOARD) ---
st.subheader("Finansal Durumum")
try:
    res_summary = requests.get(f"{SUPABASE_URL}/rest/v1/user_summary?user_id=eq.9741f74f-c083-4832-b54b-4662cd8b0cc8", headers=HEADERS)
    data = res_summary.json()
    if data:
        toplam = data[0]['total_saved']
        st.metric(label="Toplam Birikimim", value=f"{toplam} TL")
    else:
        st.write("Henüz bir işlem yapmadın, ilk havuzuna katıl!")
except:
    st.write("Veri panelini yüklerken bir sorun oluştu.")

# --- HAVUZLAR ---
res = requests.get(f"{SUPABASE_URL}/rest/v1/pools", headers=HEADERS)
pools = res.json()

st.subheader("Aktif Havuzlar")
for pool in pools:
    st.write(f"**{pool['pool_name']}** - Aylık: {pool['monthly_amount']} TL")
    if st.button(f"Havuza Katıl: {pool['pool_name']}", key=pool['pool_name']):
        katilim_data = {
            "user_id": "9741f74f-c083-4832-b54b-4662cd8b0cc8",
            "transaction_type": "HAVUZ_KATILIM",
            "amount": pool['monthly_amount']
        }
        requests.post(f"{SUPABASE_URL}/rest/v1/ledger", headers=HEADERS, json=katilim_data)
        st.success(f"Tebrikler! {pool['pool_name']} havuzuna dahil oldun.")
        st.rerun()
