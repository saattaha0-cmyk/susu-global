import streamlit as st
import random
import pandas as pd
import requests
import time
import plotly.graph_objects as go

# Sayfa Ayarları
st.set_page_config(page_title="Susu Global | Enterprise WealthTech", page_icon="🏦", layout="wide", initial_sidebar_state="expanded")

# ==========================================
# 🎨 ÖZEL CSS & STİL
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
            default = {"pools": {"Global-Alpha": {"pool_id": "Global-Alpha", "pool_name": "🌐 Global Alpha Pool", "currency": "USD", "monthly_contribution": 1000, "total_months": 4, "current_month": 1, "total_yield": 0.0, "strategy": "🤖 Smart Yield (Otomatik)", "users": [], "history": []}}}
            save_global_state_to_db(default); return default
    except: return None

def save_global_state_to_db(global_state_dict):
    base_url = get_clean_base_url()
    if not base_url or not SUPABASE_KEY: return False
    headers = {"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}", "Content-Type": "application/json", "Prefer": "resolution=merge-duplicates"}
    try: res = requests.post(f"{base_url}/rest/v1/susu_state", headers=headers, json=[{"id": "US-GLOBAL-01", "data": global_state_dict}]); return res.status_code in [200, 201]
    except: return False

class SusuUser:
    def __init__(self, user_id, name, country, has_paid=False, has_received=False, trust_score=50, **kwargs):
        self.user_id = user_id; self.name = name; self.country = country; self.has_paid = has_paid; self.has_received = has_received; self.trust_score = trust_score
    def to_dict(self): return {"user_id": self.user_id, "name": self.name, "country": self.country, "has_paid": self.has_paid, "has_received": self.has_received, "trust_score": self.trust_score}

global_state = load_global_state_from_db()
if not global_state: global_state = {"pools": {}}
pools_dict = global_state["pools"]

# Eski veritabanı kayıtları için strateji yamasını ekle
for p_id in pools_dict:
    if "strategy" not in pools_dict[p_id]: pools_dict[p_id]["strategy"] = "🤖 Smart Yield (Otomatik)"

# ==========================================
# 🎛️ YAN MENÜ (Sidebar)
# ==========================================
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2953/2953363.png", width=50)
    st.markdown("### Susu Global")
    st.caption("WealthTech OS | v12.0 Smart Yield")
    st.divider()
    
    selected_pool_id = st.selectbox("📂 Aktif Portföy", options=list(pools_dict.keys()), format_func=lambda x: pools_dict[x]["pool_name"])
    p_data = pools_dict[selected_pool_id]
    active_users = [SusuUser(**u) for u in p_data["users"]]
    current_month = p_data["current_month"]
    total_months = p_data["total_months"]
    is_completed = current_month > total_months

    # YENİ EKLENEN: STRATEJİ SEÇİMİ
    st.markdown("#### ⚙️ Portföy Stratejisi")
    strategies = ["🤖 Smart Yield (Otomatik)", "🌙 Katılım (Altın Endeksli)", "🏦 Geleneksel (US ETF)", "⚡ Yüksek Risk (Bitcoin)"]
    current_strat_idx = strategies.index(p_data["strategy"]) if p_data["strategy"] in strategies else 0
    selected_strategy = st.selectbox("Emanet Kasa Yönetimi", strategies, index=current_strat_idx)
    
    if selected_strategy != p_data["strategy"]:
        p_data["strategy"] = selected_strategy
        save_global_state_to_db(global_state)
        st.rerun()

    st.divider()
    st.markdown("#### 👤 Yeni Müşteri Katılımı")
    with st.form("onboard_form", clear_on_submit=True):
        name = st.text_input("Ad Soyad")
        country = st.selectbox("Bağlı Bölge (Node)", ["TR-Istanbul", "US-NewYork", "UK-London", "DE-Berlin"])
        if st.form_submit_button("Doğrula ve Ağa Ekle"):
            if len(active_users) >= total_months: st.error("Maksimum kapasiteye ulaşıldı.")
            else:
                p_data["users"].append(SusuUser(len(active_users) + 1, name, country, trust_score=random.randint(60, 95)).to_dict())
                save_global_state_to_db(global_state); st.rerun()

# ==========================================
# 🌐 ÜST BAR: CANLI PİYASA TERMİNALİ
# ==========================================
t1, t2, t3, t4 = st.columns(4)
with t1: st.metric("BTC/USD", "64,230.50", "1.2%", delta_color="normal")
with t2: st.metric("XAU/USD (Altın)", "2,340.10", "0.4%", delta_color="normal")
with t3: st.metric("US ETF Yield", "4.85%", "Yıllık", delta_color="off")
with t4: st.metric("Aktif Strateji", p_data["strategy"].split(" ")[1], p_data["strategy"].split(" ")[0], delta_color="off")
st.divider()

# ==========================================
# 📊 ANA YÖNETİM PANELİ (Dashboard)
# ==========================================
col_title, col_status = st.columns([3, 1])
with col_title: st.markdown(f"<h2>🏦 {p_data['pool_name']}</h2>", unsafe_allow_html=True)
with col_status:
    if is_completed: st.success("✅ Döngü Tamamlandı")
    else: st.info(f"⏳ Döngü {current_month} / {total_months}")

