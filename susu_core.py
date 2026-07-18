import streamlit as st
import json
import random
import pandas as pd
import requests
import time
from io import BytesIO

# Sayfa Ayarları
st.set_page_config(page_title="Susu Global - WealthTech Platform", page_icon="🌐", layout="wide")

# Streamlit Secrets
SUPABASE_URL = st.secrets.get("SUPABASE_URL")
SUPABASE_KEY = st.secrets.get("SUPABASE_KEY")

def get_clean_base_url():
    if not SUPABASE_URL: return ""
    url = SUPABASE_URL.strip()
    if url.endswith("/"): url = url[:-1]
    if "/rest/v1" in url:
        url = url.replace("/rest/v1", "")
        if url.endswith("/"): url = url[:-1]
    return url

# ==========================================
# 🌍 YERELLEŞTİRME MOTORU
# ==========================================
LOCALIZATION_MAP = {
    "TRY": {
        "app_title": "🪙 SUSU WEALTHTECH: TEMETTÜ & BİRİKİM",
        "sub_title": "ABD Temettü ETF'leri ve akıllı kasa altyapısıyla desteklenen sınır ötesi dijital birikim ağı.",
        "pool_label": "Aktif Birikim Odası",
        "metrics_volume": "Dönen Hacim (GMV)",
        "metrics_revenue": "Platform Geliri",
        "metrics_yield": "📈 Kasa ETF Getirisi (Temettü)",
        "btn_draw": "🔌 Kura Çek, Getiriyi ve Fonu Dağıt",
        "won_message": "Tebrikler! {winner}, {amount:,} {currency} ana para ve {yield_amt:,.2f} {currency} ETF temettü getirisi kazandı!"
    },
    "DEFAULT": {
        "app_title": "🌐 SUSU WEALTHTECH: DIVIDEND & SAVINGS",
        "sub_title": "Cross-border digital savings network powered by US Dividend ETFs and smart escrow infrastructure.",
        "pool_label": "Active Savings Pool",
        "metrics_volume": "Room Volume (GMV)",
        "metrics_revenue": "Platform Revenue",
        "metrics_yield": "📈 Escrow ETF Yield (Dividend)",
        "btn_draw": "🔌 Release Escrow, Yield & Draw",
        "won_message": "Success! {winner} won {amount:,} {currency} principal plus {yield_amt:,.2f} {currency} in ETF dividend yield!"
    }
}

def get_locale(currency):
    return LOCALIZATION_MAP.get(currency, LOCALIZATION_MAP["DEFAULT"])

# ==========================================
# VERİTABANI & NESNELER
# ==========================================
def load_global_state_from_db():
    base_url = get_clean_base_url()
    if not base_url or not SUPABASE_KEY: return None
    headers = {"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}"}
    try:
        res = requests.get(f"{base_url}/rest/v1/susu_state?id=eq.US-GLOBAL-01", headers=headers)
        if res.status_code == 200 and res.json() and "pools" in res.json()[0]["data"]:
            return res.json()[0]["data"]
        else:
            default = {
                "pools": {
                    "Alpha-USD": {"pool_id": "Alpha-USD", "pool_name": "🌐 Global USD Alpha", "currency": "USD", "monthly_contribution": 1000, "total_months": 4, "current_month": 1, "total_yield": 0.0, "users": [], "history": []},
                    "Finansal-Ozgurluk": {"pool_id": "Finansal-Ozgurluk", "pool_name": "🪙 Finansal Özgürlük (ETF Destekli)", "currency": "TRY", "monthly_contribution": 20000, "total_months": 4, "current_month": 1, "total_yield": 0.0, "users": [], "history": []}
                }
            }
            save_global_state_to_db(default)
            return default
    except: return None

