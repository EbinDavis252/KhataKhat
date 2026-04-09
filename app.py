import streamlit as st
import streamlit_authenticator as stauth
import pandas as pd
import numpy as np
import sqlite3
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from sklearn.ensemble import RandomForestClassifier
from streamlit_lottie import st_lottie
import requests

# ==========================================
# 0. UI & BRANDING CONFIG
# ==========================================
st.set_page_config(page_title="Khatakhat | AI Recovery", layout="wide", page_icon="💸")

# Hide Streamlit Branding for a Professional Look
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .main-title { font-size: 50px; font-weight: 800; color: #1E1E1E; }
    .highlight { color: #FF4B4B; }
    [data-testid="stMetricValue"] { font-size: 28px; }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 1. DATABASE & DATA ENGINE
# ==========================================
conn = sqlite3.connect('khatakhat.db', check_same_thread=False)

def get_data():
    try:
        df = pd.read_sql("SELECT * FROM ledger", conn)
        # CRITICAL FIX: Ensure all dates are actual datetime objects
        df['purchase_date'] = pd.to_datetime(df['purchase_date'], errors='coerce')
        df['due_date'] = pd.to_datetime(df['due_date'], errors='coerce')
        df['payment_date'] = pd.to_datetime(df['payment_date'], errors='coerce')
        return df
    except:
        return pd.DataFrame()

def generate_sample_data():
    """Seed data if the database is brand new."""
    np.random.seed(42)
    customers = [f"Customer {i}" for i in range(1, 21)]
    data = []
    for i in range(100):
        p_date = datetime.now() - timedelta(days=np.random.randint(1, 60))
        status = np.random.choice(["Paid", "Pending"], p=[0.7, 0.3])
        pay_date = p_date + timedelta(days=np.random.randint(5, 20)) if status == "Paid" else None
        data.append({
            "customer_name": np.random.choice(customers),
            "amount": np.random.randint(500, 5000),
            "payment_status": status,
            "purchase_date": p_date,
            "due_date": p_date + timedelta(days=15),
            "payment_date": pay_date,
            "phone_number": "9876543210"
        })
    df = pd.DataFrame(data)
    df.to_sql("ledger", conn, if_exists="replace", index=False)
    return get_data()

# ==========================================
# 2. AUTHENTICATION SETUP
# ==========================================
auth_data = {
    "usernames": {
        "kd_merchant": {
            "name": "KD",
            "password": "$2b$12$6k/p09/TfOQ.S1FzXhYis.NInXQGf.VdG5mN6f0Fv6P9rK2Jg6vG.", # password: admin123
            "email": "kd@khatakhat.com"
        }
    }
}

authenticator = stauth.Authenticate(
    auth_data,
    "khatakhat_cookie",
    "signature_key",
    cookie_expiry_days=30
)

# ==========================================
# 3. CORE MODULES
# ==========================================

def module_dashboard(df):
    st.header("📊 Merchant Dashboard")
    
    # KPIs with Data Fixes
    pending_df = df[df['payment_status'] == 'Pending']
    total_outstanding = pending_df['amount'].sum()
    
    # Fixed Date Comparison
    last_30_days = pd.Timestamp(datetime.now() - timedelta(days=30))
    recovered_this_month = df[(df['payment_status'] == 'Paid') & (df['payment_date'] >= last_30_days)]['amount'].sum()
    
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Outstanding", f"₹{total_outstanding:,.0f}")
    c2.metric("Monthly Recovery", f"₹{recovered_this_month:,.0f}")
    c3.metric("Trust Score", "742", "+12")
    c4.metric("Risk Level", "Medium", "-2%", delta_color="inverse")
    
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    with col1:
        fig = px.pie(df, names='payment_status', title="Payment Status Mix", hole=0.4, color_discrete_sequence=['#00CC96', '#EF553B'])
        st.plotly_chart(fig, use_container_width=True)
    with col2:
        trend = df.groupby(df['purchase_date'].dt.date)['amount'].sum().reset_index()
        fig2 = px.line(trend, x='purchase_date', y='amount', title="Credit Sales Trend")
        st.plotly_chart(fig2, use_container_width=True)

def module_trust_network():
    st.header("🌐 Global Trust Network")
    st.info("The first decentralized credit scoring system for Indian MSMEs.")
    phone = st.text_input("Verify Customer Phone Number", placeholder="Enter 10-digit mobile number")
    if phone:
        if phone.endswith(('0', '3', '7')): # Mock logic
            st.error("⚠️ **Alert:** This customer has defaulted with 3 other merchants in your area.")
        else:
            st.success("✅ **Verified:** No payment defaults found on the Khatakhat Network.")

def module_ledger(df):
    st.header("📓 Ledger Records")
    status = st.selectbox("Filter Status", ["All", "Pending", "Paid"])
    if status != "All":
        df = df[df['payment_status'] == status]
    st.dataframe(df, use_container_width=True)

# ==========================================
# 4. MAIN ROUTING
# ==========================================

# Render Login in Sidebar
authentication_status = authenticator.login('Login', 'sidebar')

if st.session_state["authentication_status"]:
    # --- AUTHENTICATED ---
    authenticator.logout('Logout', 'sidebar')
    
    # Load and Sanitize Data
    df = get_data()
    if df.empty:
        df = generate_sample_data()

    st.sidebar.title(f"Khatakhat 🚀")
    st.sidebar.write(f"Logged in as: **{st.session_state['name']}**")
    
    nav = st.sidebar.radio("Go to:", [
        "Dashboard", 
        "Global Trust Network", 
        "Customer Ledger", 
        "AI Recovery Engine",
        "Settings"
    ])

    if nav == "Dashboard":
        module_dashboard(df)
    elif nav == "Global Trust Network":
        module_trust_network()
    elif nav == "Customer Ledger":
        module_ledger(df)
    elif nav == "AI Recovery Engine":
        st.header("🧠 Behavioral Recovery")
        st.write("Coming Next: WhatsApp Deep-linking and Psychological Nudges.")
        
elif st.session_state["authentication_status"] is False:
    st.error('Username/password is incorrect')

elif st.session_state["authentication_status"] is None:
    # --- LANDING PAGE ---
    col1, col2 = st.columns([1.5, 1])
    with col1:
        st.markdown('<h1 class="main-title">Better than <span class="highlight">Khatabook</span>. Faster than <span class="highlight">Zoho</span>.</h1>', unsafe_allow_html=True)
        st.markdown("### Most merchants lose 20% of their capital to 'forgotten' debts. Khatakhat AI recovers them for you.")
        
        st.markdown("---")
        st.subheader("Why choose Khatakhat?")
        st.write("✅ **AI Behavioral Reminders:** Not just 'Please pay', but psychological nudges.")
        st.write("✅ **Global Trust Score:** Check if a customer pays others before giving them credit.")
        st.write("✅ **Cash Flow Predictor:** Know exactly how much money will hit your bank.")
        
        st.info("👈 **Login via the sidebar** to start your recovery engine.")
    
    with col2:
        st.image("https://img.freepik.com/free-vector/financial-analytics-concept-illustration_114360-143.jpg")
