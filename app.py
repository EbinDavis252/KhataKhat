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
# 2. AUTHENTICATION SETUP (Simplified for MVP)
# ==========================================
# We'll use a standard dictionary for users
users = {
    "kd_merchant": "admin123"
}

# Logic to handle login state manually since the hash was failing
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

def login_form():
    with st.sidebar:
        st.title("Merchant Login")
        user_input = st.text_input("Username")
        pass_input = st.text_input("Password", type="password")
        if st.button("Login"):
            if user_input in users and users[user_input] == pass_input:
                st.session_state["authenticated"] = True
                st.session_state["name"] = "KD"
                st.rerun()
            else:
                st.error("Invalid credentials")

# ==========================================
# 4. MAIN ROUTING
# ==========================================
if st.session_state["authenticated"]:
    # --- LOGGED IN STATE ---
    if st.sidebar.button("Logout"):
        st.session_state["authenticated"] = False
        st.rerun()
    
    df = get_data()
    if df.empty:
        df = generate_sample_data()

    st.sidebar.title("Khatakhat 🚀")
    nav = st.sidebar.radio("Navigation", ["Dashboard", "Recovery Engine", "Ledger", "Trust Network"])

    if nav == "Dashboard":
        module_dashboard(df)
    elif nav == "Recovery Engine":
        module_recovery_engine(df)
    elif nav == "Ledger":
        module_ledger(df)
    elif nav == "Trust Network":
        module_trust_network()

else:
    # --- LANDING PAGE & LOGIN ---
    login_form()
    
    col1, col2 = st.columns([1.5, 1])
    with col1:
        st.markdown('<h1 class="main-title">Better than <span class="highlight">Ledgers</span>.</h1>', unsafe_allow_html=True)
        st.write("### AI-powered recovery for small businesses.")
        st.info("👈 Please login via the sidebar to access your shop's engine.")
    with col2:
        st.image("https://img.freepik.com/free-vector/financial-analytics-concept-illustration_114360-143.jpg")
