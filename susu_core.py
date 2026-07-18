import streamlit as st
import random
import pandas as pd
import requests
import time
import plotly.graph_objects as go
import yfinance as yf
from datetime import datetime

# Sayfa Ayarları
st.set_page_config(page_title="Susu Global | Enterprise WealthTech", page_icon="🏦", layout="wide", initial_sidebar_state="expanded")

# ==========================================
# 🎨 ÖZEL CSS & STİL
# ==========================================
st.markdown("""
<style>
    div[data-testid="stMetricValue"] { font-size: 24px !important; font-weight: 700 !important; color: #111827 !important; }
    div[data-testid="stMetricLabel"] { font-size: 13px !important; font-weight: 600 !important; color: #6b7280 !important; }
    .login-box { background-color: white; padding: 2.5rem; border-radius: 16px; box-shadow: 0 10px 30px rgba(0,0,0,0.08); border: 1px solid #e5e7eb; }
    .cc-box { background: linear-gradient(135deg, #1f2937 0%, #111827 100%); color: white; padding: 15px; border-radius: 8px; margin-bottom: 15px; font-family: monospace;}
    .client-card { background: linear-gradient(135deg, #f0fdf4 0%, #dcfce7 100%); border: 1px solid #bbf7d0; padding: 20px; border-radius: 12px; }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 🌍 VERİ TABANI & BAĞLANTILAR
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
# 🔐 KİMLİK DOĞRULAMA (RBAC) SİSTEMİ
# ==========================================
if "role" not in st.session_state: st.session_state["role"] = None
if "current_user" not in st.session_state: st.session_state["current_user"] = None
if "current_pool" not in st.session_state: st.session_state["current_pool"] = None

if st.session_state["role"] is None:
    st.markdown("<br><br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 1.2, 1])
    with col2:
        st.markdown("<div class='login-box'>", unsafe_allow_html=True)
        st.markdown("<h2 style='text-align: center;'>Susu Global <span style='color:#16a34a;'>OS</span></h2>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: #6b7280; margin-bottom: 20px;'>Kurumsal & Bireysel Giriş Portalı</p>", unsafe_allow_html=True)
        
        login_type = st.radio("Giriş Türü", ["Yönetici (Admin)", "Yatırımcı (Client)"], horizontal=True)
        
        with st.form("login_form"):
            if login_type == "Yönetici (Admin)":
                username = st.text_input("Yetkili ID")
                password = st.text_input("Güvenlik Anahtarı", type="password")
            else:
                username = st.text_input("Adınız Soyadınız (Sisteme Kayıtlı)")
                password = st.text_input("Müşteri Şifresi (1234)", type="password")
                
            if st.form_submit_button("Sisteme Giriş Yap", type="primary", use_container_width=True):
                if login_type == "Yönetici (Admin)":
                    if username == "admin" and password == "susu2026":
                        st.session_state["role"] = "admin"; st.success("✅ Yetkili girişi başarılı."); time.sleep(1); st.rerun()
                    else: st.error("❌ Hatalı yetkili bilgisi!")
                else:
                    found = False
                    for p_id, p_data in global_state["pools"].items():
                        for u in p_data["users"]:
                            if u["name"].strip().lower() == username.strip().lower() and password == "1234":
                                st.session_state["role"] = "client"
                                st.session_state["current_user"] = u
                                st.session_state["current_pool"] = p_data
                                found = True
                                break
                        if found: break
                    if found: st.success(f"✅ Hoş geldin, {username}!"); time.sleep(1); st.rerun()
                    else: st.error("❌ Kullanıcı bulunamadı veya şifre hatalı!")
        st.markdown("</div>", unsafe_allow_html=True)
    st.stop()

def logout():
    st.session_state["role"] = None; st.session_state["current_user"] = None; st.session_state["current_pool"] = None; st.rerun()

# ==========================================
# 🌐 ORTAK ÜST BAR
# ==========================================
t1, t2, t3, t4 = st.columns(4)
with t1: btc_color = "normal" if live_market['BTC']['change'] >= 0 else "inverse"; st.metric("BTC/USD", f"${live_market['BTC']['price']:,.2f}", f"{live_market['BTC']['change']*100:.2f}%", delta_color=btc_color)
with t2: gold_color = "normal" if live_market['GOLD']['change'] >= 0 else "inverse"; st.metric("XAU/USD", f"${live_market['GOLD']['price']:,.2f}", f"{live_market['GOLD']['change']*100:.2f}%", delta_color=gold_color)
with t3: etf_color = "normal" if live_market['ETF']['change'] >= 0 else "inverse"; st.metric("US Temettü ETF", f"${live_market['ETF']['price']:,.2f}", f"{live_market['ETF']['change']*100:.2f}%", delta_color=etf_color)
with t4: 
    if st.session_state["role"] == "client": st.metric("Bağlı Havuz", st.session_state["current_pool"]["pool_name"].replace("🏦 ", ""), delta_color="off")
    else: st.metric("Sistem Durumu", "Online", "v18.0", delta_color="normal")
st.divider()

# ==========================================
# 🤵 MÜŞTERİ (CLIENT) PORTALI
# ==========================================
if st.session_state["role"] == "client":
    user_data = st.session_state["current_user"]
    pool_data = st.session_state["current_pool"]
    
    with st.sidebar:
        st.image("https://cdn-icons-png.flaticon.com/512/3135/3135715.png", width=50)
        st.markdown(f"### {user_data['name']}")
        st.caption("Bireysel Yatırımcı Portalı")
        st.button("🚪 Çıkış Yap", on_click=logout, use_container_width=True)
    
    st.markdown(f"<h2>Hoş Geldin, {user_data['name']} 👋</h2>", unsafe_allow_html=True)
    st.markdown(f"Şu anda **{pool_data['pool_name']}** fonundasın ve fon **{pool_data['strategy']}** stratejisi ile yönetiliyor.")
    
    colA, colB, colC = st.columns(3)
    with colA:
        st.markdown("<div class='client-card'>", unsafe_allow_html=True)
        st.metric("Susu Güven Puanın", f"{user_data.get('trust_score', 50)} ⭐")
        st.caption("Puanın ne kadar yüksekse, erken çekim şansın o kadar artar.")
        st.markdown("</div>", unsafe_allow_html=True)
    with colB:
        st.markdown("<div class='client-card'>", unsafe_allow_html=True)
        pay_status = "✅ Ödendi" if user_data.get('has_paid') else "⏳ Bekleniyor"
        st.metric("Bu Ayki Katılım", f"${pool_data['monthly_contribution']}", pay_status)
        st.caption(f"Döngü: {pool_data['current_month']} / {pool_data['total_months']}")
        st.markdown("</div>", unsafe_allow_html=True)
    with colC:
        st.markdown("<div class='client-card'>", unsafe_allow_html=True)
        win_status = "🏦 Hesabına Geçti" if user_data.get('has_received') else "Sırasını Bekliyor"
        st.metric("Fon Kura Durumu", win_status)
        expected = pool_data['monthly_contribution'] * pool_data['total_months']
        st.caption(f"Beklenen Minimum Tahsilat: ${expected}")
        st.markdown("</div>", unsafe_allow_html=True)

    st.divider()

    col_doc, col_chart = st.columns([1, 2])
    with col_doc:
        st.markdown("### 📄 Belgelerim")
        if user_data.get('has_paid'):
            receipt_date = datetime.now().strftime("%d-%m-%Y %H:%M")
            receipt_text = f"=========================================\n" \
                           f"        SUSU GLOBAL WEALTHTECH\n" \
                           f"          E-TAHSİLAT MAKBUZU\n" \
                           f"=========================================\n" \
                           f"Tarih: {receipt_date}\n" \
                           f"Müşteri: {user_data['name']}\n" \
                           f"Fon Adı: {pool_data['pool_name'].replace('🏦 ', '')}\n" \
                           f"Döngü: {pool_data['current_month']}. Ay Katılımı\n" \
                           f"Tahsil Edilen Tutar: ${pool_data['monthly_contribution']}\n\n" \
                           f"İşlem Durumu: BAŞARILI (Akıllı Sözleşme Onaylı)\n" \
                           f"=========================================\n" \
                           f"Bu belge elektronik olarak Susu OS tarafından üretilmiştir."
            
            st.success("Bu ayki ödemeniz başarıyla alınmıştır.")
            st.download_button("📥 E-Dekont İndir (.txt)", data=receipt_text, file_name=f"Susu_Dekont_{user_data['name'].replace(' ', '_')}.txt", use_container_width=True)
        else:
            st.info("ℹ️ Bu ayki ödemenizi henüz yapmadığınız için güncel dekontunuz oluşmamıştır.")

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("### ⚖️ Yasal Uyarı")
        with st.expander("Risk Sözleşmesini Görüntüle"):
            st.warning("Kripto para (BTC) ve Temettü (ETF) piyasaları yüksek volatilite içerebilir. Seçilen yatırım stratejisine bağlı olarak fonlarda kısa süreli dalgalanmalar yaşanabilir. Susu Global algoritması kârı maksimize etmeyi hedefler ancak kesin kazanç garantisi sunmaz. Yatırımlarınız uluslararası piyasa koşullarına tabidir.")

    with col_chart:
        st.markdown("### 📊 Havuz Getiri Performansı")
        if pool_data["history"]:
            months = [f"Döngü {h['month']}" for h in pool_data["history"]]
            yields = [h.get("yield", 0) for h in pool_data["history"]]
            fig = go.Figure()
            colors = ['#ef4444' if y < 0 else '#10b981' for y in yields]
            fig.add_trace(go.Bar(x=months, y=yields, marker_color=colors, name="Getiri"))
            fig.update_layout(xaxis_title="Aylar", yaxis_title="Net Getiri (USD)", plot_bgcolor='rgba(0,0,0,0)', margin=dict(l=0, r=0, t=30, b=0))
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Havuz henüz kura dağıtımı yapmamış. Getiri grafikleri ilk dağıtımdan sonra burada görünecektir.")

# ==========================================
# 👑 YÖNETİCİ (ADMIN) PORTALI
# ==========================================
elif st.session_state["role"] == "admin":
    pools_dict = global_state["pools"]
    if not pools_dict:
        st.warning("Hiç havuz yok. Yeni bir havuz oluşturuluyor...")
        default = {"Global-Alpha": {"pool_id": "Global-Alpha", "pool_name": "🌐 Global Alpha Pool", "currency": "USD", "monthly_contribution": 1000, "total_months": 4, "current_month": 1, "total_yield": 0.0, "strategy": "🤖 Smart Yield (Otomatik)", "users": [], "history": []}}
        save_global_state_to_db({"pools": default}); st.rerun()

    with st.sidebar:
        st.image("https://cdn-icons-png.flaticon.com/512/2953/2953363.png", width=50)
        st.markdown("### Susu Global Admin")
        st.button("🚪 Güvenli Çıkış", on_click=logout, use_container_width=True)
        st.divider()
        
        selected_pool_id = st.selectbox("📂 Aktif Portföy", options=list(pools_dict.keys()), format_func=lambda x: pools_dict[x]["pool_name"])
        p_data = pools_dict[selected_pool_id]
        active_users = p_data["users"]
        current_month = p_data["current_month"]
        total_months = p_data["total_months"]
        is_completed = current_month > total_months

        st.markdown("#### ⚙️ Portföy Stratejisi")
        strategies = ["🤖 Smart Yield (Otomatik)", "🌙 Katılım (Altın Endeksli)", "🏦 Geleneksel (US ETF)", "⚡ Yüksek Risk (Bitcoin)"]
        current_strat_idx = strategies.index(p_data["strategy"]) if p_data.get("strategy") in strategies else 0
        selected_strategy = st.selectbox("Emanet Kasa", strategies, index=current_strat_idx)
        if selected_strategy != p_data.get("strategy"):
            p_data["strategy"] = selected_strategy; save_global_state_to_db(global_state); st.rerun()

        st.divider()
        st.markdown("#### 👤 Yeni Müşteri Ekle")
        with st.form("onboard_form", clear_on_submit=True):
            name = st.text_input("Ad Soyad")
            country = st.selectbox("Bölge", ["TR-Istanbul", "US-NewYork", "UK-London"])
            if st.form_submit_button("Ağa Ekle"):
                if len(active_users) >= total_months: st.error("Havuz dolu.")
                else:
                    p_data["users"].append({"user_id": len(active_users)+1, "name": name, "country": country, "has_paid": False, "has_received": False, "trust_score": random.randint(60, 95)})
                    save_global_state_to_db(global_state); st.rerun()
                    
        st.divider()
        st.markdown("#### ➕ Yeni Havuz")
        with st.form("create_pool_form", clear_on_submit=True):
            new_pool_name = st.text_input("Adı", placeholder="Örn: US Temettü Fonu")
            new_pool_amount = st.number_input("Aylık", min_value=50, step=50, value=500)
            new_pool_months = st.number_input("Kapasite", min_value=2, max_value=24, value=5)
            if st.form_submit_button("Başlat"):
                if new_pool_name:
                    new_id = f"{new_pool_name.replace(' ', '-')}-{random.randint(1000,9999)}"
                    pools_dict[new_id] = {"pool_id": new_id, "pool_name": f"🏦 {new_pool_name}", "currency": "USD", "monthly_contribution": new_pool_amount, "total_months": new_pool_months, "current_month": 1, "total_yield": 0.0, "strategy": "🤖 Smart Yield (Otomatik)", "users": [], "history": []}
                    save_global_state_to_db(global_state); st.success("Oluşturuldu!"); time.sleep(1); st.rerun()

    col_title, col_status = st.columns([3, 1])
    with col_title: st.markdown(f"<h2>{p_data['pool_name']}</h2>", unsafe_allow_html=True)
    with col_status:
        if is_completed: st.success("✅ Döngü Tamamlandı")
        else: st.info(f"⏳ Döngü {current_month} / {total_months}")

    with st.container(border=True):
        mc1, mc2, mc3, mc4 = st.columns(4)
        with mc1: st.metric("Aylık Katılım", f"{p_data['monthly_contribution']:,} USD")
        with mc2: st.metric("Kümülatif Getiri", f"{p_data.get('total_yield', 0):+,.2f} USD")
        with mc3: st.metric("Havuz Kapasitesi", f"{len(active_users)} / {total_months} Kişi")
        with mc4: st.metric("Ortalama Güven", f"{int(sum(u.get('trust_score', 50) for u in active_users)/len(active_users)) if active_users else 0} ⭐")

    tab1, tab2 = st.tabs(["⚡ Operasyon Merkezi", "🚀 Dağıtım Logları"])

    with tab1:
        st.markdown("### 👥 Tahsilat & Pos Sistemi")
        if not active_users: st.warning("Sol menüden müşteri ekleyin.")
        else:
            df = pd.DataFrame([{"Müşteri": u['name'], "Bölge": u['country'], "Ödeme": "✅" if u['has_paid'] else "⏳", "Durum": "🏦 Kazandı" if u['has_received'] else "Bekliyor"} for u in active_users])
            st.dataframe(df, use_container_width=True, hide_index=True)
            
            if not is_completed:
                with st.container(border=True):
                    pay_cols = st.columns(min(len(active_users), 6))
                    for idx, u in enumerate(active_users):
                        with pay_cols[idx % 6]:
                            if u['has_paid']: 
                                st.success(f"{u['name']}")
                            else:
                                with st.popover(f"💳 {u['name'][:8]}", use_container_width=True):
                                    st.markdown(f"<div class='cc-box'>Susu Card<br>**** 4092<br>Tutar: ${p_data['monthly_contribution']}</div>", unsafe_allow_html=True)
                                    with st.form(f"pos_{p_data['pool_id']}_{u.get('user_id', idx)}"):
                                        if st.form_submit_button("🔒 Çekim Yap", type="primary", use_container_width=True):
                                            p_data["users"][idx]["has_paid"] = True; save_global_state_to_db(global_state); st.rerun()

                if len(active_users) >= total_months and all(u['has_paid'] for u in active_users):
                    st.info(f"ℹ️ Fonlar gerçek zamanlı {p_data['strategy']} piyasasına aktarıldı.")
                    if st.button("🚀 CANLI PİYASA GETİRİSİNİ HESAPLA VE DAĞIT", type="primary", use_container_width=True):
                        eligible_indices = [i for i, u in enumerate(active_users) if not u['has_received']]
                        if eligible_indices:
                            with st.spinner("API verisi çekiliyor..."):
                                time.sleep(1)
                                collected = p_data["monthly_contribution"] * total_months
                                rate_gold = live_market['GOLD']['change']; rate_etf = live_market['ETF']['change']; rate_btc = live_market['BTC']['change']
                                strat = p_data["strategy"]
                                if "Katılım" in strat: final_rate = rate_gold; detail = f"XAU (%{final_rate*100:.2f})"
                                elif "Geleneksel" in strat: final_rate = rate_etf; detail = f"SCHD (%{final_rate*100:.2f})"
                                elif "Yüksek Risk" in strat: final_rate = rate_btc; detail = f"BTC (%{final_rate*100:.2f})"
                                else:
                                    best, final_rate = max([("Altın", rate_gold), ("US ETF", rate_etf), ("Bitcoin", rate_btc)], key=lambda x: x[1])
                                    detail = f"Smart Opt: {best} (%{final_rate*100:.2f})"

                                generated_yield = collected * final_rate
                                p_data["total_yield"] = p_data.get("total_yield", 0) + generated_yield
                                winner_idx = random.choice(eligible_indices)
                                p_data["users"][winner_idx]["has_received"] = True
                                payout = collected * 0.99 
                                p_data["history"].append({"month": current_month, "winner": active_users[winner_idx]['name'], "payout": payout, "yield": generated_yield, "strat_detail": detail})
                                p_data["current_month"] += 1
                                for u in p_data["users"]: u["has_paid"] = False
                                save_global_state_to_db(global_state); st.rerun()

    with tab2:
        st.markdown("### 🛡️ Dağıtım Geçmişi")
        if not p_data["history"]: st.caption("İşlem yok.")
        for event in reversed(p_data["history"]):
            st.markdown(f"**Döngü {event['month']}** | Kazanan: **{event['winner']}** (Net: {event['payout']:,} USD) | API: {event.get('strat_detail', '')}")
            st.divider()