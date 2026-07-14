# --- GÜVEN KARNESİ ---
st.subheader("Güven Karnem")
# Kullanıcının skorunu çek
res_score = requests.get(f"{SUPABASE_URL}/rest/v1/users?id=eq.9741f74f-c083-4832-b54b-4662cd8b0cc8", headers=HEADERS)
user_data = res_score.json()

if user_data:
    skor = user_data[0]['trust_score']
    st.progress(skor / 200) # 200 üzerinden bir bar gösteriyoruz
    st.write(f"Güven Puanın: **{skor} / 200**")
    if skor > 150:
        st.success("Premium kullanıcı! Yüksek limitli havuzlara katılabilirsin.")
