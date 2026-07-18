import streamlit as st
import json
import random
import pandas as pd
import requests
import time
import plotly.graph_objects as go

# Sayfa Ayarları
st.set_page_config(page_title="Susu Global | Enterprise WealthTech", page_icon="🏦", layout="wide", initial_sidebar_state="expanded")

# ==========================================
# 🎨 ÖZEL CSS & STİL (Hatalar Giderildi)
# ==========================================
st.markdown("""
<style>
    div[data-testid="stMetricValue"] { font-size: 24px !important; font-weight: 700 !important; color: #111827 !important; }
    div[data-testid="stMetricLabel"] { font-size: 13px !important; font-weight: 600 !important; color: #6b7280 !important; }
    .stTabs [data-baseweb="tab-list"] { gap: 10px; border-bottom: 2px solid #e5e7eb; }
    .stTabs [data-baseweb="tab"] { font-weight: 600; color: #4b5563; }
    .stTabs [aria-selected="true"] { color: #16a34a !important; border-bottom: 3px solid #16a34a !important; }
</style>
""", unsafe_allow_html=True)

# Supabase Ayarları
SUPABASE_URL = st.secrets.get("SUPABASE_URL")
SUPABASE_KEY = st.secrets.get("SUPABASE_KEY")

def get_clean_base_url():
    if not SUPABASE_URL: return ""
    url = SUPABASE_URL.strip()
    if url.endswith("/"): url = url[:-1]
    if "/rest/v1" in url: url = url.replace("/rest/v1", ""); url = url.rstrip("/")
    return url

# ==========================================
# 🌍 VERİ TABANI & MODELLER
# ==========================================
def load_global_state_from_db():
    base_url = get_clean_base_url()
    if not base_url or not SUPABASE_KEY: return None
    headers = {"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}"}
    try:
        res = requests.get(f"{base_url}/rest/v1/susu_state?id=eq.US-GLOBAL-01", headers=headers)
        if res.status_code == 200 and res.json() and "pools" in res.json()[0]["data"]: return res.json()[0]["data"]
        else:
            default = {"pools": {"Global-Alpha": {"pool_id": "Global-Alpha", "pool_name": "🌐 Global USD Alpha Pool", "currency": "USD", "monthly_contribution": 1000, "total_months": 4, "current_month": 1, "total_yield": 0.0, "users": [], "history": []}}}
            save_global_state_to_db(default); return default
    except: return None

def save_global_state_to_db(global_state_dict):
    base_url = get_clean_base_url()
    if not base_url or not SUPABASE_KEY: return False
    headers = {"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}", "Content-Type": "application/json", "Prefer": "resolution=merge-duplicates"}
    try: res = requests.post(f"{base_url}/rest/v1/susu_state", headers=headers, json=[{"id": "US-GLOBAL-01", "data": global_state_dict}]); return res.status_code in [200, 201]
    except: return False

class SusuUser:
    def __init__(self, user_id, name, country, passport_verified, credit_score, has_paid=False, has_received=False, trust_score=50):
        self.user_id = user_id; self.name = name; self.country = country; self.passport_verified = passport_verified; self.credit_score = credit_score; self.has_paid = has_paid; self.has_received = has_received; self.trust_score = trust_score
    def to_dict(self): return {"user_id": self.user_id, "name": self.name, "country": self.country, "passport_verified": self.passport_verified, "credit_score": self.credit_score, "has_paid": self.has_paid, "has_received": self.has_received, "trust_score": self.trust_score}

global_state = load_global_state_from_db()
if not global_state: global_state = {"pools": {}}
pools_dict = global_state["pools"]

