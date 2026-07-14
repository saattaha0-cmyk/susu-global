import streamlit as st
import json
import random
import pandas as pd
import requests
import time

# Sayfa Ayarları
st.set_page_config(page_title="Susu Global - FinTech Platform", page_icon="🌐", layout="wide")

# Streamlit Secrets Kontrolü
SUPABASE_URL = st.secrets.get("SUPABASE_URL")
SUPABASE_KEY = st.secrets.get("SUPABASE_KEY")

# ==========================================
# AKILLI URL TEMİZLEYİCİ
# ==========================================
def get_clean_base_url():
    if not SUPABASE_URL: return ""
    url = SUPABASE_URL.strip()
    if url.endswith("/"): url = url[:-1]
    if "/rest/v1" in url:
        url = url.replace("/rest/v1", "")
        if url.endswith("/"): url = url[:-1]
    return url

# ==========================================
# 🌍 KÜLTÜREL YERELLEŞTİRME MOTORU
# ==========================================
LOCALIZATION_MAP = {
    "TRY": {
        "app_title": "🪙 ALTIN GÜNÜ GLOBAL: YENİ NESİL DİJİTAL BİRİKİM",
        "sub_title": "Güvenli, şeffaf ve akıllı emanet kasası altyapısıyla geleneksel altın gününü dünya standartlarına taşıyın.",
        "pool_label": "Aktif Birikim Odası (Altın Günü)",
        "onboard_title": "👤 Katılımcı Ekle (KYC Doğrulama)",
        "participants_title": "👥 Doğrulanmış Katılımcı Listesi (Canlı Bulut Verisi)",
        "escrow_ledger": "🛡️ Kasa Hesap Defteri (Denetim İzi)",
        "metrics_volume": "Toplam Dönen Hacim (GMV)",
        "metrics_revenue": "Platform Geliri (%1 Hizmet Bedeli)",
        "metrics_active": "Aktif Katılımcı",
        "metrics_phase": "Mevcut Tur / Kabul Günü",
        "phase_text": "{month}. Kabul Günü / Toplam {total} Ay",
        "btn_draw": "🔌 Kura Çek ve Aylık Birikimi Dağıt",
        "btn_add": "Kimlik Doğrula ve Gruba Ekle",
        "wait_message": "Grubun başlaması için {count} katılımcıya daha ihtiyaç var. Akıllı escrow sözleşmesi kilitlendi.",
        "kyc_verified": "🛡️ DOĞRULANDI (KYC)",
        "kyc_failed": "❌ BAŞARISIZ",
        "status_received": "🎁 Ödemesini Almış",
        "status_waiting": "⏳ Sırasını Bekliyor",
        "won_message": "Tebrikler! Kurayı {winner} kazandı ve toplam {amount:,} {currency} ödeme aldı!",
        "insurance_covered": "🛡️ BaaS Sigortası {name} adına güvence sağladı."
    },
    "DEFAULT": {
        "app_title": "🌐 SUSU GLOBAL: ROTATIONAL SAVINGS NETWORK",
        "sub_title": "Secure, cross-border decentralized social savings with institutional Escrow Guarantee.",
        "pool_label": "Active Savings Pool",
        "onboard_title": "👤 KYC Onboard User",
        "participants_title": "👥 Verified Pool Participants (Live Cloud Data)",
        "escrow_ledger": "🛡️ Audit Trails (Escrow Ledger)",
        "metrics_volume": "Room Volume (GMV)",
        "metrics_revenue": "1% Take Rate Revenue",
        "metrics_active": "Participants",
        "metrics_phase": "Cycle Phase",
        "phase_text": "Month {month} of {total}",
        "btn_draw": "🔌 Release Monthly Escrow Funds & Draw Winner",
        "btn_add": "Verify & Add to Selected Pool",
        "wait_message": "Waiting for pool to fill. Need {count} more members.",
        "kyc_verified": "🛡️ VERIFIED",
        "kyc_failed": "❌ FAILED",
        "status_received": "🎁 Distributed",
        "status_waiting": "⏳ In Escrow Queue",
        "won_message": "Success! {winner} won the draw and received {amount:,} {currency}!",
        "insurance_covered": "🛡️ Escrow Insurance covered low-score user {name}"
    }
}

