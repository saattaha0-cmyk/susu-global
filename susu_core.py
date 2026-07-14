import streamlit as st
import json
import random
import pandas as pd
import requests

# Sayfa Ayarları
st.set_page_config(page_title="Susu Global - Community Finance", page_icon="🌐", layout="wide")

# Streamlit Secrets (Şifreler) Kontrolü
SUPABASE_URL = st.secrets.get("SUPABASE_URL")
SUPABASE_KEY = st.secrets.get("SUPABASE_KEY")

# ==========================================
# AKILLI URL TEMİZLEYİCİ (URL CLEANER)
# ==========================================
def get_clean_base_url():
    """Kullanıcının kopyaladığı URL'deki fazlalıkları (eğik çizgi veya /rest/v1) temizler."""
    if not SUPABASE_URL:
        return ""
    
    url = SUPABASE_URL.strip()
    
    # Eğer url sonunda eğik çizgi varsa temizle
    if url.endswith("/"):
        url = url[:-1]
        
    # Eğer kullanıcı adresi zaten /rest/v1 ile kopyaladıysa, o kısmı temizle (çift yazılmasın diye)
    if "/rest/v1" in url:
        url = url.replace("/rest/v1", "")
        if url.endswith("/"):
            url = url[:-1]
            
    return url

# ==========================================
# VERİTABANI BAĞLANTI FONKSİYONLARI (API)
# ==========================================

def load_state_from_db():
    """Supabase bulut veritabanından güncel durumu çeker."""
    base_url = get_clean_base_url()
    if not base_url or not SUPABASE_KEY:
        st.warning("⚠️ Streamlit Secrets ayarlarında SUPABASE_URL veya SUPABASE_KEY eksik!")
        return None
    
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}"
    }
    # Temiz URL ile tam endpoint adresi oluşturuluyor
    url = f"{base_url}/rest/v1/susu_state?id=eq.US-GLOBAL-01"
    
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            rows = response.json()
            if rows:
                return rows[0]["data"]
            else:
                st.info("ℹ️ Veritabanında başlangıç verisi bulunamadı, yeni oluşturuluyor...")
                default_data = {"pool_id": "US-GLOBAL-01", "currency": "USD", "monthly_contribution": 1000, "total_months": 4, "current_month": 1, "users": [], "history": []}
                save_state_to_db(default_data)
                return default_data
        else:
            st.error(f"❌ Veritabanı Bağlantı Hatası (Kod {response.status_code}): {response.text}")
    except Exception as e:
        st.error(f"❌ Veritabanı Bağlantı Hatası: {e}")
    return None

def save_state_to_db(data_dict):
    """Supabase bulut veritabanına güncel durumu kaydeder."""
    base_url = get_clean_base_url()
    if not base_url or not SUPABASE_KEY:
        st.error("⚠️ Kaydedilemedi: API anahtarları eksik.")
        return False
    
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "resolution=merge-duplicates"
    }
    url = f"{base_url}/rest/v1/susu_state"
    payload = {
        "id": "US-GLOBAL-01",
        "data": data_dict
    }
    
    try:
        response = requests.post(url, headers=headers, json=[payload])
        if response.status_code in [200, 201]:
            return True
        else:
            st.error(f"❌ Veri Kaydetme Hatası (Kod {response.status_code}): {response.text}")
            return False
    except Exception as e:
        st.error(f"❌ Veri Kaydetme Hatası: {e}")
        return False

# ==========================================
# GİRİŞİM MANTIĞI VE SINIFLARI (CORE LOGIC)
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
        return {
            "user_id": self.user_id,
            "name": self.name,
            "country": self.country,
            "passport_verified": self.passport_verified,
            "credit_score": self.credit_score,
            "has_paid": self.has_paid,
            "has_received": self.has_received
        }

class SusuPool:
    def __init__(self, pool_id, currency, monthly_contribution, total_months, current_month=1, history=None):
        self.pool_id = pool_id
        self.currency = currency
        self.monthly_contribution = monthly_contribution
        self.total_months = total_months
        self.current_month = current_month
        self.users = []
        self.history = history if history is not None else []

    def add_user(self, name, country, passport, credit_score):
        if len(self.users) >= self.total_months:
            return False, "Pool is already full!"
        
        user_id = len(self.users) + 1
        passport_ok = True if (passport and len(passport) >= 6) else False
        
        new_user = SusuUser(user_id, name, country, passport_ok, credit_score)
        self.users.append(new_user)
        
        if self.save_to_cloud():
            return True, f"User {name} successfully onboarded!"
        else:
            self.users.pop()
            return False, "Database save failed. Please check the red error box above."

    def run_cycle(self):
        eligible = [u for u in self.users if not u.has_received]
        if not eligible:
            return False, "All cycles completed!"

        total_collected = 0
        details = []
        fee_rate = 0.01
        
        for u in self.users:
            u.has_paid = True
            total_collected += self.monthly_contribution
            if u.credit_score >= 500:
                details.append(f"✅ {u.name} paid {self.monthly_contribution:,} {self.currency}")
            else:
                details.append(f"🛡️ BaaS Escrow Guarantee covered {u.name} for {self.monthly_contribution:,} {self.currency}")

        platform_fee = total_collected * fee_rate
        payout_amount = total_collected - platform_fee

        winner = random.choice(eligible)
        winner.has_received = True

        log_entry = {
            "month": self.current_month,
            "winner": winner.name,
            "payout": payout_amount,
            "fee": platform_fee,
            "details": details
        }
        self.history.append(log_entry)
        
        self.current_month += 1
        for u in self.users:
            u.has_paid = False
            
        if self.save_to_cloud():
            return True, f"{winner.name} received {payout_amount:,} {self.currency}"
        return False, "Failed to save cycle to cloud database."

    def to_dict_for_db(self):
        return {
            "pool_id": self.pool_id,
            "currency": self.currency,
            "monthly_contribution": self.monthly_contribution,
            "total_months": self.total_months,
            "current_month": self.current_month,
            "users": [u.to_dict() for u in self.users],
            "history": self.history
        }

    def save_to_cloud(self):
        return save_state_to_db(self.to_dict_for_db())

    @classmethod
    def load_from_cloud(cls):
        db_data = load_state_from_db()
        if db_data:
            pool = cls(
                pool_id=db_data["pool_id"],
                currency=db_data["currency"],
                monthly_contribution=db_data["monthly_contribution"],
                total_months=db_data["total_months"],
                current_month=db_data["current_month"],
                history=db_data.get("history", [])
            )
            for u in db_data["users"]:
                user = SusuUser(u["user_id"], u["name"], u["country"], u["passport_verified"], u["credit_score"], u["has_paid"], u["has_received"])
                pool.users.append(user)
            return pool
        return None

