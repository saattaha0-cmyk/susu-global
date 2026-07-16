import streamlit as st
import requests

# --- 1. AYARLAR VE URL GÜVENLİK KİLİDİ ---
# .rstrip('/') ile URL'nin sonundaki gereksiz işaretleri temizleyerek URL/API hatalarını önlüyoruz.
SUPABASE_URL = st.secrets["SUPABASE_URL"].rstrip('/')
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
HEADERS = {"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}"}

st.title("Susu Global - FinTech Platform")

# --- 2. GÜVEN KARNESİ (RISK MOTORU) ---
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

# --- 3. HAVUZLAR VE KATILIM ---
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

# --- 4. AKILLI KURA VE ÖDEME MOTORU ---
st.divider()
st.subheader("🎲 Otonom Kura ve Dağıtım Motoru")
if st.button("Kura Çekilişini Başlat"):
    # SQL'deki kura fonksiyonunu tetikle
    res_draw = requests.post(f"{SUPABASE_URL}/rest/v1/rpc/run_draw", headers=HEADERS, json={"target_pool_id": 1})
    
    if res_draw.status_code == 200 and res_draw.json():
        kazanan_id = res_draw.json()[0]['winner_user_id']
        st.balloons()
        st.success("Kura başarıyla çekildi!")
        
        # 4.1. Kazananın parası otomatik olarak Ledger'a yatırılıyor
        odeme_data = {
            "user_id": kazanan_id,
            "transaction_type": "KURA_KAZANCI",
            "amount": 100000 # Örnek havuz toplam ödülü
        }
        requests.post(f"{SUPABASE_URL}/rest/v1/ledger", headers=HEADERS, json=odeme_data)
        st.info("Kazanılan tutar başarıyla kullanıcının hesabına (İşlem Geçmişi'ne) aktarıldı.")
    else:
        st.error("Kura motoru çalışamadı (Yeterli katılımcı olmayabilir).")

# --- 5. İŞLEM GEÇMİŞİ (LEDGER) ---
st.divider()
st.subheader("İşlem Geçmişim")
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
