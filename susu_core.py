import streamlit as st
import requests

st.title("Bağlantı Testi")
SUPABASE_URL = st.secrets.get("SUPABASE_URL")
SUPABASE_KEY = st.secrets.get("SUPABASE_KEY")

if st.button("Veritabanına Bağlanmayı Dene"):
    st.write(f"URL: {SUPABASE_URL}")
    url = f"{SUPABASE_URL}/rest/v1/users"
    headers = {"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}"}
    
    try:
        response = requests.get(url, headers=headers)
        st.write(f"Durum Kodu: {response.status_code}")
        st.write(f"Yanıt: {response.text}")
    except Exception as e:
        st.error(f"Hata: {e}")
