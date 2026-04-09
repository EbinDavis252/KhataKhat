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

# Custom CSS for Premium FinTech Feel
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stApp { background-color: #FFFFFF; }
    .main-title { font-size: 50px; font-weight: 800; color: #1E1E1E; }
    .highlight { color: #FF4B4B; }
    .card { padding: 20px; border-radius: 15px; background-color: #f9f9f9; border: 1px solid #eee; }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 1. AUTHENTICATION SETUP
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
# 2. DATABASE & DATA ENGINE
# ==========================================
conn = sqlite3.connect('khatakhat.db', check_same_thread=False)

def get_data():
    try:
        df = pd.read_sql("SELECT * FROM ledger", conn)
        df['purchase_date'] = pd.to_datetime(df['purchase_date'])
        df['due_date'] = pd.to_datetime(df['due_date'])
        return df
    except:
        # Initial dummy data if DB is empty
        return pd.DataFrame()

# ==========================================
# 3. GLOBAL TRUST NETWORK (The "Killer" Feature)
# ==========================================
def module_global_trust():
    st.header("🌐 Global Trust Network")
    st.markdown("### *The CIBIL for Micro-Merchants*")
    st.write("Check if a new customer has defaulted with other merchants in the Khatakhat network.")
    
    search_phone = st.text_input("Enter Customer Phone Number to verify", placeholder="98XXXXXXXX")
    
    if search_phone:
        # Simulation of a Global Network check
        # In a real app, this queries a global 'Defaulters' table
        is_flagged = int(search_phone[-1]) % 3 == 0 # Mock logic
        
        if is_flagged:
            st.error(f"⚠️ **High Alert:** Phone number {search_phone} has been flagged by 2 other merchants for non-payment.")
            st.button("Request Detailed Report")
        else:
            st.success(f"✅ **Clear Record:** No defaults found for {search_phone} in the Khatakhat Network.")

# ==========================================
# 4. OTHER CORE MODULES (Simplified for brevity)
# ==========================================
def module_dashboard(df):
    st.header("📊 Merchant Dashboard")
    col1, col2, col3 = st.columns(3)
    col1.metric("Outstanding", f"₹{df[df['payment_status']=='Pending']['amount'].sum():,.0f}")
    col2.metric("Trust Index", "742", "+12 pts")
    col3.metric("Recovery Rate", "88%", "AI Optimized")
    
    fig = px.bar(df, x='customer_name', y='amount', color='payment_status', title="Credit Distribution")
    st.plotly_chart(fig, use_container_width=True)

# ==========================================
# 5. MAIN ROUTING LOGIC
# ==========================================
authentication_status = authenticator.login('Login', 'sidebar')

if st.session_state["authentication_status"]:
    # --- LOGGED IN ---
    authenticator.logout('Logout', 'sidebar')
    df = get_data()
    
    if df.empty:
        st.warning("No data found. Please upload a ledger or wait for sync.")
        # Minimal dummy data for demonstration
        df = pd.DataFrame({'customer_name':['A', 'B'], 'amount':[100, 200], 'payment_status':['Pending', 'Paid'], 
                           'purchase_date':[datetime.now(), datetime.now()], 'due_date':[datetime.now(), datetime.now()]})

    st.sidebar.title(f"Welcome, {st.session_state['name']}!")
    menu = st.sidebar.radio("Navigation", [
        "Dashboard", 
        "Global Trust Network", 
        "AI Recovery Engine", 
        "Cash Flow Forecast",
        "Settings"
    ])

    if menu == "Dashboard":
        module_dashboard(df)
    elif menu == "Global Trust Network":
        module_global_trust()
    elif menu == "AI Recovery Engine":
        st.info("AI Nudge Engine: Integrating Social Proof reminders...")
        # (Reference your previous module_5_behavioral_engine code here)
    elif menu == "Cash Flow Forecast":
        st.info("Predicting 30-day inflow based on behavioral patterns...")

elif st.session_state["authentication_status"] is False:
    st.error('Username/password is incorrect')

elif st.session_state["authentication_status"] is None:
    # --- LANDING PAGE ---
    col1, col2 = st.columns([1.5, 1])
    with col1:
        st.markdown('<h1 class="main-title">Better than <span class="highlight">Ledgers</span>. Faster than <span class="highlight">Banks</span>.</h1>', unsafe_allow_html=True)
        st.markdown("### Khatakhat AI uses behavioral science to recover your stuck capital.")
        
        st.write("---")
        st.markdown("✅ **AI Behavioral Reminders** (WhatsApp Integrated)")
        st.markdown("✅ **Global Trust Network** (CIBIL for small shops)")
        st.markdown("✅ **Predictive Cash Flow** (Know your future balance)")
        
        st.info("👈 **Login via the sidebar** to start recovering your money.")
    
    with col2:
        # Placeholder for Lottie or Image
        st.image("https://img.freepik.com/free-vector/financial-analytics-concept-illustration_114360-143.jpg")