# ==========================================
# 🎛️ YAN MENÜ (Sidebar)
# ==========================================
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2953/2953363.png", width=50)
    st.markdown("### Susu Global")
    st.caption("WealthTech OS | v11.0 Terminal")
    st.divider()
    
    pool_options = {p_id: p_data["pool_name"] for p_id, p_data in pools_dict.items()}
    selected_pool_id = st.selectbox("📂 Aktif Portföy", options=list(pool_options.keys()), format_func=lambda x: pool_options[x])
    
    p_data = pools_dict[selected_pool_id]
    active_users = [SusuUser(**u) for u in p_data["users"]]
    current_month = p_data["current_month"]
    total_months = p_data["total_months"]
    is_completed = current_month > total_months

    st.divider()
    st.markdown("#### 👤 Yeni Müşteri Katılımı")
    with st.form("onboard_form", clear_on_submit=True):
        name = st.text_input("Ad Soyad")
        country = st.selectbox("Bağlı Bölge (Node)", ["TR-Istanbul", "US-NewYork", "UK-London", "DE-Berlin"])
        if st.form_submit_button("Doğrula ve Ağa Ekle"):
            if len(active_users) >= total_months: st.error("Maksimum kapasiteye ulaşıldı.")
            else:
                new_user = SusuUser(len(active_users) + 1, name, country, True, 720, trust_score=random.randint(60, 95))
                p_data["users"].append(new_user.to_dict()); save_global_state_to_db(global_state); st.rerun()

# ==========================================
# 🌐 ÜST BAR: CANLI PİYASA TERMİNALİ
# ==========================================
ticker_col1, ticker_col2, ticker_col3, ticker_col4 = st.columns(4)
with ticker_col1: st.metric("BTC/USD", "64,230.50", "1.2%", delta_color="normal")
with ticker_col2: st.metric("S&P 500 (SPX)", "5,120.14", "0.8%", delta_color="normal")
with ticker_col3: st.metric("Global Escrow TVL", f"${sum(h['payout'] for h in p_data['history']):,.0f}", "Aktif Havuz", delta_color="off")
with ticker_col4: st.metric("Ağ Durumu", "Operasyonel", "Susu-Node-01", delta_color="normal")
st.divider()

# ==========================================
# 📊 ANA YÖNETİM PANELİ (Dashboard)
# ==========================================
col_title, col_status = st.columns([3, 1])
with col_title:
    st.markdown(f"<h2>🏦 {p_data['pool_name']}</h2>", unsafe_allow_html=True)
with col_status:
    if is_completed:
        st.success("✅ Döngü Tamamlandı")
    else:
        st.info(f"⏳ Döngü {current_month} / {total_months}")

# Ana Metrikler
with st.container(border=True):
    mc1, mc2, mc3, mc4 = st.columns(4)
    with mc1: st.metric("Aylık Katılım", f"{p_data['monthly_contribution']:,} {p_data['currency']}")
    with mc2: st.metric("Bileşik Getiri", f"+{p_data.get('total_yield', 0):,.2f} {p_data['currency']}")
    with mc3: st.metric("Havuz Kapasitesi", f"{len(active_users)} / {total_months} Kişi")
    with mc4: st.metric("Ortalama Güven Skoru", f"{int(sum(u.trust_score for u in active_users)/len(active_users)) if active_users else 0} ⭐")

# Ana Sekmeler
tab1, tab2, tab3 = st.tabs(["⚡ Akıllı Sözleşme (Operasyon)", "🚀 5 Yıllık Özgürlük Projeksiyonu", "📜 Yasal Uyum (AML/KYC)"])

