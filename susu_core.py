# --- İŞLEM GEÇMİŞİ (LEDGER) ---
st.divider()
st.subheader("İşlem Geçmişim")
res_ledger = requests.get(f"{SUPABASE_URL}/rest/v1/ledger?user_id=eq.9741f74f-c083-4832-b54b-4662cd8b0cc8", headers=HEADERS)
ledger_data = res_ledger.json()

if ledger_data:
    for tx in ledger_data:
        st.write(f"- {tx['transaction_type']}: **{tx['amount']} TL**")
else:
    st.write("Henüz bir işlem hareketin yok.")