def get_locale(currency):
    return LOCALIZATION_MAP.get(currency, LOCALIZATION_MAP["DEFAULT"])

# ==========================================
# VERİTABANI BAĞLANTI SİSTEMİ
# ==========================================
def load_global_state_from_db():
    base_url = get_clean_base_url()
    if not base_url or not SUPABASE_KEY:
        st.warning("⚠️ API anahtarları eksik! Çevrimdışı modda çalışılıyor.")
        return None
    
    headers = {"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}"}
    url = f"{base_url}/rest/v1/susu_state?id=eq.US-GLOBAL-01"
    
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            rows = response.json()
            if rows and "pools" in rows[0]["data"]:
                return rows[0]["data"]
            else:
                default_state = {
                    "pools": {
                        "Alpha-USD": {"pool_id": "Alpha-USD", "pool_name": "🌐 Global USD Alpha Pool", "currency": "USD", "monthly_contribution": 1000, "total_months": 4, "current_month": 1, "users": [], "history": []},
                        "Finansal-Ozgurluk": {"pool_id": "Finansal-Ozgurluk", "pool_name": "🪙 Finansal Özgürlük Grubu", "currency": "TRY", "monthly_contribution": 20000, "total_months": 4, "current_month": 1, "users": [], "history": []}
                    }
                }
                save_global_state_to_db(default_state)
                return default_state
        else:
            st.error(f"❌ Veritabanı Hatası: {response.text}")
    except Exception as e:
        st.error(f"❌ Bağlantı Hatası: {e}")
    return None

def save_global_state_to_db(global_state_dict):
    base_url = get_clean_base_url()
    if not base_url or not SUPABASE_KEY: return False
    
    headers = {
        "apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json", "Prefer": "resolution=merge-duplicates"
    }
    url = f"{base_url}/rest/v1/susu_state"
    payload = {"id": "US-GLOBAL-01", "data": global_state_dict}
    
    try:
        response = requests.post(url, headers=headers, json=[payload])
        return response.status_code in [200, 201]
    except Exception as e:
        st.error(f"❌ Kaydetme Hatası: {e}")
        return False

# ==========================================
# GİRİŞİM MANTIĞI NESNELERİ (DATA MODELS)
# ==========================================
class SusuUser:
    def __init__(self, user_id, name, country, passport_verified, credit_score, has_paid=False, has_received=False):
        self.user_id = user_id
        self.name = name
        self.country = country
        self.passport_verified = passport_verified
        self.credit_score = credit_score
        self.has_paid = has_paid
        self.has_received = has_received

    def to_dict(self):
        return {"user_id": self.user_id, "name": self.name, "country": self.country, "passport_verified": self.passport_verified, "credit_score": self.credit_score, "has_paid": self.has_paid, "has_received": self.has_received}

class SusuPool:
    def __init__(self, pool_id, pool_name, currency, monthly_contribution, total_months, current_month=1, history=None):
        self.pool_id = pool_id
        self.pool_name = pool_name
        self.currency = currency
        self.monthly_contribution = monthly_contribution
        self.total_months = total_months
        self.current_month = current_month
        self.users = []
        self.history = history if history is not None else []

    def to_dict(self):
        return {"pool_id": self.pool_id, "pool_name": self.pool_name, "currency": self.currency, "monthly_contribution": self.monthly_contribution, "total_months": self.total_months, "current_month": self.current_month, "users": [u.to_dict() for u in self.users], "history": self.history}

# Global Durumu Yükle
global_state = load_global_state_from_db()
if not global_state:
    global_state = {
        "pools": {
            "Alpha-USD": {"pool_id": "Alpha-USD", "pool_name": "🌐 Global USD Alpha Pool", "currency": "USD", "monthly_contribution": 1000, "total_months": 4, "current_month": 1, "users": [], "history": []},
            "Finansal-Ozgurluk": {"pool_id": "Finansal-Ozgurluk", "pool_name": "🪙 Finansal Özgürlük Grubu", "currency": "TRY", "monthly_contribution": 20000, "total_months": 4, "current_month": 1, "users": [], "history": []}
        }
    }

pools_dict = global_state["pools"]

# ==========================================
# WEB PORTAL ARAYÜZÜ (STREAMLIT ENGINE)
# ==========================================

