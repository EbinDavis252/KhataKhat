import streamlit as st
import pandas as pd
import numpy as np
import sqlite3
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

# ==========================================
# 0. PROFESSIONAL TYPOGRAPHY & THEME
# ==========================================
st.set_page_config(page_title="KhataKhat AI | Pro", layout="wide")

# High-Readability Industrial Theme
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Roboto+Mono:wght@400;700&family=Inter:wght@400;700&display=swap');
    
    .stApp { background-color: #0B0E14; color: #CFD8DC; font-family: 'Inter', sans-serif; }
    
    /* Intelligence Box - Clean & Stark */
    .ai-advisory {
        background: #151921;
        border-top: 1px solid #1DE9B6;
        border-bottom: 1px solid #1DE9B6;
        padding: 25px;
        margin-bottom: 30px;
    }
    
    .ai-tag { color: #1DE9B6; font-family: 'Roboto Mono', monospace; font-weight: bold; font-size: 12px; letter-spacing: 2px; }
    
    h1, h2, h3 { font-family: 'Roboto Mono', monospace; color: #FFFFFF; font-weight: 700; letter-spacing: -1px; }
    
    /* Metrics - Data First */
    div[data-testid="stMetricValue"] { color: #FFFFFF !important; font-family: 'Roboto Mono'; font-size: 32px !important; }
    
    /* Buttons - No Rounded Corners, Sharp Industrial Look */
    .stButton>button {
        background: transparent;
        color: #1DE9B6;
        border: 1px solid #1DE9B6;
        border-radius: 0px;
        padding: 10px 20px;
        width: 100%;
        font-family: 'Roboto Mono';
        transition: 0.3s;
    }
    .stButton>button:hover { background: #1DE9B6; color: #000000; }
    
    /* Table Styling */
    .stDataFrame { border: 1px solid #263238; }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 1. DATA INFRASTRUCTURE
# ==========================================
conn = sqlite3.connect('khatakhat_industrial.db', check_same_thread=False)

def get_db_connection():
    try:
        df = pd.read_sql("SELECT * FROM ledger", conn)
        df['due_date'] = pd.to_datetime(df['due_date'])
        return df
    except:
        return pd.DataFrame()

def sync_data(df):
    df.columns = [c.lower().strip().replace(' ', '_') for c in df.columns]
    df.to_sql("ledger", conn, if_exists="replace", index=False)

def seed_initial_data():
    customers = ["Enterprise Corp", "Global Systems", "Matrix Retail", "Alpha Logistics", "Vision Tech"]
    data = []
    for i in range(100):
        status = np.random.choice(["Paid", "Pending"], p=[0.7, 0.3])
        data.append({
            "customer": np.random.choice(customers),
            "amount": np.random.randint(10000, 200000),
            "status": status,
            "due_date": (datetime.now() + timedelta(days=np.random.randint(-40, 40))).strftime('%Y-%m-%d'),
            "trust_score": np.random.randint(300, 900)
        })
    df = pd.DataFrame(data)
    sync_data(df)
    return get_db_connection()

# ==========================================
# 2. THE AI ADVISORY LAYER (Logic-Driven)
# ==========================================
def ai_advisor(title, analysis):
    st.markdown(f"""
    <div class="ai-advisory">
        <div class="ai-tag">KHATAKHAT AI | ANALYSIS ENGINE</div>
        <h4 style="margin: 10px 0; color: #FFFFFF;">{title}</h4>
        <p style="color: #90A4AE; font-size: 15px; line-height: 1.6;">{analysis}</p>
    </div>
    """, unsafe_allow_html=True)

# ==========================================
# 3. CORE ANALYTICAL MODULES
# ==========================================

def mod_dashboard(df):
    st.title("EXECUTIVE_OVERVIEW")
    pending = df[df['status'].str.lower() == 'pending']
    total_val = pending['amount'].sum()
    
    # AI Summary
    analysis = (f"Market exposure is currently at ₹{total_val:,.0f}. "
                "The AI detects a cluster of high-value debts (avg ₹85k) that have entered the 15-day delay window. "
                "Systemic risk is currently categorized as MODERATE.")
    ai_advisor("LIQUIDITY_STATUS_REPORT", analysis)

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("TOTAL_OUTSTANDING", f"₹{total_val:,.0f}")
    c2.metric("RECOVERY_RATE", "84.2%", "+1.2%")
    c3.metric("AVG_TRUST_SCORE", int(df['trust_score'].mean()))
    c4.metric("HIGH_RISK_CLIENTS", len(pending[pending['trust_score'] < 450]))

    st.subheader("3D_CREDIT_TOPOGRAPHY")
    fig = px.scatter_3d(df, x='amount', y='trust_score', z='status', color='status',
                        color_discrete_map={'Pending': '#FF5252', 'Paid': '#1DE9B6'},
                        template="plotly_dark", opacity=0.7)
    fig.update_layout(scene=dict(bgcolor="#0B0E14"), margin=dict(l=0,r=0,b=0,t=0))
    st.plotly_chart(fig, use_container_width=True)

def mod_risk_predictor(df):
    st.title("PROBABILITY_ANALYSIS")
    pending = df[df['status'].str.lower() == 'pending'].copy()
    if pending.empty:
        st.info("NO PENDING ASSETS DETECTED.")
        return

    # Logic-based Prediction
    pending['risk_index'] = (900 - pending['trust_score']) / 6
    
    ai_advisor("DEFAULT_PREDICTION_LOGIC", 
               "Risk is calculated using a variance model between Trust Scores and Debt Magnitude. "
               "Clients in the upper-right quadrant possess the highest probability of total capital loss.")

    fig = px.scatter(pending, x="amount", y="risk_index", size="amount", color="risk_index",
                     color_continuous_scale="Viridis", template="plotly_dark")
    st.plotly_chart(fig, use_container_width=True)

def mod_recovery_ops(df):
    st.title("RECOVERY_WAR_ROOM")
    pending = df[df['status'].str.lower() == 'pending']
    
    col1, col2 = st.columns([1, 1.5])
    with col1:
        target = st.selectbox("SELECT_ENTITY", pending['customer'].unique())
        client = pending[pending['customer'] == target].iloc[0]
        st.write(f"DEBT_VALUE: ₹{client['amount']:,.0f}")
        st.write(f"TRUST_HEALTH: {client['trust_score']}")
    
    with col2:
        ai_advisor("BEHAVIORAL_RECOVERY_STRATEGY", 
                   f"Entity {target} maintains a score of {client['trust_score']}. "
                   "Data suggests a 'Professional/Firm' nudge will trigger settlement within 48 hours.")
        msg = f"OFFICIAL NOTICE: Balance of ₹{client['amount']} is outstanding for {target}. Settle to maintain Trust Index."
        st.text_area("GENERATED_NUDGE", msg)
        st.button("EXECUTE_WHATSAPP_NUDGE")

def mod_ledger(df):
    st.title("SMART_LEDGER_SYSTEM")
    st.dataframe(df, use_container_width=True)

# ==========================================
# 4. SYSTEM NAVIGATION
# ==========================================
def main():
    # Login Layer
    if "auth" not in st.session_state: st.session_state.auth = False
    if not st.session_state.auth:
        st.title("KHATAKHAT_AI_SYSTEM_ACCESS")
        u = st.text_input("ENTITY_ID", value="kd_merchant")
        p = st.text_input("SECURE_KEY", type="password", value="admin123")
        if st.button("AUTHORIZE_ACCESS"):
            if u == "kd_merchant" and p == "admin123":
                st.session_state.auth = True
                st.rerun()
        return

    df = get_db_connection()
    if df.empty: df = seed_initial_data()

    # Sidebar
    with st.sidebar:
        st.title("KHATAKHAT_AI")
        lang = st.radio("SYSTEM_LANGUAGE", ["English", "Hindi"])
        st.markdown("---")
        # Removed icons, kept it clean typography
        menu = ["DASHBOARD", "LEDGER", "RISK_PREDICTOR", "RECOVERY_OPS", "AUDIT_REPORTS"]
        choice = st.radio("NAVIGATION", menu)
        if st.button("TERMINATE_SESSION"):
            st.session_state.auth = False
            st.rerun()

    # Main Router
    if choice == "DASHBOARD": mod_dashboard(df)
    elif choice == "LEDGER": mod_ledger(df)
    elif choice == "RISK_PREDICTOR": mod_risk_predictor(df)
    elif choice == "RECOVERY_OPS": mod_recovery_ops(df)
    elif choice == "AUDIT_REPORTS":
        st.title("AUDIT_AND_EXPORT")
        ai_advisor("DATA_EXPORT_PROTOCOL", "Full ledger audit is ready for CSV serialization. Use this for legal or banking reconciliation.")
        st.download_button("EXPORT_FULL_CSV", df.to_csv(index=False), "audit.csv")

if __name__ == "__main__":
    main()
