import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px
from datetime import datetime
import hashlib
import io
import time

# --- CONFIGURATION & THEME ---
st.set_page_config(
    page_title="Khatakhat AI | Smarter Credit",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Professional CSS
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; background-color: #F8FAFC; }
    [data-testid="stMetricValue"] { font-size: 28px; font-weight: 700; color: #0F172A; }
    .stButton>button { width: 100%; border-radius: 8px; height: 3em; background-color: #0F172A; color: white; font-weight: 600; }
    .stButton>button:hover { background-color: #2563EB; border: none; }
    .hero-section { padding: 60px 20px; text-align: center; background: white; border-radius: 20px; border: 1px solid #E2E8F0; margin-bottom: 20px; }
    .punchline { font-size: 3rem; font-weight: 800; background: linear-gradient(90deg, #0F172A, #2563EB); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
    .card { background: white; padding: 1.5rem; border-radius: 12px; border: 1px solid #E2E8F0; height: 100%; }
    </style>
    """, unsafe_allow_html=True)

# --- DATABASE ENGINE ---
DB_NAME = 'khatakhat_pro_v3.db'

def get_db_connection():
    return sqlite3.connect(DB_NAME, check_same_thread=False)

def init_db():
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (
                    username TEXT PRIMARY KEY, 
                    password TEXT, 
                    business_name TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS ledger (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    merchant TEXT,
                    customer TEXT,
                    amount REAL,
                    status TEXT,
                    days_due INTEGER,
                    trust_score INTEGER,
                    last_reminder TEXT)''')
    conn.commit()
    conn.close()

init_db()

# --- AUTH LOGIC (With Secure Salt) ---
SALT = "friday_secure_system_v1" # Changing this will invalidate old passwords

def make_hashes(password):
    return hashlib.sha256(str.encode(password + SALT)).hexdigest()

def check_hashes(password, hashed_text):
    return make_hashes(password) == hashed_text

# --- SESSION STATE ---
if 'auth_state' not in st.session_state:
    st.session_state.auth_state = 'landing'
if 'user' not in st.session_state:
    st.session_state.user = None

# --- UI PAGES ---

def landing_page():
    st.markdown(f"""
        <div class="hero-section">
            <p style="color: #2563EB; font-weight: 600; letter-spacing: 2px; text-transform: uppercase;">Smarter Credit. Faster Recovery.</p>
            <h1 class="punchline">"Dhanda Udhaari Se Nahi, Delivery Se Chalta Hai!"</h1>
            <p style="font-size: 1.2rem; color: #475569; max-width: 700px; margin: 0 auto 30px auto;">
                Welcome <b>KD</b>. Khatakhat AI automates your bahi-khata, predicts risks, and collects payments 3x faster.
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns([1, 1, 1, 1])
    with col2:
        if st.button("🚀 Register Business"):
            st.session_state.auth_state = 'register'
            st.rerun()
    with col3:
        if st.button("🔑 Merchant Login"):
            st.session_state.auth_state = 'login'
            st.rerun()

    st.markdown("---")
    c1, c2, c3 = st.columns(3)
    with c1: st.markdown("""<div class="card"><h3>📊 Digital Ledger</h3><p>Track every rupee of credit with real-time balance tracking.</p></div>""", unsafe_allow_html=True)
    with c2: st.markdown("""<div class="card"><h3>🧠 Risk AI</h3><p>Predict defaults using our proprietary Trust Score algorithms.</p></div>""", unsafe_allow_html=True)
    with c3: st.markdown("""<div class="card"><h3>📲 WhatsApp Sync</h3><p>Send professional automated reminders with one click.</p></div>""", unsafe_allow_html=True)

def registration_page():
    st.subheader("Create Your Business Account")
    _, col, _ = st.columns([1, 1.2, 1])
    with col:
        with st.form("reg_form"):
            new_user = st.text_input("Mobile/Email (Username)")
            new_biz = st.text_input("Business Name")
            new_pw = st.text_input("Password", type='password')
            submit = st.form_submit_button("Register & Get Started")
            
            if submit:
                if new_user and new_pw and new_biz:
                    conn = get_db_connection()
                    c = conn.cursor()
                    try:
                        c.execute('INSERT INTO users VALUES (?,?,?)', (new_user, make_hashes(new_pw), new_biz))
                        conn.commit()
                        st.success("Registration Successful!")
                        time.sleep(1)
                        st.session_state.auth_state = 'login'
                        st.rerun()
                    except: st.error("Username already exists.")
                    finally: conn.close()
        if st.button("← Back"):
            st.session_state.auth_state = 'landing'
            st.rerun()

def login_page():
    st.subheader("Login to Dashboard")
    _, col, _ = st.columns([1, 1, 1])
    with col:
        with st.form("login_form"):
            username = st.text_input("Username")
            password = st.text_input("Password", type='password')
            if st.form_submit_button("Login"):
                conn = get_db_connection()
                c = conn.cursor()
                c.execute('SELECT password FROM users WHERE username = ?', (username,))
                data = c.fetchone()
                conn.close()
                if data and check_hashes(password, data[0]):
                    st.session_state.user = username
                    st.session_state.auth_state = 'dashboard'
                    st.rerun()
                else: st.error("Invalid Credentials")
        if st.button("← Back"):
            st.session_state.auth_state = 'landing'
            st.rerun()

def dashboard_view():
    st.title("📊 Executive Dashboard")
    conn = get_db_connection()
    df = pd.read_sql("SELECT * FROM ledger WHERE merchant = ?", conn, params=(st.session_state.user,))
    conn.close()

    if df.empty:
        st.info("Your ledger is empty. Upload a CSV to see insights!")
        return

    m1, m2, m3, m4 = st.columns(4)
    pending = df[df['status'] != 'Paid']
    m1.metric("Outstanding", f"₹{pending['amount'].sum():,.0f}")
    m2.metric("Collection Rate", f"{(len(df[df['status']=='Paid'])/len(df))*100:.1f}%")
    m3.metric("High Risk Debtors", len(df[df['days_due'] > 30]))
    m4.metric("Avg Trust Score", int(df['trust_score'].mean()))

    st.markdown("---")
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("Trust Score Distribution")
        fig = px.histogram(df, x="trust_score", color_discrete_sequence=['#2563EB'])
        st.plotly_chart(fig, use_container_width=True)
    with c2:
        st.subheader("Top Delinquent Accounts")
        top_d = pending.nlargest(5, 'amount')
        st.bar_chart(top_d.set_index('customer')['amount'])

def upload_view():
    st.title("📁 Data Integration")
    
    # Helpful Sample Generator
    sample_df = pd.DataFrame({
        'Customer_Name': ['Rahul Sharma', 'Priya Gupta'],
        'Amount': [5000, 12000],
        'Due_Days': [15, 45],
        'Status': ['Pending', 'Pending']
    })
    st.download_button("📥 Download Sample CSV Template", sample_df.to_csv(index=False), "template.csv", "text/csv")
    
    uploaded_file = st.file_uploader("Upload Business Ledger (CSV)", type=['csv'])
    if uploaded_file:
        df_raw = pd.read_csv(uploaded_file)
        st.write("Data Preview:", df_raw.head())
        
        if st.button("Sync with AI Ledger"):
            # Robust Column Mapping
            mapping = {'Customer_Name': 'customer', 'Amount': 'amount', 'Due_Days': 'days_due', 'Status': 'status'}
            processed = pd.DataFrame()
            for old, new in mapping.items():
                if old in df_raw.columns: processed[new] = df_raw[old]
            
            processed['merchant'] = st.session_state.user
            processed['trust_score'] = 700 # Default score
            processed['last_reminder'] = None
            
            conn = get_db_connection()
            processed.to_sql('ledger', conn, if_exists='append', index=False)
            conn.commit()
            conn.close()
            st.success("Cloud Sync Complete!")
            st.balloons()

# --- MAIN CONTROLLER ---
if st.session_state.auth_state == 'landing': landing_page()
elif st.session_state.auth_state == 'register': registration_page()
elif st.session_state.auth_state == 'login': login_page()
elif st.session_state.auth_state == 'dashboard':
    st.sidebar.title("Khatakhat AI")
    st.sidebar.write(f"Logged in: **{st.session_state.user}**")
    menu = st.sidebar.radio("Navigate", ["Dashboard", "Upload Data", "Reminders", "Risk Matrix"])
    
    if menu == "Dashboard": dashboard_view()
    elif menu == "Upload Data": upload_view()
    elif menu == "Reminders": st.write("Reminder Engine Module - Ready for Integration")
    elif menu == "Risk Matrix": st.write("Risk Matrix Visualization - Ready for Integration")
    
    if st.sidebar.button("Logout"):
        st.session_state.auth_state = 'landing'
        st.session_state.user = None
        st.rerun()