# Sol Menü Tasarımı
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2953/2953363.png", width=70)
    st.title("Susu Core Engine")
    st.caption("🔑 Role-Based Access Control Active")
    st.write("---")
    
    # 👑 ROL SEÇİM PANELİ (YATIRIMCI DEMO MODU)
    st.subheader("👤 Demo User Role")
    user_role = st.radio("Choose perspective for demo:", ["Admin / Platform Owner", "Pool Participant"], horizontal=True)
    
    st.write("---")
    
    # 📁 HAVUZ SEÇİM PANELİ
    st.subheader("📁 Select Savings Pool")
    pool_options = {p_id: p_data["pool_name"] for p_id, p_data in pools_dict.items()}
    selected_pool_id = st.selectbox("Choose a room:", options=list(pool_options.keys()), format_func=lambda x: pool_options[x])
    
    # Seçili havuz nesnesi oluşturma
    p_data = pools_dict[selected_pool_id]
    active_pool = SusuPool(p_data["pool_id"], p_data["pool_name"], p_data["currency"], p_data["monthly_contribution"], p_data["total_months"], p_data["current_month"], p_data.get("history", []))
    for u in p_data["users"]:
        active_pool.users.append(SusuUser(u["user_id"], u["name"], u["country"], u["passport_verified"], u["credit_score"], u["has_paid"], u["has_received"]))

    lang = get_locale(active_pool.currency)
    st.write("---")
    
    # SADECE ADMIN YENİ HAVUZ DEPLOY EDEBİLİR
    if user_role == "Admin / Platform Owner":
        st.subheader("🆕 Deploy New Pool (Admin Only)")
        with st.expander("Configure Parameters", expanded=False):
            new_id = st.text_input("Unique Pool ID", placeholder="e.g., Izmir-Ege").strip()
            new_name = st.text_input("Display Name", placeholder="e.g., Ege Finans Grubu")
            new_curr = st.selectbox("Currency", ["TRY", "USD", "EUR", "GBP"])
            new_contrib = st.number_input("Monthly Contribution", min_value=10, value=20000, step=100)
            new_duration = st.slider("Total Months / Members", 3, 12, 4)
            create_btn = st.button("🚀 Deploy to Cloud", use_container_width=True)
            
            if create_btn and new_id and new_name:
                prefix = "🪙" if new_curr == "TRY" else "🌐"
                pools_dict[new_id] = {"pool_id": new_id, "pool_name": f"{prefix} {new_name} ({new_curr})", "currency": new_curr, "monthly_contribution": new_contrib, "total_months": new_duration, "current_month": 1, "users": [], "history": []}
                global_state["pools"] = pools_dict
                if save_global_state_to_db(global_state):
                    st.success("Deployed successfully!")
                    st.rerun()

        st.write("---")
        
        # SADECE ADMIN KATILIMCI EKLEYEBİLİR (KYC)
        st.subheader(lang["onboard_title"])
        with st.form("onboard_form", clear_on_submit=True):
            name = st.text_input("Full Name")
            country = st.selectbox("Country", ["Turkey", "United States", "United Kingdom", "Germany", "Nigeria", "Mexico"])
            passport = st.text_input("Passport Number")
            score = st.slider("Credit Score", 300, 850, 720)
            submit = st.form_submit_button(lang["btn_add"])
            
            if submit and name:
                if len(active_pool.users) >= active_pool.total_months:
                    st.error("Pool is full!")
                else:
                    user_id = len(active_pool.users) + 1
                    pass_ok = True if (passport and len(passport) >= 6) else False
                    new_user = SusuUser(user_id, name, country, pass_ok, score)
                    active_pool.users.append(new_user)
                    pools_dict[selected_pool_id] = active_pool.to_dict()
                    global_state["pools"] = pools_dict
                    if save_global_state_to_db(global_state):
                        st.success("Onboarded!")
                        st.rerun()

        st.write("---")
        if st.button("🚨 Factory Reset Database", use_container_width=True):
            default_state = {
                "pools": {
                    "Alpha-USD": {"pool_id": "Alpha-USD", "pool_name": "🌐 Global USD Alpha Pool", "currency": "USD", "monthly_contribution": 1000, "total_months": 4, "current_month": 1, "users": [], "history": []},
                    "Finansal-Ozgurluk": {"pool_id": "Finansal-Ozgurluk", "pool_name": "🪙 Finansal Özgürlük Grubu", "currency": "TRY", "monthly_contribution": 20000, "total_months": 4, "current_month": 1, "users": [], "history": []}
                }
            }
            if save_global_state_to_db(default_state):
                st.success("Database fully reset!")
                st.rerun()
    else:
        st.info("ℹ️ You are in **Participant Mode**. New pool deployment, factory resets, and KYC onboarding are restricted to Admin role.")

