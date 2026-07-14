import streamlit as st
import requests

# ... (API bağlantı ayarların aynı kalıyor) ...

def get_pools():
    url = f"{SUPABASE_URL}/rest/v1/pools"
    res = requests.get(url, headers=HEADERS)
    return res.json()

if "onboarding_step" not in st.session_state: st.session_state.onboarding_step = 1

# --- HAVUZ GİRİŞ EKRANI ---
if st.session_state.onboarding_step == 3:
    st.subheader("Aktif Tasarruf Havuzları")
    pools = get_pools()
    
    for pool in pools:
        st.write(f"**{pool['pool_name']}**")
        st.write(f"Aylık Katılım: {pool['monthly_amount']} TL")
        if st.button(f"Bu Havuza Katıl ({pool['pool_name']})"):
            # Havuz bağlantısını Ledger'a yazıyoruz
            db_save_ledger(st.session_state.db_user_id, "HAVUZA_KATILIM", pool['monthly_amount'], "JOIN_POOL_TX")
            st.success("Tebrikler! Havuza başarıyla katıldınız.")
            st.session_state.onboarding_step = 4
            st.rerun()