with tab1:
    col_left, col_right = st.columns([6, 4])
    
    with col_left:
        st.markdown("### 👥 Ağa Bağlı Katılımcılar")
        if not active_users: 
            st.warning("Havuz boş. İşleme başlamak için sol menüden müşteri ekleyin.")
        else:
            df = pd.DataFrame([{"Müşteri": u.name, "Bölge": u.country, "Trust Score": f"{u.trust_score}", "Ödeme": "✅" if u.has_paid else "⏳", "Hakediş": "🏦 Alındı" if u.has_received else "➖ Bekliyor"} for u in active_users])
            st.dataframe(df, use_container_width=True, hide_index=True)
            
            if not is_completed:
                with st.container(border=True):
                    st.markdown("#### 💳 Tahsilat Terminali")
                    pay_cols = st.columns(len(active_users))
                    for idx, u in enumerate(active_users):
                        with pay_cols[idx]:
                            if u.has_paid: st.success(f"{u.name}\n(Ödendi)")
                            else:
                                if st.button(f"Tahsil Et:\n{u.name}", key=f"pay_{u.user_id}", use_container_width=True):
                                    p_data["users"][idx]["has_paid"] = True; save_global_state_to_db(global_state); st.rerun()

                # Dağıtım Motoru
                if len(active_users) >= total_months and all(u.has_paid for u in active_users):
                    st.info("ℹ️ Tüm fonlar emanet kasasına (escrow) alındı.")
                    if st.button("🚀 FONU VE TEMETTÜYÜ DAĞIT", type="primary", use_container_width=True):
                        eligible_indices = [i for i, u in enumerate(active_users) if not u.has_received]
                        if eligible_indices:
                            with st.spinner("Piyasa Getirileri Hesaplanıyor ve Dağıtılıyor..."):
                                time.sleep(1.5)
                                winner_idx = random.choice(eligible_indices)
                                collected = p_data["monthly_contribution"] * total_months
                                generated_yield = collected * random.uniform(0.01, 0.03) # %1 - %3 getiri simülasyonu
                                
                                p_data["total_yield"] = p_data.get("total_yield", 0) + generated_yield
                                fee = collected * 0.01; payout = collected - fee
                                
                                p_data["users"][winner_idx]["has_received"] = True
                                p_data["users"][winner_idx]["trust_score"] = min(100, p_data["users"][winner_idx]["trust_score"] + 10)
                                
                                p_data["history"].append({"month": current_month, "winner": active_users[winner_idx].name, "payout": payout, "yield": generated_yield, "fee": fee})
                                p_data["current_month"] += 1
                                for u in p_data["users"]: u["has_paid"] = False
                                
                                save_global_state_to_db(global_state); st.rerun()

    with col_right:
        st.markdown("### 🛡️ İşlem Logları (Ledger)")
        with st.container(height=450, border=True):
            if not p_data["history"]: st.caption("Henüz finansal işlem yok.")
            for event in reversed(p_data["history"]):
                st.markdown(f"**Döngü {event['month']}** | Kazanan: **{event['winner']}**")
                st.markdown(f"Ana Para: **{event['payout']:,}** USD | Temettü: **+{event.get('yield', 0):,.2f}** USD")
                st.caption("✅ Stablecoin altyapısı ile transfer edildi.")
                st.divider()

with tab2:
    st.markdown("### 🎯 Finansal Özgürlük Vizyonu (5 Yıllık Simülasyon)")
    st.write("Susu Global sadece bir birikim aracı değil, aynı zamanda finansal hedeflere ulaşma motorudur. Aşağıdaki grafik, düzenli havuz katılımlarının ve elde edilen bileşik getirilerin 5 yıl (60 ay) içinde yaratacağı portföy etkisini göstermektedir.")
    
    # 5 Yıllık Büyüme Simülasyonu
    months_sim = list(range(1, 61))
    monthly_base = p_data["monthly_contribution"]
    base_capital = [monthly_base * m for m in months_sim]
    compound_growth = [monthly_base * m * (1.008 ** m) for m in months_sim] # Aylık %0.8 büyüme varsayımı

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=months_sim, y=base_capital, mode='lines', name='Sadece Birikim (Yastık Altı)', line=dict(color='#9ca3af', dash='dash')))
    fig.add_trace(go.Scatter(x=months_sim, y=compound_growth, mode='lines', name='Susu Global Bileşik Getiri', line=dict(color='#3b82f6', width=3), fill='tonexty', fillcolor='rgba(59, 130, 246, 0.1)'))
    
    fig.update_layout(xaxis_title="Geçen Süre (Ay)", yaxis_title="Portföy Değeri (USD)", hovermode="x unified", plot_bgcolor='rgba(0,0,0,0)', margin=dict(l=0, r=0, t=30, b=0))
    st.plotly_chart(fig, use_container_width=True)

with tab3:
    st.markdown("### ⚖️ Uluslararası Uyum Raporları")
    with st.container(border=True):
        st.write("Tüm fon transferleri zincir üstü (on-chain) olarak denetlenmektedir.")
        if is_completed: st.success("Bu havuz için tüm AML (Kara Para Aklama) taramaları başarıyla tamamlandı.")
        else: st.info("Tarama işlemlerinin tamamlanması için havuz döngüsünün bitmesi bekleniyor.")
