import streamlit as st
import random
import pandas as pd
import requests
import time
import plotly.graph_objects as go
import yfinance as yf
from datetime import datetime

# ==========================================
# ⚙️ SAYFA & CSS AYARLARI (Mobil Odaklı)
# ==========================================
st.set_page_config(page_title="Susu Global | WealthTech", page_icon="🏦", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
    /* Temel Metrik ve Font Ayarları */
    div[data-testid="stMetricValue"] { font-size: 22px !important; font-weight: 800 !important; color: #111827 !important; }
    div[data-testid="stMetricLabel"] { font-size: 13px !important; font-weight: 600 !important; color: #6b7280 !important; }
    
    /* Login Ekranı Ortalaması ve Gölgeler */
    .login-box { background-color: #ffffff; padding: 2.5rem; border-radius: 16px; box-shadow: 0 10px 40px rgba(0,0,0,0.08); border: 1px solid #f3f4f6; margin-top: 5vh; }
    
    /* Mobil Uyumlu Kredi Kartı ve Kullanıcı Kartları */
    .cc-box { background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%); color: #f8fafc; padding: 18px; border-radius: 12px; margin-bottom: 15px; font-family: monospace; letter-spacing: 1px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
    .client-card { background: linear-gradient(135deg, #f0fdf4 0%, #dcfce7 100%); border: 1px solid #bbf7d0; padding: 15px; border-radius: 12px; height: 100%; }
    .ai-card { background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%); border-left: 4px solid #3b82f6; padding: 15px; border-radius: 8px; font-size: 14px; }
    .kyc-warning { background-color: #fffbeb; border-left: 4px solid #f59e0b; padding: 15px; border-radius: 8px; margin-bottom: 20px; font-size: 14px; }
    
    /* Sekme (Tab) Tasarımlarını Temizleme */
    .stTabs [data-baseweb="tab-list"] { gap: 8px; border-bottom: 1px solid #e5e7eb; padding-bottom: 0; }
    .stTabs [data-baseweb="tab"] { font-weight: 600; color: #6b7280; padding: 10px 16px; }
    .stTabs [aria-selected="true"] { color: #16a34a !important; border-bottom: 3px solid #16a34a !important; background-color: #f0fdf4; border-radius: 8px 8px 0 0; }
    
    /* Butonları daha yumuşak yapma */
    .stButton>button { border-radius: 8px; font-weight: 600; }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 🌍 VERİ TABANI & CANLI PİYASA
# ==========================================
SUPABASE_URL = st.secrets.get("SUPABASE_URL")
SUPABASE_KEY = st.secrets.get("SUPABASE_KEY")

def get_clean_base_url():
    if not SUPABASE_URL: return ""
    url = SUPABASE_URL.strip()
    if url.endswith("/"): url = url[:-1]
    if "/rest/v1" in url: url = url.replace("/rest/v1", ""); url = url.rstrip("/")
    return url

def load_global_state_from_db():
    base_url = get_clean_base_url()
    if not base_url or not SUPABASE_KEY: return {"pools": {}}
    headers = {"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}"}
    try:
        res = requests.get(f"{base_url}/rest/v1/susu_state?id=eq.US-GLOBAL-01", headers=headers)
        if res.status_code == 200 and res.json() and "pools" in res.json()[0]["data"]: return res.json()[0]["data"]
    except: pass
    return {"pools": {}}

def save_global_state_to_db(global_state_dict):
    base_url = get_clean_base_url()
    if not base_url or not SUPABASE_KEY: return False
    headers = {"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}", "Content-Type": "application/json", "Prefer": "resolution=merge-duplicates"}
    try: 
        res = requests.post(f"{base_url}/rest/v1/susu_state", headers=headers, json=[{"id": "US-GLOBAL-01", "data": global_state_dict}])
        return res.status_code in [200, 201]
    except: return False

global_state = load_global_state_from_db()

@st.cache_data(ttl=300) 
def get_live_market_data():
    rates = {"BTC": {"price": 0, "change": 0}, "GOLD": {"price": 0, "change": 0}, "ETF": {"price": 0, "change": 0}}
    try:
        assets = {"BTC-USD": "BTC", "GC=F": "GOLD", "SCHD": "ETF"}
        for symbol, name in assets.items():
            tk = yf.Ticker(symbol)
            hist = tk.history(period="5d")
            if len(hist) >= 2: rates[name] = {"price": float(hist['Close'].iloc[-1]), "change": (float(hist['Close'].iloc[-1]) - float(hist['Close'].iloc[0])) / float(hist['Close'].iloc[0])}
    except: pass
    return rates

live_market = get_live_market_data()

# ==========================================
# 🔐 KİMLİK DOĞRULAMA SİSTEMİ
# ==========================================
if "role" not in st.session_state: st.session_state["role"] = None
if "current_user" not in st.session_state: st.session_state["current_user"] = None
if "current_pool" not in st.session_state: st.session_state["current_pool"] = None

if st.session_state["role"] is None:
    col1, col2, col3 = st.columns([1, 1.2, 1])
    with col2:
        st.markdown("<div class='login-box'>", unsafe_allow_html=True)
        st.markdown("<h2 style='text-align: center; margin-bottom:0;'>🏦 Susu Global</h2>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: #6b7280; margin-bottom: 25px;'>Giriş Portalı</p>", unsafe_allow_html=True)
        
        login_type = st.radio("Erişim Türü", ["Yatırımcı (Client)", "Yönetici (Admin)"], horizontal=True)
        st.markdown("<br>", unsafe_allow_html=True)
        
        with st.form("login_form"):
            if login_type == "Yönetici (Admin)":
                username = st.text_input("Yetkili ID", placeholder="admin")
                password = st.text_input("Şifre", type="password")
            else:
                username = st.text_input("Adınız Soyadınız", placeholder="Sisteme kayıtlı adınız")
                password = st.text_input("Şifre", type="password", placeholder="Örn: 1234")
                
            if st.form_submit_button("Güvenli Giriş Yap", type="primary", use_container_width=True):
                if login_type == "Yönetici (Admin)":
                    if username == "admin" and password == "susu2026":
                        st.session_state["role"] = "admin"; st.success("Giriş başarılı."); time.sleep(1); st.rerun()
                    else: st.error("Hatalı bilgi!")
                else:
                    found = False
                    for p_id, p_data in global_state["pools"].items():
                        for idx, u in enumerate(p_data["users"]):
                            if u["name"].strip().lower() == username.strip().lower() and password == "1234":
                                st.session_state["role"] = "client"
                                st.session_state["current_user"] = u
                                st.session_state["current_user_idx"] = idx
                                st.session_state["current_pool"] = p_data
                                found = True
                                break
                        if found: break
                    if found: st.success(f"Hoş geldin, {username}!"); time.sleep(1); st.rerun()
                    else: st.error("Kullanıcı bulunamadı!")
        st.markdown("</div>", unsafe_allow_html=True)
    st.stop()

def logout():
    st.session_state["role"] = None; st.session_state["current_user"] = None; st.session_state["current_pool"] = None; st.session_state.pop("current_user_idx", None); st.rerun()

# ==========================================
# 🌐 KOMPAKT ÜST BAR (Mobil Dostu)
# ==========================================
with st.expander("📈 Canlı Piyasa Terminali (Tıkla Genişlet)", expanded=False):
    t1, t2, t3 = st.columns(3)
    with t1: btc_color = "normal" if live_market['BTC']['change'] >= 0 else "inverse"; st.metric("BTC/USD", f"${live_market['BTC']['price']:,.2f}", f"{live_market['BTC']['change']*100:.2f}%", delta_color=btc_color)
    with t2: gold_color = "normal" if live_market['GOLD']['change'] >= 0 else "inverse"; st.metric("XAU/USD", f"${live_market['GOLD']['price']:,.2f}", f"{live_market['GOLD']['change']*100:.2f}%", delta_color=gold_color)
    with t3: etf_color = "normal" if live_market['ETF']['change'] >= 0 else "inverse"; st.metric("US Temettü ETF", f"${live_market['ETF']['price']:,.2f}", f"{live_market['ETF']['change']*100:.2f}%", delta_color=etf_color)

# ==========================================
# 🤵 MÜŞTERİ (CLIENT) PORTALI
# ==========================================
if st.session_state["role"] == "client":
    pool_data = global_state["pools"][st.session_state["current_pool"]["pool_id"]]
    user_idx = st.session_state["current_user_idx"]
    user_data = pool_data["users"][user_idx]
    
    with st.sidebar:
        st.markdown(f"### 👤 {user_data['name']}")
        if user_data.get("kyc_verified", False): st.success("✅ Doğrulanmış Hesap")
        else: st.warning("⚠️ Hesap Onaysız")
        st.divider()
        st.caption("Bireysel Yatırımcı Portalı")
        st.button("🚪 Çıkış Yap", on_click=logout, use_container_width=True)
    
    st.title(f"Cüzdanım")
    
    if not user_data.get("kyc_verified", False):
        st.markdown("<div class='kyc-warning'><b>⚠️ Yasal Uyarı (KYC):</b> Fon havuzundan ödeme alabilmeniz için kimlik doğrulamanızı tamamlamanız gerekmektedir.</div>", unsafe_allow_html=True)
        with st.expander("📄 Kimlik Yükle ve Doğrula"):
            st.file_uploader("Pasaport veya Kimlik Kartı", type=['jpg', 'png', 'pdf'])
            if st.button("Belgeyi Gönder", type="primary"):
                with st.spinner("İşleniyor..."): time.sleep(1.5)
                pool_data["users"][user_idx]["kyc_verified"] = True
                save_global_state_to_db(global_state); st.success("Doğrulandı!"); time.sleep(1); st.rerun()

    tab_c1, tab_c2, tab_c3, tab_c4 = st.tabs(["📊 Özet", "🎯 Planlayıcı", "📄 Belgeler", "🤖 SusuAI"])
    
    with tab_c1:
        st.caption(f"Aktif Fon: **{pool_data['pool_name']}** | Strateji: **{pool_data['strategy']}**")
        colA, colB, colC = st.columns(3)
        with colA:
            st.markdown("<div class='client-card'>", unsafe_allow_html=True)
            st.metric("Susu Puanın", f"{user_data.get('trust_score', 50)} ⭐")
            st.markdown("</div>", unsafe_allow_html=True)
        with colB:
            st.markdown("<div class='client-card'>", unsafe_allow_html=True)
            st.metric("Bu Ay Katılım", f"${pool_data['monthly_contribution']}", "✅ Ödendi" if user_data.get('has_paid') else "⏳ Bekliyor")
            st.markdown("</div>", unsafe_allow_html=True)
        with colC:
            st.markdown("<div class='client-card'>", unsafe_allow_html=True)
            st.metric("Kura Durumu", "🏦 Alındı" if user_data.get('has_received') else "Bekliyor")
            st.markdown("</div>", unsafe_allow_html=True)

        if pool_data["history"]:
            st.markdown("---")
            st.markdown("#### 📈 Getiri Performansı")
            months = [f"Döngü {h['month']}" for h in pool_data["history"]]
            yields = [h.get("yield", 0) for h in pool_data["history"]]
            fig = go.Figure()
            colors = ['#ef4444' if y < 0 else '#10b981' for y in yields]
            fig.add_trace(go.Bar(x=months, y=yields, marker_color=colors))
            fig.update_layout(margin=dict(l=0, r=0, t=10, b=0), height=250, plot_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig, use_container_width=True)

    with tab_c2:
        st.markdown("#### 🎯 Finansal Özgürlük Planlayıcısı")
        sim_col1, sim_col2 = st.columns([1, 1.5])
        with sim_col1:
            sim_monthly = st.number_input("Aylık Yatırım (USD)", min_value=50, step=50, value=pool_data['monthly_contribution'])
            sim_years = st.slider("Süre (Yıl)", 1, 15, 5)
            sim_strat = st.selectbox("Strateji", ["ABD Temettü (~%9)", "Geleneksel (%0)", "Yüksek Risk (~%20)"])
            
            annual_rate = 0.09 if "Temettü" in sim_strat else (0.20 if "Risk" in sim_strat else 0.0)
            months_total = sim_years * 12
            monthly_rate = annual_rate / 12
            
            future_value = 0
            balances, contributions = [], []
            for m in range(1, months_total + 1):
                future_value = (future_value + sim_monthly) * (1 + monthly_rate)
                balances.append(future_value)
                contributions.append(sim_monthly * m)
            
            st.metric(f"Toplam Portföy", f"${future_value:,.0f}", f"+${(future_value - (sim_monthly * months_total)):,.0f} Kâr")
            
        with sim_col2:
            fig_sim = go.Figure()
            fig_sim.add_trace(go.Scatter(x=list(range(1, months_total + 1)), y=balances, mode='lines', name='Portföy', line=dict(color='#10b981', width=3), fill='tozeroy'))
            fig_sim.add_trace(go.Scatter(x=list(range(1, months_total + 1)), y=contributions, mode='lines', name='Ana Para', line=dict(color='#6b7280', width=2, dash='dash')))
            fig_sim.update_layout(margin=dict(l=0, r=0, t=10, b=0), height=250, plot_bgcolor='rgba(0,0,0,0)', legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01))
            st.plotly_chart(fig_sim, use_container_width=True)

    with tab_c3:
        if user_data.get('has_paid'):
            receipt_date = datetime.now().strftime("%d-%m-%Y %H:%M")
            receipt_text = f"Susu OS Makbuzu\nTarih: {receipt_date}\nMüşteri: {user_data['name']}\nTutar: ${pool_data['monthly_contribution']}\nDurum: BAŞARILI"
            st.download_button("📥 E-Dekont İndir (.txt)", data=receipt_text, file_name=f"Dekont_{user_data['name']}.txt")
        else: st.info("Bu ayki ödeme bekleniyor.")
        st.caption("Risk Bildirimi: Kripto ve ETF piyasaları volatilite içerebilir.")

    with tab_c4:
        best_asset = max(live_market.items(), key=lambda x: x[1]['change'])
        st.markdown(f"<div class='ai-card'><b>SusuAI:</b> Puanın <b>{user_data.get('trust_score', 50)}</b>. Düzenli ödemeler kura şansını %15 artırır.<br><br>Günün en iyi varlığı: <b>{best_asset[0]}</b> (%{(best_asset[1]['change']*100):.2f}). Akıllı sözleşmeler devrede.</div>", unsafe_allow_html=True)

# ==========================================
# 👑 YÖNETİCİ (ADMIN) PORTALI
# ==========================================
elif st.session_state["role"] == "admin":
    pools_dict = global_state["pools"]
    if not pools_dict:
        default = {"Global-Alpha": {"pool_id": "Global-Alpha", "pool_name": "🌐 Global Alpha Pool", "currency": "USD", "monthly_contribution": 1000, "total_months": 4, "current_month": 1, "total_yield": 0.0, "strategy": "🤖 Smart Yield (Otomatik)", "users": [], "history": []}}
        save_global_state_to_db({"pools": default}); st.rerun()

    with st.sidebar:
        st.markdown("### 👑 Admin Paneli")
        st.button("🚪 Güvenli Çıkış", on_click=logout, use_container_width=True)
        st.divider()
        
        selected_pool_id = st.selectbox("📂 Aktif Havuz", options=list(pools_dict.keys()), format_func=lambda x: pools_dict[x]["pool_name"])
        p_data = pools_dict[selected_pool_id]
        active_users, current_month, total_months = p_data["users"], p_data["current_month"], p_data["total_months"]
        is_completed = current_month > total_months

        strategies = ["🤖 Smart Yield (Otomatik)", "🌙 Katılım (Altın Endeksli)", "🏦 Geleneksel (US ETF)", "⚡ Yüksek Risk (Bitcoin)"]
        current_strat_idx = strategies.index(p_data["strategy"]) if p_data.get("strategy") in strategies else 0
        selected_strategy = st.selectbox("Strateji", strategies, index=current_strat_idx)
        if selected_strategy != p_data.get("strategy"): p_data["strategy"] = selected_strategy; save_global_state_to_db(global_state); st.rerun()

        # Kalabalığı önlemek için Expander kullanımı
        with st.expander("👤 Yeni Müşteri Ekle"):
            with st.form("onboard_form", clear_on_submit=True):
                name = st.text_input("Ad Soyad")
                if st.form_submit_button("Ağa Ekle"):
                    if len(active_users) >= total_months: st.error("Havuz dolu.")
                    else:
                        p_data["users"].append({"user_id": len(active_users)+1, "name": name, "country": "Global", "has_paid": False, "has_received": False, "trust_score": random.randint(60, 95), "kyc_verified": False})
                        save_global_state_to_db(global_state); st.rerun()
                        
        with st.expander("➕ Yeni Havuz Kur"):
            with st.form("create_pool_form", clear_on_submit=True):
                new_pool_name = st.text_input("Adı")
                new_pool_amount = st.number_input("Aylık", 50, step=50, value=500)
                new_pool_months = st.number_input("Kapasite", 2, value=5)
                if st.form_submit_button("Başlat"):
                    if new_pool_name:
                        new_id = f"{new_pool_name.replace(' ', '-')}-{random.randint(1000,9999)}"
                        pools_dict[new_id] = {"pool_id": new_id, "pool_name": f"🏦 {new_pool_name}", "currency": "USD", "monthly_contribution": new_pool_amount, "total_months": new_pool_months, "current_month": 1, "total_yield": 0.0, "strategy": "🤖 Smart Yield (Otomatik)", "users": [], "history": []}
                        save_global_state_to_db(global_state); st.rerun()

    st.markdown(f"### {p_data['pool_name']}")
    
    with st.container(border=True):
        mc1, mc2, mc3 = st.columns(3)
        with mc1: st.metric("Durum", f"Döngü {current_month}/{total_months}")
        with mc2: st.metric("Kümülatif Getiri", f"{p_data.get('total_yield', 0):+,.2f} USD")
        with mc3: st.metric("Aylık Hacim", f"${p_data['monthly_contribution'] * len(active_users):,}")

    tab_a1, tab_a2, tab_a3 = st.tabs(["⚡ Operasyon", "🚀 Loglar", "🤖 SusuAI"])

    with tab_a1:
        if not active_users: st.warning("Menüden müşteri ekleyin.")
        else:
            st.markdown("#### 👥 Tahsilat Paneli")
            
            # Mobil dostu POS butonları (3'lü grid)
            if not is_completed:
                pay_cols = st.columns(3)
                for idx, u in enumerate(active_users):
                    with pay_cols[idx % 3]:
                        if u['has_paid']: st.success(f"{u['name']} ✅")
                        else:
                            with st.popover(f"💳 {u['name'][:8]}", use_container_width=True):
                                st.markdown(f"<div class='cc-box'>Tutar: ${p_data['monthly_contribution']}</div>", unsafe_allow_html=True)
                                with st.form(f"pos_{p_data['pool_id']}_{u.get('user_id', idx)}"):
                                    if st.form_submit_button("🔒 Çek", type="primary", use_container_width=True):
                                        p_data["users"][idx]["has_paid"] = True; save_global_state_to_db(global_state); st.rerun()

            st.divider()
            
            if len(active_users) >= total_months and all(u['has_paid'] for u in active_users) and not is_completed:
                if st.button("🚀 CANLI PİYASA GETİRİSİNİ HESAPLA VE DAĞIT", type="primary", use_container_width=True):
                    eligible_indices = [i for i, u in enumerate(active_users) if not u['has_received'] and u.get('kyc_verified', False)]
                    if not eligible_indices: st.error("Kura çekilemiyor! Uygun KYC onaylı kullanıcı yok.")
                    else:
                        with st.spinner("API işleniyor..."):
                            time.sleep(1)
                            collected = p_data["monthly_contribution"] * total_months
                            r_gold = live_market['GOLD']['change']; r_etf = live_market['ETF']['change']; r_btc = live_market['BTC']['change']
                            strat = p_data["strategy"]
                            if "Katılım" in strat: rate = r_gold; det = f"XAU (%{rate*100:.2f})"
                            elif "Geleneksel" in strat: rate = r_etf; det = f"SCHD (%{rate*100:.2f})"
                            elif "Risk" in strat: rate = r_btc; det = f"BTC (%{rate*100:.2f})"
                            else: best = max([("Altın", r_gold), ("ETF", r_etf), ("BTC", r_btc)], key=lambda x: x[1]); rate = best[1]; det = f"Smart: {best[0]} (%{rate*100:.2f})"

                            y_val = collected * rate
                            p_data["total_yield"] = p_data.get("total_yield", 0) + y_val
                            w_idx = random.choice(eligible_indices)
                            p_data["users"][w_idx]["has_received"] = True
                            p_data["history"].append({"month": current_month, "winner": active_users[w_idx]['name'], "payout": collected * 0.99, "yield": y_val, "strat_detail": det})
                            p_data["current_month"] += 1
                            for u in p_data["users"]: u["has_paid"] = False
                            save_global_state_to_db(global_state); st.rerun()

    with tab_a2:
        for event in reversed(p_data["history"]):
            st.markdown(f"**Döngü {event['month']}** | 👑 **{event['winner']}** (Net: ${event['payout']:,}) | {event.get('strat_detail', '')}")
            st.divider()

    with tab_a3:
        avg_trust = int(sum(u.get('trust_score', 50) for u in active_users) / len(active_users)) if active_users else 0
        kyc_count = sum(1 for u in active_users if u.get("kyc_verified", False))
        st.markdown(f"<div class='ai-card'><b>Yönetici Raporu:</b><br><br>Ortalama Güven: <b>{avg_trust}</b>. <br>KYC Onaylı: <b>{kyc_count}/{len(active_users)}</b><br>Tavsiye: Mevcut piyasa şartlarında '{p_data['strategy']}' başarılı görünüyor.</div>", unsafe_allow_html=True)
