import streamlit as st
import pandas as pd
import numpy as np
import sqlite3
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import io

# ==========================================
# 0. UI & READABILITY ENGINE
# ==========================================
st.set_page_config(page_title="KhataKhat Pro | AI Assistant", layout="wide", page_icon="📈")

st.markdown("""
    <style>
    .stApp { background-color: #0F172A; color: #F8FAFC; }
    .khatakhat-card {
        background: #1E293B; border-left: 6px solid #6366F1;
        padding: 20px; border-radius: 12px; margin-bottom: 25px;
        color: #F8FAFC; box-shadow: 0 4px 15px rgba(0,0,0,0.4);
    }
    h1, h2, h3 { color: #38BDF8; font-weight: 700; }
    div[data-testid="stMetricValue"] { color: #22D3EE !important; }
    .stButton>button {
        background: linear-gradient(90deg, #6366F1, #38BDF8);
        color: white; border-radius: 8px; border: none; font-weight: bold; width: 100%;
    }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 1. BILINGUAL DICTIONARY
# ==========================================
lex = {
    "English": {
        "m1": "📊 Dashboard", "m2": "📂 Upload Data", "m3": "Smart Ledger", 
        "m4": "🔮 AI Predictor", "m5": "🎯 Recovery Ops", "m6": "⚠️ Risk Radar",
        "m7": "📅 Smart Scheduler", "m8": "🎖️ Trust Index", "m9": "💡 Insights", "m10": "📄 Reports",
        "ai_head": "KhataKhat AI Briefing", "wa": "WhatsApp Nudge 🚀"
    },
    "Hindi": {
        "m1": "📊 डैशबोर्ड", "m2": "📂 डेटा अपलोड", "m3": "स्मार्ट खाता", 
        "m4": "🔮 भविष्यवाणी", "m5": "🎯 वसूली केंद्र", "m6": "⚠️ जोखिम रडार",
        "m7": "📅 स्मार्ट कैलेंडर", "m8": "🎖️ भरोसा स्कोर", "m9": "💡 व्यापारिक विचार", "m10": "📄 रिपोर्ट",
        "ai_head": "खटाखट AI विश्लेषण", "wa": "व्हाट्सएप भेजें 🚀"
    }
}

# ==========================================
# 2. DATA PROTECTION & NORMALIZATION
# ==========================================
conn = sqlite3.connect('khatakhat_final_v4.db', check_same_thread=False)

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
    required = ['customer', 'amount', 'status', 'due_date', 'trust_score']
    for col in required:
        if col not in df.columns:
            df[col] = 500 if col == 'trust_score' else ('Pending' if col == 'status' else 0)
    df.to_sql("ledger", conn, if_exists="replace", index=False)

def generate_seeds():
    names = ["Sharma Electronics", "Verma Grocery", "Rajesh Traders", "Priya Fashion", "Malhotra Sweets"]
    data = []
    for i in range(50):
        status = np.random.choice(["Paid", "Pending"], p=[0.7, 0.3])
        data.append({
            "customer": np.random.choice(names),
            "amount": np.random.randint(5000, 50000),
            "status": status,
            "due_date": (datetime.now() + timedelta(days=np.random.randint(-15, 15))).strftime('%Y-%m-%d'),
            "trust_score": np.random.randint(350, 850)
        })
    df = pd.DataFrame(data)
    save_data(df)
    return get_data()

def ai_card(title, msg):
    st.markdown(f"<div class='khatakhat-card'><h4 style='margin:0; color:#38BDF8;'>🤖 {title}</h4><p style='margin-top:10px;'>{msg}</p></div>", unsafe_allow_html=True)

# ==========================================
# 3. FULL MODULE IMPLEMENTATION
# ==========================================

def mod_dashboard(df, L):
    st.title(lex[L]["m1"])
    pending = df[df['status'].str.lower() == 'pending']
    total = pending['amount'].sum() if not pending.empty else 0
    ai_card(lex[L]["ai_head"], f"KD, you have ₹{total:,.0f} outstanding. Market sentiment is stable.")
    c1, c2, c3 = st.columns(3)
    c1.metric("Pending", f"₹{total:,.0f}")
    c2.metric("Trust Avg", int(df['trust_score'].mean()))
    c3.metric("Records", len(df))
    if not df.empty:
        fig = px.scatter_3d(df, x='amount', y='trust_score', z='status', color='status', template="plotly_dark")
        st.plotly_chart(fig, use_container_width=True)

def mod_predictor(df, L):
    st.title(lex[L]["m4"])
    pending = df[df['status'].str.lower() == 'pending'].copy()
    if pending.empty:
        st.success("No pending debts to analyze!")
        return
    pending['risk'] = (900 - pending['trust_score']) / 6
    # Fix: Ensure size is always > 0 for Plotly
    pending['bubble_size'] = pending['amount'].clip(lower=100)
    fig = px.scatter(pending, x="amount", y="risk", size="bubble_size", color="risk", 
                     hover_name="customer", color_continuous_scale="RdYlGn_r", template="plotly_dark")
    st.plotly_chart(fig, use_container_width=True)

def mod_recovery(df, L):
    st.title(lex[L]["m5"])
    pending = df[df['status'].str.lower() == 'pending']
    if pending.empty:
        st.success("Recovery Room is clear!")
        return
    target = st.selectbox("Select Client", pending['customer'].unique())
    client_data = pending[pending['customer'] == target]
    if not client_data.empty:
        client = client_data.iloc[0]
        st.subheader(f"Strategy for {target}")
        st.write(f"**Amount:** ₹{client['amount']} | **Trust:** {client['trust_score']}")
        msg = f"Pranaam {target}, KhataKhat AI update. Please settle ₹{client['amount']} to protect your {client['trust_score']} score."
        st.text_area("Draft", msg, height=100)
        st.button(lex[L]["wa"])

def mod_scheduler(df, L):
    st.title(lex[L]["m7"])
    pending = df[df['status'].str.lower() == 'pending'].copy()
    if pending.empty:
        st.info("No tasks scheduled.")
        return
    # Logic: Remind high trust later, low trust now
    pending['remind_on'] = pending.apply(lambda x: x['due_date'] - timedelta(days=2) if x['trust_score'] < 500 else x['due_date'] + timedelta(days=2), axis=1)
    st.subheader("Upcoming Nudge Schedule")
    st.dataframe(pending[['customer', 'amount', 'remind_on']].sort_values(by='remind_on'), use_container_width=True)

def mod_trust_index(df, L):
    st.title(lex[L]["m8"])
    ranking = df.groupby('customer')['trust_score'].mean().sort_values(ascending=False).reset_index()
    st.table(ranking)

def mod_insights(df, L):
    st.title(lex[L]["m9"])
    st.write(f"**Best Customer:** {df[df['status']=='Paid']['customer'].mode().values[0] if not df[df['status']=='Paid'].empty else 'N/A'}")
    st.write(f"**Capital Health Ratio:** {round(df[df['status']=='Paid']['amount'].sum() / df['amount'].sum() * 100, 1)}%")
    fig = px.pie(df, names='status', values='amount', title="Capital Split")
    st.plotly_chart(fig)

def mod_reports(df, L):
    st.title(lex[L]["m10"])
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button("📥 Export CSV Report", data=csv, file_name="audit.csv")
    if st.button("Reset & Reload Sample Data"):
        generate_seeds()
        st.rerun()

# ==========================================
# 4. MAIN NAVIGATION
# ==========================================
def main():
    if "auth" not in st.session_state: st.session_state.auth = False
    if not st.session_state.auth:
        st.title("🛡️ KhataKhat Pro Login")
        u = st.text_input("User", value="kd_merchant")
        p = st.text_input("Pass", type="password", value="admin123")
        if st.button("Login"):
            if u == "kd_merchant" and p == "admin123":
                st.session_state.auth = True
                st.rerun()
        return

    df = get_data()
    if df.empty: df = generate_seeds()

    with st.sidebar:
        st.title("KhataKhat AI")
        L = st.radio("Language", ["English", "Hindi"])
        st.markdown("---")
        menu = [lex[L][f"m{i}"] for i in range(1, 11)]
        choice = st.radio("Navigate", menu)
        if st.button("Logout"):
            st.session_state.auth = False
            st.rerun()

    # Fixed Routing Map
    if choice == lex[L]["m1"]: mod_dashboard(df, L)
    elif choice == lex[L]["m2"]: 
        st.title(lex[L]["m2"])
        f = st.file_uploader("Upload")
        if f: 
            d = pd.read_csv(f) if f.name.endswith('.csv') else pd.read_excel(f)
            save_data(d); st.success("Updated!"); st.rerun()
    elif choice == lex[L]["m3"]: st.title(lex[L]["m3"]); st.dataframe(df, use_container_width=True)
    elif choice == lex[L]["m4"]: mod_predictor(df, L)
    elif choice == lex[L]["m5"]: mod_recovery(df, L)
    elif choice == lex[L]["m7"]: mod_scheduler(df, L)
    elif choice == lex[L]["m8"]: mod_trust_index(df, L)
    elif choice == lex[L]["m9"]: mod_insights(df, L)
    elif choice == lex[L]["m10"]: mod_reports(df, L)

if __name__ == "__main__":
    main()