# Ana Metrikler
with st.container(border=True):
    mc1, mc2, mc3, mc4 = st.columns(4)
    with mc1: st.metric("Aylık Katılım", f"{p_data['monthly_contribution']:,} USD")
    with mc2: st.metric("Kümülatif Getiri", f"+{p_data.get('total_yield', 0):,.2f} USD")
    with mc3: st.metric("Havuz Kapasitesi", f"{len(active_users)} / {total_months} Kişi")
    with mc4: st.metric("Susu Trust Score", f"{int(sum(u.trust_score for u in active_users)/len(active_users)) if active_users else 0} ⭐")

tab1, tab2 = st.tabs(["⚡ Akıllı Sözleşme (Operasyon)", "🚀 Getiri Grafiği"])

with tab1:
    col_left, col_right = st.columns([6, 4])
    
    with col_left:
        st.markdown("### 👥 Tahsilat & Dağıtım Motoru")
        if not active_users: st.warning("Havuz boş. Sol menüden müşteri ekleyin.")
        else:
            df = pd.DataFrame([{"Müşteri": u.name, "Bölge": u.country, "Trust Score": f"{u.trust_score}", "Ödeme": "✅" if u.has_paid else "⏳", "Durum": "🏦 Kazandı" if u.has_received else "Bekliyor"} for u in active_users])
            st.dataframe(df, use_container_width=True, hide_index=True)
            
            if not is_completed:
                with st.container(border=True):
                    pay_cols = st.columns(len(active_users))
                    for idx, u in enumerate(active_users):
                        with pay_cols[idx]:
                            if u.has_paid: st.success(f"{u.name}")
                            else:
                                if st.button(f"Tahsil Et:\n{u.name}", key=f"pay_{u.user_id}", use_container_width=True):
                                    p_data["users"][idx]["has_paid"] = True; save_global_state_to_db(global_state); st.rerun()

                # DİNAMİK GETİRİ MOTORU (YENİ)
                if len(active_users) >= total_months and all(u.has_paid for u in active_users):
                    st.info(f"ℹ️ Fonlar {p_data['strategy']} rotasına aktarıldı.")
                    if st.button("🚀 PİYASA GETİRİSİNİ HESAPLA VE DAĞIT", type="primary", use_container_width=True):
                        eligible_indices = [i for i, u in enumerate(active_users) if not u.has_received]
                        if eligible_indices:
                            with st.spinner(f"Optimizasyon yapılıyor: {p_data['strategy']}..."):
                                time.sleep(1.5)
                                collected = p_data["monthly_contribution"] * total_months
                                
                                # Stratejiye göre getiri hesaplama kurgusu
                                strat = p_data["strategy"]
                                rate_gold = random.uniform(0.005, 0.015)
                                rate_etf = random.uniform(0.01, 0.02)
                                rate_btc = random.uniform(-0.02, 0.05) # BTC zarar da ettirebilir
                                
                                if "Katılım" in strat: final_rate = rate_gold; detail = "Fiziksel Altın bazlı değer artışı"
                                elif "Geleneksel" in strat: final_rate = rate_etf; detail = "US Temettü ETF getirisi"
                                elif "Yüksek Risk" in strat: final_rate = rate_btc; detail = "Bitcoin Day-Trade kar/zararı"
                                else: # Smart Yield
                                    final_rate = max(rate_gold, rate_etf, rate_btc)
                                    detail = f"Smart Yield Optimizasyonu (Kullanılan Oran: %{final_rate*100:.2f})"

                                generated_yield = collected * final_rate
                                p_data["total_yield"] = p_data.get("total_yield", 0) + generated_yield
                                
                                winner_idx = random.choice(eligible_indices)
                                p_data["users"][winner_idx]["has_received"] = True
                                p_data["users"][winner_idx]["trust_score"] = min(100, p_data["users"][winner_idx]["trust_score"] + 5)
                                
                                payout = collected * 0.99 # %1 platform kesintisi
                                p_data["history"].append({"month": current_month, "winner": active_users[winner_idx].name, "payout": payout, "yield": generated_yield, "strat_detail": detail})
                                p_data["current_month"] += 1
                                for u in p_data["users"]: u["has_paid"] = False
                                
                                save_global_state_to_db(global_state); st.rerun()

    with col_right:
        st.markdown("### 🛡️ Dağıtım Logları")
        with st.container(height=450, border=True):
            if not p_data["history"]: st.caption("Henüz işlem yok.")
            for event in reversed(p_data["history"]):
                st.markdown(f"**Döngü {event['month']}** | Kazanan: **{event['winner']}**")
                color = "green" if event.get('yield', 0) >= 0 else "red"
                st.markdown(f"Ana Para: **{event['payout']:,}** USD <br> Temettü: <span style='color:{color};'>**{event.get('yield', 0):,.2f}** USD</span>", unsafe_allow_html=True)
                st.caption(f"⚙️ {event.get('strat_detail', '')}")
                st.divider()

with tab2:
    st.markdown("### 📈 Strateji Performans Analizi")
    if p_data["history"]:
        months = [f"Döngü {h['month']}" for h in p_data["history"]]
        yields = [h.get("yield", 0) for h in p_data["history"]]
        
        fig = go.Figure()
        colors = ['#ef4444' if y < 0 else '#10b981' for y in yields]
        fig.add_trace(go.Bar(x=months, y=yields, marker_color=colors, name="Döngüsel Getiri/Zarar"))
        fig.update_layout(title=f"Uygulanan Strateji: {p_data['strategy']}", xaxis_title="Zaman Çizelgesi", yaxis_title="Getiri (USD)", plot_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Veri oluşması için kura çekimi yapılmalıdır.")