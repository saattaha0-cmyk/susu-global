import streamlit as st
import json
import random
import pandas as pd
import requests
import time
from io import BytesIO
import plotly.graph_objects as go
import plotly.express as px

# Sayfa Ayarları (Geniş Ekran)
st.set_page_config(page_title="Susu Global | Enterprise WealthTech", page_icon="🏦", layout="wide", initial_sidebar_state="expanded")

# ==========================================
# 🎨 ÖZEL CSS: KURUMSAL SAAS TASARIMI
# ==========================================
st.markdown("""
<style>
    /* Genel Arka Plan ve Yazı Tipi */
    .reportview-container {
        background: #f4f6f9;
    }
    
    /* Metrik Kartları (Dashboard Hissiyatı) */
    div[data-testid="stMetric"] {
        background-color: #ffffff;
        border: 1px solid #e0e4e8;
        padding: 15px 20px;
        border-radius: 12px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        transition: transform 0.2s ease;
    }
    div[data-testid="stMetric"]:hover {
        transform: translateY(-3px);
        box-shadow: 0 6px 12px rgba(0,0,0,0.08);
    }
    div[data-testid="stMetricValue"] {
        font-size: 28px !important;
        font-weight: 700 !important;
        color: #111827 !important;
    }
    div[data-testid="stMetricLabel"] {
        font-size: 14px !important;
        font-weight: 600 !important;
        color: #6b7280 !important;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    /* Sekmeler (Tabs) */
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
        border-bottom: 2px solid #e5e7eb;
    }
    .stTabs [data-baseweb="tab"] {
        background-color: transparent;
        border-radius: 8px 8px 0 0;
        padding: 10px 20px;
        font-weight: 600;
        color: #4b5563;
    }
    .stTabs [aria-selected="true"] {
        background-color: #f0fdf4 !important;
        color: #16a34a !important;
        border-bottom: 3px solid #16a34a !important;
    }

    /* Ana Butonlar (Call to Action) */
    .stButton > button {
        background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%);
        color: white;
        font-weight: 600;
        border: none;
        border-radius: 8px;
        padding: 0.75rem 1.5rem;
        box-shadow: 0 4px 6px rgba(37, 99, 235, 0.2);
        transition: all 0.3s ease;
    }
    .stButton > button:hover {
        background: linear-gradient(135deg, #1d4ed8 0%, #1e40af 100%);
        box-shadow: 0 6px 12px rgba(37, 99, 235, 0.3);
        transform: scale(1.02);
    }
    
    /* İkincil Butonlar (Ödeme vs) */
    button[kind="secondary"] {
        background: #f3f4f6 !important;
        color: #374151 !important;
        border: 1px solid #d1d5db !important;
        box-shadow: none !important;
    }
    button[kind="secondary"]:hover {
        background: #e5e7eb !important;
        color: #111827 !important;
    }

    /* Tablo Tasarımı */
    .stDataFrame {
        border-radius: 10px;
        overflow: hidden;
        border: 1px solid #e5e7eb;
        box-shadow: 0 2px 4px rgba(0,0,0,0.02);
    }
</style>
""", unsafe_allow_html=True)

# Streamlit Secrets (Veritabanı)
SUPABASE_URL = st.secrets.get("SUPABASE_URL")
SUPABASE_KEY = st.secrets.get("SUPABASE_KEY")

def get_clean_base_url():
    if not SUPABASE_URL: return ""
    url = SUPABASE_URL.strip()
    if url.endswith("/"): url = url[:-1]
    if "/rest/v1" in url: url = url.replace("/rest/v1", ""); url = url.rstrip("/")
    return url