def save_global_state_to_db(global_state_dict):
    base_url = get_clean_base_url()
    if not base_url or not SUPABASE_KEY: return False
    headers = {"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}", "Content-Type": "application/json", "Prefer": "resolution=merge-duplicates"}
    try:
        res = requests.post(f"{base_url}/rest/v1/susu_state", headers=headers, json=[{"id": "US-GLOBAL-01", "data": global_state_dict}])
        return res.status_code in [200, 201]
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
# ARAYÜZ
# ==========================================
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2953/2953363.png", width=70)
    st.title("WealthTech Core")
    st.caption("🚀 ETF Yield & Web3 Routing v9.0")
    st.write("---")
    
    user_role = st.radio("Perspective:", ["Admin (Platform Owner)", "Participant"], horizontal=True)
    st.write("---")
    
    pool_options = {p_id: p_data["pool_name"] for p_id, p_data in pools_dict.items()}
    if not pool_options: st.stop()
    selected_pool_id = st.selectbox("📁 Select Pool:", options=list(pool_options.keys()), format_func=lambda x: pool_options[x])
    
    p_data = pools_dict[selected_pool_id]
    active_pool = SusuPool(p_data["pool_id"], p_data["pool_name"], p_data["currency"], p_data["monthly_contribution"], p_data["total_months"], p_data["current_month"], p_data.get("total_yield", 0.0), p_data.get("history", []))
    for u in p_data["users"]: active_pool.users.append(SusuUser(u["user_id"], u["name"], u["country"], u["passport_verified"], u["credit_score"], u["has_paid"], u["has_received"], u.get("trust_score", 50)))

    lang = get_locale(active_pool.currency)
    st.write("---")
    
    if user_role == "Admin (Platform Owner)":
        st.subheader("👤 Onboard (KYC)")
        with st.form("onboard_form", clear_on_submit=True):
            name = st.text_input("Name")
            country = st.selectbox("Routing Region", ["Turkey", "United States", "United Kingdom", "Germany", "Nigeria", "Mexico"])
            passport = st.text_input("ID Number")
            score = st.slider("FICO Score", 300, 850, 720)
            if st.form_submit_button("Verify & Add") and name:
                if len(active_pool.users) >= active_pool.total_months: st.error("Pool full!")
                else:
                    active_pool.users.append(SusuUser(len(active_pool.users) + 1, name, country, True if passport else False, score, trust_score=random.randint(40, 95)))
                    pools_dict[selected_pool_id] = active_pool.to_dict(); global_state["pools"] = pools_dict; save_global_state_to_db(global_state); st.rerun()

st.title(lang["app_title"])
st.write(lang["sub_title"])

col1, col2, col3, col4 = st.columns(4)
with col1: st.metric(lang["metrics_volume"], f"{sum([h['payout'] for h in active_pool.history]):,} {active_pool.currency}")
with col2: st.metric(lang["metrics_revenue"], f"{sum([h['fee'] for h in active_pool.history]):,} {active_pool.currency}")
with col3: st.metric(lang["metrics_yield"], f"+{active_pool.total_yield:,.2f} {active_pool.currency}")
with col4: st.metric("Global Trust Score Avg", f"{int(sum(u.trust_score for u in active_pool.users)/len(active_pool.users)) if active_pool.users else 0} / 100")

st.write("---")
tab1, tab2, tab3 = st.tabs(["🏛️ Smart Escrow (İşlemler)", "📈 US Dividend ETF Yield", "📜 Tax & AML"])

