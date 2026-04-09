import streamlit as st
import pandas as pd
import numpy as np
import sqlite3
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import io

# ==========================================
# 0. THEME & STYLING (READABILITY MAX)
# ==========================================
st.set_page_config(page_title="KhataKhat Pro | Ultimate", layout="wide", page_icon="🧿")

st.markdown("""
    <style>
    .stApp { background-color: #0F172A; color: #F8FAFC; }
    .khatakhat-card {
        background: #1E293B; border-left: 6px solid #00F2FF;
        padding: 20px; border-radius: 12px; margin-bottom: 25px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.5);
    }
    h1, h2, h3 { color: #00F2FF; font-family: sans-serif; }
    div[data-testid="stMetricValue"] { color: #10B981 !important; font-weight: 800; }
    .stButton>button {
        background: linear-gradient(90deg, #6366F1, #00F2FF);
        color: white; border: none; border-radius: 8px; font-weight: bold; width: 100%;
    }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 1. BILINGUAL DICTIONARY
# ==========================================
lex = {
    "English": {
        "m1": "📊 Dashboard", "m2": "📂 Bulk Upload", "m3": "Smart Ledger", 
        "m4": "🔮 AI Predictor", "m5": "🎯 Recovery Ops", "m6": "⚠️ Risk Radar",
        "m7": "📅 Action Scheduler", "m8": "🎖️ Trust Index", "m9": "⚖️ Legal Center", 
        "m10": "🏦 Bankability", "m11": "🤖 Auto-Logs", "m12": "📄 Audit Reports",
        "ai": "KhataKhat AI Brief", "wa": "WhatsApp Nudge 🚀"
    },
    "Hindi": {
        "m1": "📊 डैशबोर्ड", "m2": "📂 डेटा अपलोड", "m3": "स्मार्ट खाता", 
        "m4": "🔮 भविष्यवाणी", "m5": "🎯 वसूली केंद्र", "m6": "⚠️ जोखिम रडार",
        "m7": "📅 स्मार्ट कैलेंडर", "m8": "🎖️ भरोसा स्कोर", "m9": "⚖️ कानूनी केंद्र", 
        "m10": "🏦 बैंक योग्यता", "m11": "🤖 ऑटो-लॉग्स", "m12": "📄 ऑडिट रिपोर्ट",
        "ai": "खटाखट AI विश्लेषण", "wa": "व्हाट्सएप भेजें 🚀"
    }
}

# ==========================================
# 2. DATABASE & DATA INTEGRITY
# ==========================================
conn = sqlite3.connect('khatakhat_final_v6.db', check_same_thread=False)

def get_data():
    try:
        df = pd.read_sql("SELECT * FROM ledger", conn)
        df['due_date'] = pd.to_datetime(df['due_date'])
        return df
    except:
        return pd.DataFrame()

def save_data(df):
    df.columns = [c.lower().replace(' ', '_') for c in df.columns]
    mapping = {'customer_name': 'customer', 'payment_status': 'status', 'trust': 'trust_score'}
    df = df.rename(columns=mapping)
    df.to_sql("ledger", conn, if_exists="replace", index=False)

def generate_seeds():
    names = ["Sharma Electronics", "Verma Grocery", "Rajesh Traders", "Priya Fashion", "Malhotra Sweets"]
    data = []
    for i in range(100):
        status = np.random.choice(["Paid", "Pending"], p=[0.6, 0.4])
        data.append({
            "customer": np.random.choice(names),
            "amount": np.random.randint(5000, 85000),
            "status": status,
            "due_date": (datetime.now() + timedelta(days=np.random.randint(-30, 30))).strftime('%Y-%m-%d'),
            "trust_score": np.random.randint(300, 900)
        })
    df = pd.DataFrame(data)
    save_data(df)
    return get_data()

def ai_brief(title, msg):
    st.markdown(f"<div class='khatakhat-card'><h4 style='margin:0; color:#00F2FF;'>🤖 {title}</h4><p style='margin-top:10px;'>{msg}</p></div>", unsafe_allow_html=True)

# ==========================================
# 3. ALL 12 MODULES (FULL CODE)
# ==========================================

def mod_dashboard(df, L):
    st.title(lex[L]["m1"])
    pend = df[df['status'].str.lower() == 'pending']
    c1, c2, c3 = st.columns(3)
    c1.metric("Pending Capital", f"₹{pend['amount'].sum():,.0f}")
    c2.metric("Trust Health", int(df['trust_score'].mean()))
    c3.metric("System Status", "Live")
    fig = px.scatter_3d(df, x='amount', y='trust_score', z='status', color='status', template="plotly_dark")
    st.plotly_chart(fig, use_container_width=True)

def mod_upload(L):
    st.title(lex[L]["m2"])
    f = st.file_uploader("Upload CSV/Excel")
    if f:
        d = pd.read_csv(f) if f.name.endswith('.csv') else pd.read_excel(f)
        if st.button("Sync Data"):
            save_data(d); st.success("Database Updated!"); st.rerun()

def mod_ledger(df, L):
    st.title(lex[L]["m3"])
    st.dataframe(df, column_config={"trust_score": st.column_config.ProgressColumn("Trust")}, use_container_width=True)

def mod_predictor(df, L):
    st.title(lex[L]["m4"])
    pend = df[df['status'].str.lower() == 'pending'].copy()
    if not pend.empty:
        pend['risk'] = (900 - pend['trust_score']) / 6
        fig = px.scatter(pend, x="amount", y="risk", size="amount", color="risk", template="plotly_dark")
        st.plotly_chart(fig, use_container_width=True)
    else: st.success("No Risk Detected.")

def mod_recovery(df, L):
    st.title(lex[L]["m5"])
    pend = df[df['status'].str.lower() == 'pending']
    if not pend.empty:
        target = st.selectbox("Client", pend['customer'].unique())
        client = pend[pend['customer'] == target].iloc[0]
        st.write(f"Debt: ₹{client['amount']}")
        st.button(lex[L]["wa"])
    else: st.success("All Clear!")

def mod_risk_radar(df, L):
    st.title(lex[L]["m6"])
    fig = px.density_heatmap(df, x="amount", y="trust_score", template="plotly_dark")
    st.plotly_chart(fig, use_container_width=True)

def mod_scheduler(df, L):
    st.title(lex[L]["m7"])
    pend = df[df['status'].str.lower() == 'pending'].copy()
    pend['nudge_date'] = pend['due_date'].dt.date
    st.dataframe(pend[['customer', 'amount', 'nudge_date']].sort_values(by='nudge_date'))

def mod_trust(df, L):
    st.title(lex[L]["m8"])
    st.table(df.groupby('customer')['trust_score'].mean().sort_values(ascending=False))

def mod_legal(df, L):
    st.title(lex[L]["m9"])
    st.markdown("<div style='background:white; color:black; padding:20px;'><h3>NOTICE OF DEMAND</h3><p>Payment is required immediately.</p></div>", unsafe_allow_html=True)

def mod_bankability(df, L):
    st.title(lex[L]["m10"])
    score = (df[df['status']=='Paid']['amount'].sum() / df['amount'].sum()) * 100
    st.metric("Credit Score", f"{int(score)}/100")

def mod_logs(L):
    st.title(lex[L]["m11"])
    st.write("10:00 AM - Auto-Nudge Sent to Client A")

def mod_audit(df, L):
    st.title(lex[L]["m12"])
    st.download_button("Export Report", df.to_csv(index=False), "audit.csv")

# ==========================================
# 4. MAIN ROUTING
# ==========================================
def main():
    if "auth" not in st.session_state: st.session_state.auth = False
    if not st.session_state.auth:
        st.title("🧿 KhataKhat Pro Login")
        u = st.text_input("User", value="kd_merchant")
        p = st.text_input("Key", type="password", value="admin123")
        if st.button("Access Engine"):
            if u == "kd_merchant" and p == "admin123":
                st.session_state.auth = True
                st.rerun()
        return

    df = get_data()
    if df.empty: df = generate_seeds()

    with st.sidebar:
        st.title("KhataKhat AI")
        lang = st.radio("Language", ["English", "Hindi"])
        st.markdown("---")
        menu = [lex[lang][f"m{i}"] for i in range(1, 13)]
        choice = st.radio("Navigation", menu)
        if st.button("Logout"):
            st.session_state.auth = False
            st.rerun()

    # Explicit Map for Stability
    if choice == lex[lang]["m1"]: mod_dashboard(df, lang)
    elif choice == lex[lang]["m2"]: mod_upload(lang)
    elif choice == lex[lang]["m3"]: mod_ledger(df, lang)
    elif choice == lex[lang]["m4"]: mod_predictor(df, lang)
    elif choice == lex[lang]["m5"]: mod_recovery(df, lang)
    elif choice == lex[lang]["m6"]: mod_risk_radar(df, lang)
    elif choice == lex[lang]["m7"]: mod_scheduler(df, lang)
    elif choice == lex[lang]["m8"]: mod_trust(df, lang)
    elif choice == lex[lang]["m9"]: mod_legal(df, lang)
    elif choice == lex[lang]["m10"]: mod_bankability(df, lang)
    elif choice == lex[lang]["m11"]: mod_logs(lang)
    elif choice == lex[lang]["m12"]: mod_audit(df, lang)

if __name__ == "__main__":
    main()
