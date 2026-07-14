# --- KURA ÇEKİLİŞ MOTORU ---
st.subheader("🎲 Kura Çekilişi")
if st.button("Kura Çekilişini Başlat"):
    # SQL fonksiyonumuzu çağırıyoruz
    res = requests.post(f"{SUPABASE_URL}/rest/v1/rpc/run_draw", 
                        headers=HEADERS, 
                        json={"target_pool_id": 1})
    
    if res.status_code == 200:
        kazanan = res.json()[0]['winner_user_id']
        st.balloons()
        st.success(f"Kazanan Kullanıcı: {kazanan}")
        # Burada kazananı Ledger'a işleyeceğiz...
    else:
        st.error("Kura çekilemedi, yeterli katılımcı olmayabilir.")
