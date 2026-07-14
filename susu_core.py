import streamlit as st
import requests

SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
HEADERS = {"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}"}

st.title("Susu Global")

# Verileri çek
res = requests.get(f"{SUPABASE_URL}/rest/v1/pools", headers=HEADERS)
pools = res.json()

st.subheader("Aktif Havuzlar")

for pool in pools:
    st.write(f"**{pool['pool_name']}** - Aylık: {pool['monthly_amount']} TL")
    
    # Katılım Butonu
    if st.button(f"Havuza Katıl: {pool['pool_name']}", key=pool['pool_name']):
        # Veritabanına katılımı yaz
        katilim_data = {
            "user_id": "9741f74f-c083-4832-b54b-4662cd8b0cc8", # Senin ID'n
            "transaction_type": "HAVUZ_KATILIM",
            "amount": pool['monthly_amount']
        }
        requests.post(f"{SUPABASE_URL}/rest/v1/ledger", headers=HEADERS, json=katilim_data)
        st.success(f"Tebrikler! {pool['pool_name']} havuzuna dahil oldun.")