# ==========================================
# ANA PANEL (INVESTOR VIEW)
# ==========================================
st.title(lang["app_title"])
st.write(lang["sub_title"])
st.info(f"📍 {lang['pool_label']}: **{active_pool.pool_name}** | **{active_pool.monthly_contribution:,} {active_pool.currency}** Per Participant/Month")

# FinTek Metrik Paneli
col1, col2, col3, col4 = st.columns(4)
total_volume = sum([h['payout'] for h in active_pool.history])
total_revenue = sum([h['fee'] for h in active_pool.history])

with col1: st.metric(label=lang["metrics_volume"], value=f"{total_volume:,} {active_pool.currency}")
with col2: st.metric(label=lang["metrics_revenue"], value=f"{total_revenue:,} {active_pool.currency}")
with col3: st.metric(label=lang["metrics_active"], value=f"{len(active_pool.users)} / {active_pool.total_months}")
with col4: st.metric(label=lang["metrics_phase"], value=lang["phase_text"].format(month=active_pool.current_month, total=active_pool.total_months))

st.write("---")

# GÖRSEL ANALİTİK PANELİ
if active_pool.history:
    st.subheader("📊 FinTech Growth & Escrow Analytics (Investor Data Visuals)")
    chart_data = pd.DataFrame([{
        "Cycle Month": f"Month {h['month']}",
        "Gross Volume (GMV)": h['payout'] + h['fee'],
        "Net Platform Revenue": h['fee']
    } for h in active_pool.history])
    
    c1, c2 = st.columns(2)
    with c1:
        st.caption("🚀 Capital Transacted Volume (Cumulative Growth)")
        st.bar_chart(chart_data.set_index("Cycle Month")["Gross Volume (GMV)"])
    with c2:
        st.caption("💸 Net Core Revenue (1% Take Rate Realized)")
        st.line_chart(chart_data.set_index("Cycle Month")["Net Platform Revenue"])
    st.write("---")

# İki Sütunlu Canlı Veri Akışı
left, right = st.columns([2, 1])