# ==========================================
# WEB PORTAL ARAYÜZÜ (STREAMLIT)
# ==========================================

pool = SusuPool.load_from_cloud()
if pool is None:
    pool = SusuPool(pool_id="US-GLOBAL-01", currency="USD", monthly_contribution=1000, total_months=4)

# Yan Panel
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2953/2953363.png", width=80)
    st.title("Susu Global Admin")
    st.caption("🔒 Secured with Supabase PostgreSQL")
    st.write("---")
    
    st.subheader("KYC & Onboard New User")
    with st.form("onboard_form", clear_on_submit=True):
        name = st.text_input("Full Name")
        country = st.selectbox("Country of Residence", ["United States", "United Kingdom", "Germany", "Turkey", "Nigeria", "Mexico"])
        passport = st.text_input("Passport Number (for KYC verification)")
        score = st.slider("Financial Credit Score", 300, 850, 720)
        submit = st.form_submit_button("Verify & Add to Pool")
        
        if submit and name:
            success, msg = pool.add_user(name, country, passport, score)
            if success:
                st.success(msg)
                st.rerun()
            else:
                st.error(msg)
                
    st.write("---")
    if st.button("🚨 Reset Cloud Database", use_container_width=True):
        default_state = {
            "pool_id": "US-GLOBAL-01",
            "currency": "USD",
            "monthly_contribution": 1000,
            "total_months": 4,
            "current_month": 1,
            "users": [],
            "history": []
        }
        if save_state_to_db(default_state):
            st.success("Cloud database successfully cleared!")
            st.rerun()

# Ana Sayfa Giriş
st.title("🌐 SUSU GLOBAL: ROTATIONAL SAVINGS NETWORK")
st.write("Secure, cross-border decentralized social savings with institutional Escrow Guarantee.")

# Yatırımcı Paneli (Pitch Metrics)
st.subheader("📈 Investor Dashboard (SaaS Metrics)")
col1, col2, col3, col4 = st.columns(4)

total_volume = sum([h['payout'] for h in pool.history])
total_revenue = sum([h['fee'] for h in pool.history])

with col1:
    st.metric(label="Total Transaction Volume (GMV)", value=f"{total_volume:,} {pool.currency}")
with col2:
    st.metric(label="Platform Revenue (%1 SaaS Fee)", value=f"{total_revenue:,} {pool.currency}")
with col3:
    st.metric(label="Active Users In Pool", value=f"{len(pool.users)} / {pool.total_months}")
with col4:
    st.metric(label="Current Cycle Phase", value=f"Month {pool.current_month} of {pool.total_months}")

st.write("---")

left, right = st.columns([2, 1])

with left:
    st.subheader("👥 Verified Pool Participants (Live Cloud)")
    if not pool.users:
        st.info("No verified users in this pool yet. Please use the KYC Onboarding panel on the left.")
    else:
        user_list = []
        for u in pool.users:
            kyc_status = "🛡️ VERIFIED (KYC)" if u.passport_verified else "❌ UNVERIFIED"
            payout_status = "🎁 Received Funds" if u.has_received else "⏳ Waiting Cycle"
            user_list.append({
                "User ID": u.user_id,
                "Name": u.name,
                "Region": u.country,
                "KYC Verification": kyc_status,
                "FICO Score": u.credit_score,
                "Status": payout_status
            })
        st.dataframe(pd.DataFrame(user_list), use_container_width=True, hide_index=True)
        
        st.write("")
        if len(pool.users) < pool.total_months:
            st.warning(f"Waiting for pool to fill. Need {pool.total_months - len(pool.users)} more verified user(s) to start the smart escrow contract.")
        else:
            if st.button("🔌 Execute Monthly Escrow & Draw Winner", type="primary", use_container_width=True):
                success, msg = pool.run_cycle()
                if success:
                    st.balloons()
                    st.success(msg)
                    st.rerun()
                else:
                    st.error(msg)

with right:
    st.subheader("🛡️ Escrow Ledger (Live Audit)")
    if not pool.history:
        st.info("No escrow transactions recorded yet.")
    else:
        for event in reversed(pool.history):
            with st.expander(f"📅 Cycle Month {event['month']} Audit"):
                st.write(f"**Escrow Release Amount:** {event['payout']:,} {pool.currency}")
                st.write(f"**Susu Platform Take Rate:** {event['fee']:,} {pool.currency}")
                st.write("**On-Chain Escrow Clearings:**")
                for d in event['details']:
                    st.write(d)