with tab1:
    left, right = st.columns([2, 1])
    with left:
        if not active_pool.users: st.info("No active users.")
        else:
            st.dataframe(pd.DataFrame([{"ID": u.user_id, "Katılımcı": u.name, "Bölge": u.country, "Trust Score": f"⭐ {u.trust_score}", "Durum": "🎁 Kazandı" if u.has_received else "⏳ Bekliyor", "Ödeme": "🟢 PAID" if u.has_paid else "🔴 PENDING"} for u in active_pool.users]), use_container_width=True, hide_index=True)
            
            st.write("---")
            st.subheader("💸 Cross-Border Payment Routing")
            p_cols = st.columns(len(active_pool.users))
            for idx, u in enumerate(active_pool.users):
                with p_cols[idx]:
                    if u.has_paid: st.success("✓ Paid")
                    else:
                        if st.button(f"Pay ({u.name.split()[0]})", key=f"pay_{u.user_id}", use_container_width=True):
                            u.has_paid = True; pools_dict[selected_pool_id] = active_pool.to_dict(); global_state["pools"] = pools_dict; save_global_state_to_db(global_state); st.rerun()

            st.write("---")
            if len(active_pool.users) >= active_pool.total_months and all(u.has_paid for u in active_pool.users):
                if st.button(lang["btn_draw"], type="primary", use_container_width=True):
                    eligible = [u for u in active_pool.users if not u.has_received]
                    if eligible:
                        with st.spinner("Executing Bitcoin Lightning / USDC Routing & Liquidating ETF Yields..."): time.sleep(2)
                        
                        # Temettü (Yield) Simülasyonu: Biriken paranın %0.5 ile %1.2'si arası havuzda temettü olarak birikir
                        collected = active_pool.monthly_contribution * len(active_pool.users)
                        generated_yield = collected * random.uniform(0.005, 0.012)
                        active_pool.total_yield += generated_yield
                        
                        fee = collected * 0.01; payout = collected - fee
                        winner = random.choice(eligible); winner.has_received = True; winner.trust_score = min(100, winner.trust_score + 5)
                        
                        details = [f"⚡ [Web3 Routing] {u.name} transfer settled via Stablecoin rails.", f"📈 [ETF Sweep] Excess capital auto-staked. Yield generated: {generated_yield:,.2f} {active_pool.currency}"]
                        active_pool.history.append({"month": active_pool.current_month, "winner": winner.name, "payout": payout, "yield": generated_yield, "fee": fee, "details": details})
                        active_pool.current_month += 1
                        for u in active_pool.users: u.has_paid = False
                        pools_dict[selected_pool_id] = active_pool.to_dict(); global_state["pools"] = pools_dict; save_global_state_to_db(global_state)
                        st.balloons(); st.success(lang["won_message"].format(winner=winner.name, amount=payout, yield_amt=generated_yield, currency=active_pool.currency)); st.rerun()
            elif any(not u.has_paid for u in active_pool.users):
                if user_role == "Admin (Platform Owner)" and st.button("⚡ Admin: Auto-Fund All via Smart Contract", use_container_width=True):
                    for u in active_pool.users: u.has_paid = True
                    pools_dict[selected_pool_id] = active_pool.to_dict(); global_state["pools"] = pools_dict; save_global_state_to_db(global_state); st.rerun()

    with right:
        st.subheader("🛡️ Clearing Logs")
        for event in reversed(active_pool.history):
            with st.expander(f"⚙️ Cycle {event['month']} / Winner: {event['winner']}"):
                st.code(f"PRINCIPAL: {event['payout']:,}\nDIVIDEND YIELD: +{event.get('yield', 0):,.2f}\nREV SHARE: {event['fee']:,}", language="bash")
                for d in event['details']: st.caption(d)

with tab2:
    st.subheader("📈 Institutional Yield Dashboard")
    st.write("Emanet kasasında bekleyen fonlar, kura gününe kadar dünyanın en güvenilir US Dividend ETF'lerine ve güvenli tahvillere (T-Bills) yönlendirilir. Yatırımcılar sırasını beklerken bile pasif gelir elde eder.")
    
    if active_pool.total_yield > 0:
        st.success(f"🔥 Bu havuz piyasalardan şu ana kadar toplam **{active_pool.total_yield:,.2f} {active_pool.currency}** temettü geliri üretti!")
        chart_data = pd.DataFrame([{"Döngü": f"{h['month']}. Ay", "Temettü Getirisi": h.get("yield", 0)} for h in active_pool.history])
        st.area_chart(chart_data.set_index("Döngü"))
    else:
        st.info("İlk döngü (kura) tamamlandıktan sonra ETF getiri analizleri burada görünecektir.")

with tab3:
    st.subheader("📜 Yasal Uyum ve Güven Pasaportu")
    st.info("Kullanıcıların 'Trust Score' (Güven Skoru) puanlaması, platform içi sadakat ve sınır ötesi finansal güvenilirliklerini kanıtlar. Bu veri, gelişmekte olan ülkelerdeki katılımcılar için küresel bir kredi skoruna dönüştürülebilir.")