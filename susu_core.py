import streamlit as st
import requests
import time

# --- 1. AYARLAR VE URL GÜVENLİK KİLİDİ ---
SUPABASE_URL = st.secrets["SUPABASE_URL"].rstrip('/')
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
HEADERS = {"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}"}

st.title("Susu Global - FinTech Platform")

# --- 2. GÜVEN KARNESİ (RİSK MOTORU) ---
st.subheader("Güven Karnem")
try:
    res_score = requests.get(f"{SUPABASE_URL}/rest/v1/users?id=eq.9741f74f-c083-4832-b54b-4662cd8b0cc8", headers=HEADERS)
    if res_score.status_code == 200 and res_score.json():
        skor = res_score.json()[0].get('trust_score', 100)
        st.progress(min(skor / 200, 1.0))
        st.write(f"Güven Puanın: **{skor} / 200**")
    else:
        st.write("Güven karnesi verisi şu an çekilemiyor.")
except Exception as e:
    st.error("API Bağlantı Hatası: Güven motoru yanıt vermiyor.")

# --- 3. YÖNETİCİ PANELİ: RİSK VE AĞ SİMÜLASYONU ---
st.divider()
st.subheader("⚙️ Sistem Motoru Test Paneli")
col1, col2, col3 = st.columns(3)

with col1:
    if st.button("✅ Ödül (+10 Puan)"):
        payload = {"target_user_id": "9741f74f-c083-4832-b54b-4662cd8b0cc8", "change_amount": 10}
        requests.post(f"{SUPABASE_URL}/rest/v1/rpc/update_trust_score", headers=HEADERS, json=payload)
        st.rerun()

with col2:
    if st.button("❌ Ceza (-20 Puan)"):
        payload = {"target_user_id": "9741f74f-c083-4832-b54b-4662cd8b0cc8", "change_amount": -20}
        requests.post(f"{SUPABASE_URL}/rest/v1/rpc/update_trust_score", headers=HEADERS, json=payload)
        st.rerun()

with col3:
    if st.button("👥 Havuza 5 Kullanıcı Ekle"):
        bot_ids = ["Yatirimci-A", "Yatirimci-B", "Yatirimci-C", "Yatirimci-D", "Yatirimci-E"]
        for bot in bot_ids:
            bot_data = {
                "user_id": bot,
                "transaction_type": "HAVUZ_KATILIM",
                "amount": 20000
            }
            requests.post(f"{SUPABASE_URL}/rest/v1/ledger", headers=HEADERS, json=bot_data)
        st.success("Ağ hacmi büyüdü! Havuza 5 yeni yatırımcı girdi.")

# --- 4. HAVUZLAR VE KATILIM ---
st.divider()
st.subheader("Aktif Havuzlar")
try:
    res_pools = requests.get(f"{SUPABASE_URL}/rest/v1/pools", headers=HEADERS)
    pools = res_pools.json()
    for pool in pools:
        st.write(f"**{pool['pool_name']}** - Aylık: {pool['monthly_amount']} TL")
        if st.button(f"Havuza Katıl: {pool['pool_name']}", key=f"join_{pool['id']}"):
            katilim_data = {
                "user_id": "9741f74f-c083-4832-b54b-4662cd8b0cc8",
                "transaction_type": "HAVUZ_KATILIM",
                "amount": pool['monthly_amount']
            }
            requests.post(f"{SUPABASE_URL}/rest/v1/ledger", headers=HEADERS, json=katilim_data)
            st.success("İşlem başarıyla kaydedildi!")
            st.rerun()
except:
    st.warning("Havuzlar yüklenemedi. URL veya bağlantı kontrol edilmeli.")

# --- 5. AKILLI KURA VE ÖDEME MOTORU ---
st.divider()
st.subheader("🎲 Otonom Kura Motoru")
if st.button("Kura Çekilişini Başlat"):
    with st.spinner("Şifreli algoritmalarla rastgele kazanan belirleniyor..."):
        time.sleep(1.5) # Gerçekçilik katmak için kısa bir bekleme efekti
        res_draw = requests.post(f"{SUPABASE_URL}/rest/v1/rpc/run_draw", headers=HEADERS, json={"target_pool_id": 1})
        
        if res_draw.status_code == 200 and res_draw.json():
            kazanan_id = res_draw.json()[0]['winner_user_id']
            st.balloons()
            st.success(f"Kura başarıyla çekildi! Kazanan: **{kazanan_id}**")
            
            odeme_data = {
                "user_id": kazanan_id,
                "transaction_type": "KURA_KAZANCI",
                "amount": 120000 # 6 kişi * 20.000 TL
            }
            requests.post(f"{SUPABASE_URL}/rest/v1/ledger", headers=HEADERS, json=odeme_data)
        else:
            st.error("Kura motoru çalışamadı.")

# --- 6. İŞLEM GEÇMİŞİ (LEDGER) ---
st.divider()
st.subheader("İşlem Geçmişim (Şeffaflık Defteri)")
try:
    res_ledger = requests.get(f"{SUPABASE_URL}/rest/v1/ledger?user_id=eq.9741f74f-c083-4832-b54b-4662cd8b0cc8", headers=HEADERS)
    if res_ledger.status_code == 200:
        ledger_data = res_ledger.json()
        if ledger_data:
            for tx in ledger_data:
                st.write(f"- {tx['transaction_type']}: **{tx['amount']} TL**")
        else:
            st.write("Henüz bir işlem hareketin yok.")
except:
    st.write("İşlem geçmişi bağlantısında sorun yaşandı.")