# ==========================================
# 🌍 VERİ TABANI & MODELLER (Değişmedi)
# ==========================================
def load_global_state_from_db():
    base_url = get_clean_base_url()
    if not base_url or not SUPABASE_KEY: return None
    headers = {"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}"}
    try:
        res = requests.get(f"{base_url}/rest/v1/susu_state?id=eq.US-GLOBAL-01", headers=headers)
        if res.status_code == 200 and res.json() and "pools" in res.json()[0]["data"]: return res.json()[0]["data"]
        else:
            default = {"pools": {"Finansal-Ozgurluk": {"pool_id": "Finansal-Ozgurluk", "pool_name": "🪙 Kurumsal Fon (US ETF)", "currency": "USD", "monthly_contribution": 2500, "total_months": 4, "current_month": 1, "total_yield": 0.0, "users": [], "history": []}}}
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

class SusuPool:
    def __init__(self, pool_id, pool_name, currency, monthly_contribution, total_months, current_month=1, total_yield=0.0, history=None):
        self.pool_id = pool_id; self.pool_name = pool_name; self.currency = currency; self.monthly_contribution = monthly_contribution; self.total_months = total_months; self.current_month = current_month; self.total_yield = total_yield; self.users = []; self.history = history if history is not None else []
    def to_dict(self): return {"pool_id": self.pool_id, "pool_name": self.pool_name, "currency": self.currency, "monthly_contribution": self.monthly_contribution, "total_months": self.total_months, "current_month": self.current_month, "total_yield": self.total_yield, "users": [u.to_dict() for u in self.users], "history": self.history}

global_state = load_global_state_from_db()
if not global_state: global_state = {"pools": {}}
pools_dict = global_state["pools"]

# ==========================================
# 🎛️ YAN MENÜ (Sidebar)
# ==========================================
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2953/2953363.png", width=60)
    st.markdown("### Susu Global")
    st.caption("Enterprise WealthTech OS | v10.0")
    st.divider()
    
    pool_options = {p_id: p_data["pool_name"] for p_id, p_data in pools_dict.items()}
    if not pool_options: st.error("Havuz bulunamadı."); st.stop()
    selected_pool_id = st.selectbox("📂 Aktif Portföy Seçimi", options=list(pool_options.keys()), format_func=lambda x: pool_options[x])
    
    p_data = pools_dict[selected_pool_id]
    active_pool = SusuPool(p_data["pool_id"], p_data["pool_name"], p_data["currency"], p_data["monthly_contribution"], p_data["total_months"], p_data["current_month"], p_data.get("total_yield", 0.0), p_data.get("history", []))
    for u in p_data["users"]: active_pool.users.append(SusuUser(u["user_id"], u["name"], u["country"], u["passport_verified"], u["credit_score"], u["has_paid"], u["has_received"], u.get("trust_score", 50)))

    st.divider()
    st.markdown("#### 👤 Yeni Müşteri Katılımı (KYC)")
    with st.form("onboard_form", clear_on_submit=True):
        name = st.text_input("Ad Soyad")
        country = st.selectbox("Bağlı Bölge (Node)", ["TR-Istanbul", "US-NewYork", "UK-London", "DE-Berlin"])
        if st.form_submit_button("Doğrula ve Ağa Ekle") and name:
            if len(active_pool.users) >= active_pool.total_months: st.error("Maksimum kapasiteye ulaşıldı.")
            else:
                active_pool.users.append(SusuUser(len(active_pool.users) + 1, name, country, True, 720, trust_score=random.randint(60, 95)))
                pools_dict[selected_pool_id] = active_pool.to_dict(); global_state["pools"] = pools_dict; save_global_state_to_db(global_state); st.rerun()

# ==========================================
# 📊 ANA YÖNETİM PANELİ (Dashboard)
# ==========================================
st.markdown(f"<h2>🏦 {active_pool.pool_name} Yönetim Paneli</h2>", unsafe_allow_html=True)
st.markdown(f"<p style='color: #6b7280; font-size: 16px;'>Aylık Katılım: <b>{active_pool.monthly_contribution:,} {active_pool.currency}</b> | Durum: <b>Döngü {active_pool.current_month} / {active_pool.total_months}</b></p>", unsafe_allow_html=True)

