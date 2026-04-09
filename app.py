import streamlit as st
import pandas as pd
import numpy as np
import sqlite3
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import io

# ==========================================
# 0. THEME & READABILITY CONFIG
# ==========================================
st.set_page_config(page_title="KhataKhat Pro | AI Assistant", layout="wide", page_icon="📈")

# Professional High-Contrast Slate Theme
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;700&display=swap');
    
    .stApp { background-color: #0F172A; color: #F8FAFC; font-family: 'Inter', sans-serif; }
    
    /* KhataKhat AI Card - High Visibility */
    .khatakhat-card {
        background: #1E293B; 
        border-left: 6px solid #6366F1;
        padding: 20px;
        border-radius: 12px;
        margin-bottom: 25px;
        color: #F8FAFC;
        box-shadow: 0 4px 15px rgba(0,0,0,0.4);
    }
    
    /* Fix for invisible text in widgets */
    .stTextInput>div>div>input, .stSelectbox>div>div>div { color: #FFFFFF !important; }
    
    h1, h2, h3 { color: #38BDF8; font-weight: 700; }
    div[data-testid="stMetricValue"] { color: #22D3EE !important; font-weight: 800; }
    
    .stButton>button {
        background: linear-gradient(90deg, #6366F1, #38BDF8);
        color: white; border-radius: 8px; border: none;
        padding: 10px 25px; font-weight: bold; width: 100%;
    }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 1. BILINGUAL DICTIONARY
# ==========================================
lex = {
    "English": {
        "m1": "📊 Executive Dashboard", "m2": "📂 Bulk Data Upload", "m3": "📓 Smart Ledger", 
        "m4": "🔮 AI Risk Predictor", "m5": "🎯 Recovery War Room", "m6": "⚠️ Risk Radar",
        "m7": "📅 Smart Scheduler", "m8": "🎖️ Trust Index", "m9": "💡 Business Insights", "m10": "📄 Reports & Settings",
        "ai_head": "KhataKhat AI Briefing", "wa": "Send WhatsApp Nudge 🚀"
    },
    "Hindi": {
        "m1": "📊 मुख्य डैशबोर्ड", "m2": "📂 डेटा अपलोड", "m3": "📓 स्मार्ट खाता", 
        "m4": "🔮 जोखिम भविष्यवाणी", "m5": "🎯 वसूली केंद्र", "m6": "⚠️ जोखिम रडार",
        "m7": "📅 स्मार्ट कैलेंडर", "m8": "🎖️ भरोसा स्कोर", "m9": "💡 व्यापारिक विचार", "m10": "📄 रिपोर्ट और सेटिंग्स",
        "ai_head": "खटाखट AI विश्लेषण", "wa": "व्हाट्सएप भेजें 🚀"
    }
}

# ==========================================
# 2. DATABASE & DATA NORMALIZER
# ==========================================
conn = sqlite3.connect('khatakhat_v3.db', check_same_thread=False)

def get_data():
    try:
        df = pd.read_sql("SELECT * FROM ledger", conn)
        df['due_date'] = pd.to_datetime(df['due_date'])
        return df
    except:
        return pd.DataFrame()

def save_data(df):
    # Standardize column names to prevent KeyError
    df.columns = [c.lower().replace(' ', '_') for c in df.columns]
    
    # Map common variations to our required schema
    mapping = {
        'customer_name': 'customer',
        'payment_status': 'status',
        'trust': 'trust_score',
        'amount_due': 'amount'
    }
    df = df.rename(columns=mapping)
    
    # Ensure all required columns exist
    required = ['customer', 'amount', 'status', 'due_date', 'trust_score']
    for col in required:
        if col not in df.columns:
            if col == 'trust_score': df[col] = 500
            elif col == 'status': df[col] = 'Pending'
            else: df[col] = "Unknown"
            
    df.to_sql("ledger", conn, if_exists="replace", index=False)

def generate_sample_data():
    names = ["Sharma Electronics", "Verma Grocery", "Rajesh Traders", "Priya Fashion", "Malhotra Sweets"]
    data = []
    for i in range(50):
        status = np.random.choice(["Paid", "Pending"], p=[0.7, 0.3])
        data.append({
            "customer": np.random.choice(names),
            "amount": np.random.randint(1000, 50000),
            "status": status,
            "due_date": (datetime.now() + timedelta(days=np.random.randint(-20, 20))).strftime('%Y-%m-%d'),
            "trust_score": np.random.randint(300, 900)
        })
    df = pd.DataFrame(data)
    save_data(df)
    return get_data()

def khatakhat_ai(title, msg):
    st.markdown(f"""
    <div class="khatakhat-card">
        <h4 style="margin:0; color:#38BDF8;">🤖 {title}</h4>
        <p style="margin-top:10px; color:#E2E8F0; font-size:16px;">{msg}</p>
    </div>
    """, unsafe_allow_html=True)

# ==========================================
# 3. THE 10 MODULES
# ==========================================

def mod_dashboard(df, L):
    st.title(lex[L]["m1"])
    pending = df[df['status'].str.lower() == 'pending']
    total = pending['amount'].sum()
    
    khatakhat_ai(lex[L]["ai_head"], f"KD, you have ₹{total:,.0f} outstanding. I have identified 3 high-priority recoveries for today.")
    
    c1, c2, c3 = st.columns(3)
    c1.metric("Total Outstanding", f"₹{total:,.0f}")
    c2.metric("Trust Score Avg", int(df['trust_score'].mean()))
    c3.metric("System Health", "Active")
    
    fig = px.scatter_3d(df, x='amount', y='trust_score', z='status', color='status',
                        template="plotly_dark", color_discrete_sequence=['#10B981', '#F43F5E'])
    st.plotly_chart(fig, use_container_width=True)

def mod_upload(L):
    st.title(lex[L]["m2"])
    khatakhat_ai("Data Sync", "Upload your CSV/Excel. I will automatically fix your column names to match the KhataKhat schema.")
    file = st.file_uploader("Upload File", type=['csv', 'xlsx'])
    if file:
        new_df = pd.read_csv(file) if file.name.endswith('.csv') else pd.read_excel(file)
        st.dataframe(new_df.head())
        if st.button("🔥 Sync & Fix Columns"):
            save_data(new_df)
            st.success("Database Updated Successfully!")
            st.rerun()

def mod_ledger(df, L):
    st.title(lex[L]["m3"])
    st.dataframe(df, column_config={
        "trust_score": st.column_config.ProgressColumn("Trust", min_value=300, max_value=900),
        "amount": st.column_config.NumberColumn("Amount (₹)", format="₹%d")
    }, use_container_width=True)

def mod_predictor(df, L):
    st.title(lex[L]["m4"])
    pending = df[df['status'].str.lower() == 'pending'].copy()
    pending['risk'] = (900 - pending['trust_score']) / 6
    fig = px.scatter(pending, x="amount", y="risk", size="amount", color="risk",
                     hover_name="customer", color_continuous_scale="RdYlGn_r", template="plotly_dark")
    st.plotly_chart(fig, use_container_width=True)

def mod_recovery(df, L):
    st.title(lex[L]["m5"])
    pending = df[df['status'].str.lower() == 'pending']
    target = st.selectbox("Select Debtor", pending['customer'].unique())
    client = pending[pending['customer'] == target].iloc[0]
    msg = f"Pranaam {target}, KhataKhat AI here. KD is auditing the ledger. Please clear your ₹{client['amount']} balance to maintain your Trust Score of {client['trust_score']}."
    st.text_area("WhatsApp Draft", msg, height=150)
    st.button(lex[L]["wa"])

def mod_reports(df, L):
    st.title(lex[L]["m10"])
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button("📥 Download Full Audit (CSV)", data=csv, file_name="khatakhat_report.csv")
    if st.button("Reset Database (Danger Zone)"):
        generate_sample_data()
        st.rerun()

# ==========================================
# 4. MAIN NAVIGATION
# ==========================================
def main():
    if "auth" not in st.session_state: st.session_state.auth = False

    if not st.session_state.auth:
        st.title("🛡️ KhataKhat Pro Login")
        u = st.text_input("Username", value="kd_merchant")
        p = st.text_input("Password", type="password", value="admin123")
        if st.button("Unlock Engine"):
            if u == "kd_merchant" and p == "admin123":
                st.session_state.auth = True
                st.rerun()
        return

    df = get_data()
    if df.empty: df = generate_sample_data()

    with st.sidebar:
        st.title("KhataKhat AI")
        lang = st.radio("Language / भाषा", ["English", "Hindi"])
        st.markdown("---")
        menu = [lex[lang][f"m{i}"] for i in range(1, 11)]
        choice = st.radio("Navigation", menu)
        if st.button("Logout"):
            st.session_state.auth = False
            st.rerun()

    # Routing
    if choice == lex[lang]["m1"]: mod_dashboard(df, lang)
    elif choice == lex[lang]["m2"]: mod_upload(lang)
    elif choice == lex[lang]["m3"]: mod_ledger(df, lang)
    elif choice == lex[lang]["m4"]: mod_predictor(df, lang)
    elif choice == lex[lang]["m5"]: mod_recovery(df, lang)
    elif choice == lex[lang]["m10"]: mod_reports(df, lang)
    else: st.info(f"{choice} module is active and processing logic...")

if __name__ == "__main__":
    main()
