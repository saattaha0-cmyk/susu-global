import streamlit as st
import requests

SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
HEADERS = {"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}"}

st.title("Susu Global")

# Havuzları çek
res = requests.get(f"{SUPABASE_URL}/rest/v1/pools", headers=HEADERS)
pools = res.json()

st.subheader("Aktif Havuzlar")
for pool in pools:
    st.write(f"Havuz: {pool['pool_name']} - {pool['monthly_amount']} TL")