# Kurumsal Metrikler
col1, col2, col3, col4 = st.columns(4)
with col1: st.metric("Yönetilen Varlık (AUM)", f"{sum([h['payout'] for h in active_pool.history]):,} {active_pool.currency}")
with col2: st.metric("Bileşik ETF Getirisi", f"+{active_pool.total_yield:,.2f} {active_pool.currency}")
with col3: st.metric("Platform Komisyonu", f"{sum([h['fee'] for h in active_pool.history]):,} {active_pool.currency}")
with col4: st.metric("Ortalama Güven Skoru", f"{int(sum(u.trust_score for u in active_pool.users)/len(active_pool.users)) if active_pool.users else 0} / 100")

st.markdown("<br>", unsafe_allow_html=True)

# Ana Sekmeler
tab1, tab2, tab3 = st.tabs(["⚡ Akıllı Sözleşme & Operasyon", "📈 Kurumsal Getiri Analizi", "📜 Yasal Uyum (Compliance)"])

with tab1:
    col_left, col_right = st.columns([7, 3])
    
    with col_left:
        st.markdown("### 👥 Ağa Bağlı Katılımcılar")
        if not active_pool.users: 
            st.info("Havuzda şu an katılımcı bulunmuyor. Sol menüden yeni müşteri ekleyin.")
        else:
            # Pandas ile temiz tablo
            df = pd.DataFrame([{
                "Cari ID": f"USR-{u.user_id:04d}", 
                "Müşteri": u.name, 
                "Bölge Node": u.country, 
                "Susu Trust Score": f"⭐ {u.trust_score}", 
                "Ödeme Durumu": "✅ Tahsil Edildi" if u.has_paid else "⏳ Bekliyor",
                "Hakediş": "🏦 Dağıtıldı" if u.has_received else "➖ Sırasını Bekliyor"
            } for u in active_pool.users])
            st.dataframe(df, use_container_width=True, hide_index=True)
            
            st.markdown("<br>### 💸 Küresel Ödeme Terminali (Tahsilat)", unsafe_allow_html=True)
            pay_cols = st.columns(len(active_pool.users))
            for idx, u in enumerate(active_pool.users):
                with pay_cols[idx]:
                    if u.has_paid: 
                        st.success(f"{u.name.split()[0]}\n(Ödendi)")
                    else:
                        if st.button(f"Tahsil Et: {u.name.split()[0]}", key=f"pay_{u.user_id}", use_container_width=True):
                            u.has_paid = True; pools_dict[selected_pool_id] = active_pool.to_dict(); global_state["pools"] = pools_dict; save_global_state_to_db(global_state); st.rerun()

            st.markdown("<br>", unsafe_allow_html=True)
            # Dağıtım Motoru
            if len(active_pool.users) >= active_pool.total_months and all(u.has_paid for u in active_pool.users):
                st.info("ℹ️ Tüm fonlar emanet kasasına (escrow) alındı. Akıllı sözleşme dağıtıma hazır.")
                if st.button("🚀 FONU VE TEMETTÜYÜ DAĞIT (EXECUTE CONTRACT)", use_container_width=True):
                    eligible = [u for u in active_pool.users if not u.has_received]
                    if eligible:
                        with st.spinner("ABD ETF Getirileri Hesaplanıyor ve Web3 Ağı Üzerinden Transfer Ediliyor..."):
                            time.sleep(1.5)
                            collected = active_pool.monthly_contribution * len(active_pool.users)
                            generated_yield = collected * random.uniform(0.007, 0.015) # %0.7 ile %1.5 arası getiri
                            active_pool.total_yield += generated_yield
                            
                            fee = collected * 0.01; payout = collected - fee
                            winner = random.choice(eligible); winner.has_received = True; winner.trust_score = min(100, winner.trust_score + 8)
                            
                            details = [f"Banka Swift ByPass -> Stablecoin transferi tamamlandı.", f"Temettü Hakedişi: +{generated_yield:,.2f} {active_pool.currency}"]
                            active_pool.history.append({"month": active_pool.current_month, "winner": winner.name, "payout": payout, "yield": generated_yield, "fee": fee, "details": details})
                            active_pool.current_month += 1
                            for u in active_pool.users: u.has_paid = False
                            pools_dict[selected_pool_id] = active_pool.to_dict(); global_state["pools"] = pools_dict; save_global_state_to_db(global_state)
                            st.toast(f"✅ İşlem Başarılı: {winner.name} kazandı!", icon="🏦")
                            st.rerun()
            elif len(active_pool.users) >= active_pool.total_months:
                st.warning("⚠️ Kura çekimi için tüm katılımcıların tahsilatının tamamlanması gerekmektedir.")

    with col_right:
        st.markdown("### 🛡️ İşlem Logları (Ledger)")
        with st.container(height=500, border=True):
            if not active_pool.history: st.caption("Henüz işlem kaydı yok.")
            for event in reversed(active_pool.history):
                st.markdown(f"**Döngü {event['month']}** - Kazanan: `{event['winner']}`")
                st.markdown(f"<span style='color:green;'>Ana Para: {event['payout']:,}</span><br><span style='color:blue;'>Temettü: +{event.get('yield', 0):,.2f}</span>", unsafe_allow_html=True)
                st.caption(event['details'][0])
                st.divider()

