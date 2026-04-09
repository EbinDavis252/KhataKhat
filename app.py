import streamlit as st
import streamlit_authenticator as stauth
import pandas as pd
import numpy as np
import sqlite3
import plotly.express as px
from datetime import datetime, timedelta
import urllib.parse

# ==========================================
# 0. UI & BRANDING CONFIG
# ==========================================
st.set_page_config(page_title="Khatakhat | AI Recovery", layout="wide", page_icon="💸")

st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .main-title { font-size: 45px; font-weight: 800; color: #1E1E1E; }
    .highlight { color: #FF4B4B; }
    .stButton>button { width: 100%; border-radius: 5px; height: 3em; background-color: #FF4B4B; color: white; }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 1. DATABASE & DATA ENGINE
# ==========================================
conn = sqlite3.connect('khatakhat.db', check_same_thread=False)

def get_data():
    try:
        df = pd.read_sql("SELECT * FROM ledger", conn)
        df['purchase_date'] = pd.to_datetime(df['purchase_date'], errors='coerce')
        df['due_date'] = pd.to_datetime(df['due_date'], errors='coerce')
        df['payment_date'] = pd.to_datetime(df['payment_date'], errors='coerce')
        return df
    except:
        return pd.DataFrame()

def generate_sample_data():
    np.random.seed(42)
    customers = ["Ramesh Kumar", "Suresh Store", "Ankit Electronics", "Priya Textiles", "Verma Ji"]
    data = []
    for _ in range(50):
        p_date = datetime.now() - timedelta(days=np.random.randint(1, 60))
        status = np.random.choice(["Paid", "Pending"], p=[0.6, 0.4])
        data.append({
            "customer_name": np.random.choice(customers),
            "amount": np.random.randint(500, 5000),
            "payment_status": status,
            "purchase_date": p_date,
            "due_date": p_date + timedelta(days=15),
            "payment_date": p_date + timedelta(days=20) if status == "Paid" else None,
            "phone_number": "919876543210" # Use international format for WhatsApp
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
# 3. BEHAVIORAL RECOVERY MODULE (The Core Engine)
# ==========================================
def module_recovery_engine(df):
    st.header("🧠 Behavioral Recovery Engine")
    
    pending_df = df[df['payment_status'] == 'Pending']
    if pending_df.empty:
        st.success("All caught up! No pending payments.")
        return

    st.subheader("Select a customer to nudge")
    selected_cust = st.selectbox("Customer Name", pending_df['customer_name'].unique())
    cust_data = pending_df[pending_df['customer_name'] == selected_cust].iloc[0]
    
    amount = cust_data['amount']
    phone = cust_data['phone_number']

    st.markdown(f"### Strategy Selection for {selected_cust}")
    
    # AI Message Strategies
    strategies = {
        "Social Proof": f"Hi {selected_cust}, you are one of our top-rated customers! Clearing your ₹{amount} helps maintain your status in the merchant trust network.",
        "Loss Aversion": f"Hi {selected_cust}, to avoid a temporary pause in your credit limit, please settle the outstanding ₹{amount} today.",
        "Reciprocity": f"Hi {selected_cust}, we've valued our partnership for months. Kindly return the favor by clearing your ₹{amount} ledger today."
    }
    
    choice = st.radio("Choose Nudge Strategy", list(strategies.keys()))
    message = strategies[choice]
    
    st.info(f"**Preview:** {message}")
    
    # WhatsApp Deep Linking Logic
    encoded_msg = urllib.parse.quote(message)
    # Note: UPI link could be added to message here as well
    wa_url = f"https://wa.me/{phone}?text={encoded_msg}"
    
    st.markdown(f'<a href="{wa_url}" target="_blank"><button style="width:100%; background-color:#25D366; color:white; border:none; padding:10px; border-radius:5px; cursor:pointer;">📲 Send WhatsApp Nudge</button></a>', unsafe_allow_html=True)

# ==========================================
# 4. MAIN ROUTING
# ==========================================

# FIX: Added keyword arguments for the login method
# Current streamlit-authenticator syntax: .login(location='main' or 'sidebar')
try:
    authenticator.login(location='sidebar')
except Exception as e:
    # Fallback for even newer versions where 'location' might be 'main' by default
    authenticator.login()

if st.session_state["authentication_status"]:
    authenticator.logout('Logout', 'sidebar')
    
    df = get_data()
    if df.empty:
        df = generate_sample_data()

    st.sidebar.title("Khatakhat 🚀")
    nav = st.sidebar.radio("Navigation", ["Dashboard", "Recovery Engine", "Ledger", "Trust Network"])

    if nav == "Dashboard":
        # Simplified Dashboard Logic
        st.header("📊 Merchant Dashboard")
        c1, c2 = st.columns(2)
        c1.metric("Outstanding", f"₹{df[df['payment_status']=='Pending']['amount'].sum():,.0f}")
        c2.metric("Recovery Rate", "82%")
        st.plotly_chart(px.bar(df, x='customer_name', y='amount', color='payment_status'), use_container_width=True)
        
    elif nav == "Recovery Engine":
        module_recovery_engine(df)
        
    elif nav == "Ledger":
        st.header("📓 Records")
        st.dataframe(df, use_container_width=True)
        
    elif nav == "Trust Network":
        st.header("🌐 Global Trust Network")
        st.text_input("Search Customer Phone Number")
        st.write("Results will appear here based on cross-merchant data.")

elif st.session_state["authentication_status"] is False:
    st.error('Username/password is incorrect')

elif st.session_state["authentication_status"] is None:
    # --- LANDING PAGE ---
    st.markdown('<h1 class="main-title">Better than <span class="highlight">Ledgers</span>.</h1>', unsafe_allow_html=True)
    st.write("### AI-powered recovery for small businesses.")
    st.image("https://img.freepik.com/free-vector/financial-analytics-concept-illustration_114360-143.jpg", width=600)
    st.info("👈 Please login via the sidebar to access your shop's engine.")
