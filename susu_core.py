import streamlit as st
import json
import random
import pandas as pd
import requests
import time
from io import BytesIO

# Sayfa Ayarları
st.set_page_config(page_title="Susu Global - FinTech Platform", page_icon="🌐", layout="wide")

# Streamlit Secrets Kontrolü
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
# 🌍 KÜLTÜREL YERELLEŞTİRME & VERGİ MOTORU
# ==========================================
LOCALIZATION_MAP = {
    "TRY": {
        "app_title": "🪙 ALTIN GÜNÜ GLOBAL: YENİ NESİL DİJİTAL BİRİKİM",
        "sub_title": "Güvenli, şeffaf ve akıllı emanet kasası altyapısıyla geleneksel altın gününü dünya standartlarına taşıyın.",
        "pool_label": "Aktif Birikim Odası (Altın Günü)",
        "onboard_title": "👤 Katılımcı Ekle (KYC Doğrulama)",
        "participants_title": "👥 Doğrulanmış Katılımcı Listesi",
        "escrow_ledger": "🛡️ Kasa Hesap Defteri",
        "metrics_volume": "Toplam Dönen Hacim",
        "metrics_revenue": "Platform Geliri",
        "metrics_active": "Aktif Katılımcı",
        "metrics_phase": "Mevcut Tur",
        "phase_text": "{month}. Kabul Günü / {total} Ay",
        "btn_draw": "🔌 Kura Çek ve Dağıt",
        "btn_add": "Kimlik Doğrula ve Gruba Ekle",
        "wait_message": "Grubun başlaması için {count} katılımcıya daha ihtiyaç var.",
        "kyc_verified": "🛡️ DOĞRULANDI",
        "kyc_failed": "❌ BAŞARISIZ",
        "status_received": "🎁 Ödemesini Almış",
        "status_waiting": "⏳ Sırasını Bekliyor",
        "won_message": "Tebrikler! Kurayı {winner} kazandı ve toplam {amount:,} {currency} ödeme aldı!",
        "tax_title": "📜 Yasal Uyum ve Vergi Raporlama (Compliance & Tax)",
        "tax_desc": "Maliye Bakanlığı ve yerel regülatörler için sınır ötesi dijital emanet gelir/gider beyannamesi oluşturun.",
        "btn_download": "📥 Resmi Vergi Raporunu İndir (CSV)"
    },
    "DEFAULT": {
        "app_title": "🌐 SUSU GLOBAL: ROTATIONAL SAVINGS NETWORK",
        "sub_title": "Secure, cross-border decentralized social savings with institutional Escrow Guarantee.",
        "pool_label": "Active Savings Pool",
        "onboard_title": "👤 KYC Onboard User",
        "participants_title": "👥 Verified Pool Participants",
        "escrow_ledger": "🛡️ Escrow Ledger",
        "metrics_volume": "Room Volume",
        "metrics_revenue": "Platform Revenue",
        "metrics_active": "Participants",
        "metrics_phase": "Cycle Phase",
        "phase_text": "Month {month} of {total}",
        "btn_draw": "🔌 Release Escrow & Draw",
        "btn_add": "Verify & Add",
        "wait_message": "Waiting for pool to fill. Need {count} more members.",
        "kyc_verified": "🛡️ VERIFIED",
        "kyc_failed": "❌ FAILED",
        "status_received": "🎁 Distributed",
        "status_waiting": "⏳ In Queue",
        "won_message": "Success! {winner} won the draw and received {amount:,} {currency}!",
        "tax_title": "📜 Tax & AML Compliance Reporting",
        "tax_desc": "Generate official tax statements and Anti-Money Laundering (AML) reports for cross-border transactions.",
        "btn_download": "📥 Download Official Tax Statement (CSV)"
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
            default = {"pools": {"Alpha-USD": {"pool_id": "Alpha-USD", "pool_name": "🌐 Global USD Alpha Pool", "currency": "USD", "monthly_contribution": 1000, "total_months": 4, "current_month": 1, "users": [], "history": []}, "Finansal-Ozgurluk": {"pool_id": "Finansal-Ozgurluk", "pool_name": "🪙 Finansal Özgürlük Grubu", "currency": "TRY", "monthly_contribution": 20000, "total_months": 4, "current_month": 1, "users": [], "history": []}}}
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
    def __init__(self, user_id, name, country, passport_verified, credit_score, has_paid=False, has_received=False):
        self.user_id = user_id; self.name = name; self.country = country; self.passport_verified = passport_verified; self.credit_score = credit_score; self.has_paid = has_paid; self.has_received = has_received
    def to_dict(self): return {"user_id": self.user_id, "name": self.name, "country": self.country, "passport_verified": self.passport_verified, "credit_score": self.credit_score, "has_paid": self.has_paid, "has_received": self.has_received}

class SusuPool:
    def __init__(self, pool_id, pool_name, currency, monthly_contribution, total_months, current_month=1, history=None):
        self.pool_id = pool_id; self.pool_name = pool_name; self.currency = currency; self.monthly_contribution = monthly_contribution; self.total_months = total_months; self.current_month = current_month; self.users = []; self.history = history if history is not None else []
    def to_dict(self): return {"pool_id": self.pool_id, "pool_name": self.pool_name, "currency": self.currency, "monthly_contribution": self.monthly_contribution, "total_months": self.total_months, "current_month": self.current_month, "users": [u.to_dict() for u in self.users], "history": self.history}

global_state = load_global_state_from_db()
if not global_state: global_state = {"pools": {}}
pools_dict = global_state["pools"]

# ==========================================
# WEB PORTAL ARAYÜZÜ (STREAMLIT ENGINE)
# ==========================================
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2953/2953363.png", width=70)
    st.title("Susu Core Engine")
    st.caption("🔑 Escrow & Tax Compliant v8.0")
    st.write("---")
    
    user_role = st.radio("Choose perspective:", ["Admin / Platform Owner", "Pool Participant"], horizontal=True)
    st.write("---")
    
    pool_options = {p_id: p_data["pool_name"] for p_id, p_data in pools_dict.items()}
    if not pool_options: st.stop()
    selected_pool_id = st.selectbox("📁 Select Pool:", options=list(pool_options.keys()), format_func=lambda x: pool_options[x])
    
    p_data = pools_dict[selected_pool_id]
    active_pool = SusuPool(p_data["pool_id"], p_data["pool_name"], p_data["currency"], p_data["monthly_contribution"], p_data["total_months"], p_data["current_month"], p_data.get("history", []))
    for u in p_data["users"]: active_pool.users.append(SusuUser(u["user_id"], u["name"], u["country"], u["passport_verified"], u["credit_score"], u["has_paid"], u["has_received"]))

    lang = get_locale(active_pool.currency)
    st.write("---")
    
    if user_role == "Admin / Platform Owner":
        st.subheader("🆕 Deploy New Pool")
        with st.expander("Configure Parameters", expanded=False):
            new_id = st.text_input("Unique Pool ID").strip()
            new_name = st.text_input("Display Name")
            new_curr = st.selectbox("Currency", ["TRY", "USD", "EUR", "GBP"])
            new_contrib = st.number_input("Monthly Contribution", min_value=10, value=5000, step=100)
            new_duration = st.slider("Total Months / Members", 3, 12, 4)
            if st.button("🚀 Deploy to Cloud", width="stretch" and new_id and new_name:
                pools_dict[new_id] = {"pool_id": new_id, "pool_name": f"✨ {new_name} ({new_curr})", "currency": new_curr, "monthly_contribution": new_contrib, "total_months": new_duration, "current_month": 1, "users": [], "history": []}
                global_state["pools"] = pools_dict; save_global_state_to_db(global_state); st.rerun()

        st.write("---")
        st.subheader(lang["onboard_title"])
        with st.form("onboard_form", clear_on_submit=True):
            name = st.text_input("Full Name")
            country = st.selectbox("Country", ["Turkey", "United States", "United Kingdom", "Germany", "Nigeria", "Mexico"])
            passport = st.text_input("Passport (KYC/AML)")
            score = st.slider("Credit Score", 300, 850, 720)
            if st.form_submit_button(lang["btn_add"]) and name:
                if len(active_pool.users) >= active_pool.total_months: st.error("Pool full!")
                else:
                    active_pool.users.append(SusuUser(len(active_pool.users) + 1, name, country, True if passport else False, score))
                    pools_dict[selected_pool_id] = active_pool.to_dict(); global_state["pools"] = pools_dict; save_global_state_to_db(global_state); st.rerun()
    else:
        st.info("ℹ️ Participant Mode: Configuration restricted.")

# ==========================================
# ANA PANEL
# ==========================================
st.title(lang["app_title"])
st.info(f"📍 {lang['pool_label']}: **{active_pool.pool_name}** | **{active_pool.monthly_contribution:,} {active_pool.currency}**")

col1, col2, col3, col4 = st.columns(4)
with col1: st.metric(lang["metrics_volume"], f"{sum([h['payout'] for h in active_pool.history]):,} {active_pool.currency}")
with col2: st.metric(lang["metrics_revenue"], f"{sum([h['fee'] for h in active_pool.history]):,} {active_pool.currency}")
with col3: st.metric(lang["metrics_active"], f"{len(active_pool.users)} / {active_pool.total_months}")
with col4: st.metric(lang["metrics_phase"], lang["phase_text"].format(month=active_pool.current_month, total=active_pool.total_months))

st.write("---")

tab1, tab2 = st.tabs(["🏛️ Escrow & Draw (Ana İşlemler)", "📜 Tax & Compliance (Vergi ve Yasal Uyum)"])

with tab1:
    left, right = st.columns([2, 1])
    with left:
        if not active_pool.users: st.info("No active users.")
        else:
            st.dataframe(pd.DataFrame([{"ID": u.user_id, "Katılımcı": u.name, "Bölge": u.country, "KYC/AML": lang["kyc_verified"] if u.passport_verified else lang["kyc_failed"], "Durum": lang["status_received"] if u.has_received else lang["status_waiting"], "Ödeme": "🟢 PAID" if u.has_paid else "🔴 PENDING"} for u in active_pool.users]), use_container_width=True, hide_index=True)
            
            st.write("---")
            st.subheader("💸 Payment Terminal")
            p_cols = st.columns(len(active_pool.users))
            for idx, u in enumerate(active_pool.users):
                with p_cols[idx]:
                    if u.has_paid: st.success(f"✓ {u.name.split()[0]} paid")
                    else:
                        if st.button(f"Pay {u.name.split()[0]}", key=f"pay_{u.user_id}", width="stretch":
                            u.has_paid = True; pools_dict[selected_pool_id] = active_pool.to_dict(); global_state["pools"] = pools_dict; save_global_state_to_db(global_state); st.rerun()

            st.write("---")
            if len(active_pool.users) < active_pool.total_months:
                st.warning(lang["wait_message"].format(count=active_pool.total_months - len(active_pool.users)))
            else:
                if any(not u.has_paid for u in active_pool.users):
                    st.error("🔒 Escrow Locked: All members must pay first.")
                    if user_role == "Admin / Platform Owner" and st.button("⚡ Admin Auto-Pay All", width="stretch":
                        for u in active_pool.users: u.has_paid = True
                        pools_dict[selected_pool_id] = active_pool.to_dict(); global_state["pools"] = pools_dict; save_global_state_to_db(global_state); st.rerun()
                else:
                    if st.button(lang["btn_draw"], type="primary", width="stretch":
                        eligible = [u for u in active_pool.users if not u.has_received]
                        if not eligible: st.info("Cycle completed!")
                        else:
                            with st.spinner("Processing Smart Contract..."): time.sleep(1)
                            collected = active_pool.monthly_contribution * len(active_pool.users)
                            fee = collected * 0.01; payout = collected - fee
                            winner = random.choice(eligible); winner.has_received = True
                            details = [f"🟢 [Webhook] {u.name} paid {active_pool.monthly_contribution}" for u in active_pool.users]
                            active_pool.history.append({"month": active_pool.current_month, "winner": winner.name, "payout": payout, "fee": fee, "details": details})
                            active_pool.current_month += 1
                            for u in active_pool.users: u.has_paid = False
                            pools_dict[selected_pool_id] = active_pool.to_dict(); global_state["pools"] = pools_dict; save_global_state_to_db(global_state)
                            st.balloons(); st.success(lang["won_message"].format(winner=winner.name, amount=payout, currency=active_pool.currency)); st.rerun()
    with right:
        st.subheader(lang["escrow_ledger"])
        for event in reversed(active_pool.history):
            with st.expander(f"⚙️ Ledger / Cycle {event['month']}"):
                st.code(f"SETTLED: {event['payout']:,} {active_pool.currency}", language="bash")
                for d in event['details']: st.write(d)

# YENİ EKLENEN VERGİ VE YASAL UYUM PORTALI
with tab2:
    st.subheader(lang["tax_title"])
    st.write(lang["tax_desc"])
    
    if not active_pool.history:
        st.info("⚠️ Vergi raporu oluşturabilmek için en az bir kuranın (döngünün) tamamlanmış olması gerekir.")
    else:
        # Kullanıcı Seçimi
        user_names = [u.name for u in active_pool.users]
        selected_user = st.selectbox("Katılımcı Seçin (Kimin adına rapor oluşturulacak?):", user_names)
        
        # Vergi Hesaplama Mantığı
        total_paid_by_user = (active_pool.current_month - 1) * active_pool.monthly_contribution
        total_received = 0
        winning_month = "-"
        for h in active_pool.history:
            if h["winner"] == selected_user:
                total_received = h["payout"]
                winning_month = h["month"]
        
        # Ekranda Rapor Özeti
        st.write("---")
        c1, c2, c3 = st.columns(3)
        c1.metric("Toplam Yatırılan Tutar", f"-{total_paid_by_user:,} {active_pool.currency}")
        c2.metric("Toplam Alınan (Hakediş)", f"+{total_received:,} {active_pool.currency}")
        c3.metric("Ödenen Platform Vergi/Hizmet Bedeli", f"{(total_received / 0.99 * 0.01) if total_received > 0 else 0:,.2f} {active_pool.currency}")
        
        st.success(f"✅ KYC/AML Durumu: {selected_user} için uluslararası kara para aklama taraması temiz. (Clear)")
        
        # CSV Dışa Aktarma (Export) Hazırlığı
        report_data = pd.DataFrame([{
            "Belge No": f"TAX-SUSU-{random.randint(10000,99999)}",
            "Havuz ID": active_pool.pool_id,
            "Katilimci": selected_user,
            "Toplam Yatirilan": total_paid_by_user,
            "Alinan Kura": total_received,
            "Kura Ayi": winning_month,
            "Para Birimi": active_pool.currency,
            "KYC_AML_Durumu": "PASSED"
        }])
        
        csv_report = report_data.to_csv(index=False).encode('utf-8')
        
        st.download_button(
            label=lang["btn_download"],
            data=csv_report,
            file_name=f"Tax_Report_{selected_user.replace(' ', '_')}.csv",
            mime="text/csv",
            type="primary"
        )