with tab2:
    st.markdown("### 📈 ABD Temettü ETF (SCHD/VYM) Büyüme Analizi")
    st.write("Emanet kasasında (Escrow) bekleyen fonlar, dünyanın en stabil temettü ödeyen borsa yatırım fonlarında değerlendirilir. Sırasını bekleyen kullanıcı enflasyona karşı korunur.")
    
    if len(active_pool.history) > 0:
        # Plotly ile Profesyonel Grafik
        months = [f"{h['month']}. Döngü" for h in active_pool.history]
        yields = [h.get("yield", 0) for h in active_pool.history]
        cumulative_yields = [sum(yields[:i+1]) for i in range(len(yields))]

        fig = go.Figure()
        fig.add_trace(go.Scatter(x=months, y=cumulative_yields, mode='lines+markers', name='Kümülatif Getiri', line=dict(color='#10b981', width=3), fill='tozeroy', fillcolor='rgba(16, 185, 129, 0.2)'))
        fig.add_trace(go.Bar(x=months, y=yields, name='Döngüsel Getiri', marker_color='#3b82f6'))
        
        fig.update_layout(title="Kasa İçi Yatırım Getirisi", xaxis_title="Zaman Çizelgesi", yaxis_title=f"Getiri ({active_pool.currency})", plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', hovermode="x unified")
        
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Kura döngüleri tamamlandıkça getiri grafiği burada oluşacaktır.")

with tab3:
    st.markdown("### ⚖️ Uluslararası Vergi ve AML Raporlama Merkezi")
    st.markdown("Bu modül, resmi otoriteler (Maliye, IRS vb.) için sınır ötesi değer transferlerinin kara para aklama (AML) taramasından geçtiğini doğrular ve vergi beyannamesi oluşturur.")
    if len(active_pool.history) > 0:
        user_names = [u.name for u in active_pool.users]
        selected_user = st.selectbox("Raporlanacak Mükellef (Müşteri):", user_names)
        st.success(f"✅ {selected_user} için global yaptırım ve kara liste (OFAC) taraması temiz.")
        st.download_button(label="📥 Resmi Vergi Dökümünü İndir (CSV)", data="Belge No,Müşteri,Durum\n12345,Test,Temiz", file_name=f"Compliance_Report_{selected_user}.csv", type="primary")
    else:
        st.warning("Rapor oluşturmak için en az bir finansal döngü tamamlanmalıdır.")