with left:
    st.subheader(lang["participants_title"])
    if not active_pool.users:
        st.info("No active users in this cloud room yet. Use the Admin panel on the left to add members.")
    else:
        user_list = []
        for u in active_pool.users:
            kyc_status = lang["kyc_verified"] if u.passport_verified else lang["kyc_failed"]
            payout_status = lang["status_received"] if u.has_received else lang["status_waiting"]
            payment_indicator = "🟢 PAID" if u.has_paid else "🔴 UNPAID (PENDING)"
            user_list.append({
                "Sıra/ID": u.user_id, "Katılımcı": u.name, "Bölge": u.country,
                "KYC Altyapısı": kyc_status, "Risk Skoru": u.credit_score,
                "Aylık Ödeme": payment_indicator, "Akıllı Durum": payout_status
            })
        st.dataframe(pd.DataFrame(user_list), use_container_width=True, hide_index=True)
        
        # ==========================================
        # 💸 INTERACTIVE PAYMENT TERMINAL (DEMO MODE)
        # ==========================================
        st.write("")
        st.subheader("💸 Interactive Escrow Payment Gateway")
        st.write("In a live app, participants pay via open banking or cards. Click below to simulate instant deposit or credit coverage:")
        
        # Her katılımcı için ödeme yapma butonlarını grid halinde sunalım
        payment_cols = st.columns(len(active_pool.users))
        for idx, u in enumerate(active_pool.users):
            with payment_cols[idx]:
                if u.has_paid:
                    st.success(f"✓ {u.name} paid")
                else:
                    # Risk Temerrüt Simülasyonu (Eğer kredi skoru çok düşükse ödemede zorlanıyor gösterelim)
                    if u.credit_score < 500:
                        st.warning(f"⚠️ {u.name} (Risk)")
                        if st.button(f"Cover with BaaS Insurance", key=f"ins_{u.user_id}", use_container_width=True):
                            u.has_paid = True
                            pools_dict[selected_pool_id] = active_pool.to_dict()
                            global_state["pools"] = pools_dict
                            if save_global_state_to_db(global_state):
                                st.toast(f"BaaS Default Insurance successfully covered {u.name}'s share!")
                                st.rerun()
                    else:
                        if st.button(f"Pay {active_pool.monthly_contribution:,} {active_pool.currency} ({u.name})", key=f"pay_{u.user_id}", use_container_width=True):
                            u.has_paid = True
                            pools_dict[selected_pool_id] = active_pool.to_dict()
                            global_state["pools"] = pools_dict
                            if save_global_state_to_db(global_state):
                                st.toast(f"Payment settled for {u.name}!")
                                st.rerun()

        # Akıllı Havuz Tetikleme Butonu
        st.write("---")
        if len(active_pool.users) < active_pool.total_months:
            needed = active_pool.total_months - len(active_pool.users)
            st.warning(lang["wait_message"].format(count=needed))
        else:
            # Ödeme yapmayanların kontrolü
            unpaid_users = [u for u in active_pool.users if not u.has_paid]
            
            if unpaid_users:
                st.error(f"🔒 **Escrow Locked:** All participants must settle their payments before drawing the winner. **{len(unpaid_users)}** users pending.")
                # Admin için "Hepsini Ödenmiş Yap" Hızlı Demo Butonu
                if user_role == "Admin / Platform Owner":
                    if st.button("⚡ Admin Hack: Simulate Auto-Debit for All", use_container_width=True):
                        for u in active_pool.users:
                            u.has_paid = True
                        pools_dict[selected_pool_id] = active_pool.to_dict()
                        global_state["pools"] = pools_dict
                        if save_global_state_to_db(global_state):
                            st.success("All users simulated as paid!")
                            st.rerun()
            else:
                st.success("🔓 **Escrow Unlocked:** 100% of the funds are safely locked in the smart vault. Ready for distribution!")
                if st.button(lang["btn_draw"], type="primary", use_container_width=True):
                    eligible = [u for u in active_pool.users if not u.has_received]
                    if not eligible:
                        st.info("Döngü tamamlandı! / Cycle fully optimized!")
                    else:
                        with st.spinner("Connecting to Banking-as-a-Service API & Locking Escrow Vault..."):
                            time.sleep(1.5)
                        
                        collected = 0
                        details = []
                        for u in active_pool.users:
                            collected += active_pool.monthly_contribution
                            if u.credit_score >= 500:
                                details.append(f"🟢 [BaaS Webhook] API_200: {u.name} debited {active_pool.monthly_contribution:,} {active_pool.currency}")
                            else:
                                details.append(f"🛡️ [Insurance API] Credit cover deployed for {u.name}. Liquidity pool credit guarantee settled.")
                        
                        fee = collected * 0.01
                        payout = collected - fee
                        
                        winner = random.choice(eligible)
                        winner.has_received = True
                        
                        active_pool.history.append({"month": active_pool.current_month, "winner": winner.name, "payout": payout, "fee": fee, "details": details})
                        active_pool.current_month += 1
                        
                        # Kura çekilince yeni ay için ödemeleri sıfırlayalım
                        for u in active_pool.users: 
                            u.has_paid = False
                        
                        pools_dict[selected_pool_id] = active_pool.to_dict()
                        global_state["pools"] = pools_dict
                        if save_global_state_to_db(global_state):
                            st.balloons()
                            st.success(lang["won_message"].format(winner=winner.name, amount=payout, currency=active_pool.currency))
                            st.rerun()

with right:
    st.subheader(lang["escrow_ledger"])
    if not active_pool.history:
        st.info("No recorded ledgers. Trigger a cycle on the left to see institutional logging.")
    else:
        for event in reversed(active_pool.history):
            with st.expander(f"⚙️ Ledger Node / Cycle {event['month']}"):
                st.caption("🏦 INSTITUTIONAL CLEARING LOGS")
                st.code(f"STATUS: SETTLED\nNET PAYOUT: {event['payout']:,} {active_pool.currency}\nREV SHARE: {event['fee']:,} {active_pool.currency}", language="bash")
                st.write("**Core Routing Logs:**")
                for d in event['details']:
                    st.write(d)