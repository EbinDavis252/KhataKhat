import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px
from datetime import datetime
import hashlib

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
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
        background-color: #F8FAFC;
    }
    
    /* Metrics Styling */
    [data-testid="stMetricValue"] {
        font-size: 28px;
        font-weight: 700;
        color: #0F172A;
    }
    
    /* Button Styling */
    .stButton>button {
        width: 100%;
        border-radius: 8px;
        height: 3em;
        background-color: #0F172A;
        color: white;
        border: none;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    
    .stButton>button:hover {
        background-color: #2563EB;
        border: none;
        color: white;
    }

    /* Landing Page Hero */
    .hero-section {
        padding: 60px 20px;
        text-align: center;
        background: white;
        border-radius: 15px;
        border: 1px solid #E2E8F0;
        margin-bottom: 30px;
    }
    
    .punchline {
        font-size: 2.5rem;
        font-weight: 800;
        background: linear-gradient(90deg, #0F172A, #2563EB);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- DATABASE ENGINE ---
def get_db_connection():
    conn = sqlite3.connect('khatakhat_pro.db', check_same_thread=False)
    return conn

def init_db():
    conn = get_db_connection()
    c = conn.cursor()
    # Users table
    c.execute('''CREATE TABLE IF NOT EXISTS users (
                    username TEXT PRIMARY KEY, 
                    password TEXT, 
                    business_name TEXT)''')
    # Ledger table
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

# --- AUTH LOGIC ---
def make_hashes(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

def check_hashes(password, hashed_text):
    if make_hashes(password) == hashed_text:
        return hashed_text
    return False

# --- SESSION STATE INITIALIZATION ---
if 'auth_state' not in st.session_state:
    st.session_state.auth_state = 'landing' # landing, register, login, dashboard
if 'user' not in st.session_state:
    st.session_state.user = None

# --- UI COMPONENTS ---

def landing_page():
    st.markdown("""
        <div class="hero-section">
            <p style="color: #2563EB; font-weight: 600; letter-spacing: 1.5px; text-transform: uppercase; margin-bottom: 0;">Smarter Credit. Faster Recovery.</p>
            <h1 class="punchline">"Dhanda Udhaari Se Nahi, Delivery Se Chalta Hai!"</h1>
            <p style="font-size: 1.2rem; color: #64748B; max-width: 800px; margin: 0 auto 30px auto;">
                Khatakhat AI is India’s first intelligent receivables platform. We don't just record transactions; 
                we predict who will pay and automate your recovery using AI.
            </p>
        </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)
    with col1:
        st.subheader("🚀 Track Udhaar")
        st.write("Digitalize your bahi-khata with zero effort. Real-time sync across devices.")
    with col2:
        st.subheader("🧠 Predict Risk")
        st.write("Our AI analyzes customer behavior to give you a 'Trust Score' before you give credit.")
    with col3:
        st.subheader("📲 Smart Reminders")
        st.write("Automated WhatsApp and SMS reminders that sound professional, not pushy.")

    st.markdown("---")
    c1, c2, c3 = st.columns([1, 2, 1])
    with col2:
        if st.button("Get Started - Register Business"):
            st.session_state.auth_state = 'register'
            st.rerun()

def registration_page():
    st.markdown("<h2 style='text-align: center;'>Create Your Merchant Account</h2>", unsafe_allow_html=True)
    with st.container():
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            new_user = st.text_input("Username / Mobile")
            new_biz = st.text_input("Business Name")
            new_pw = st.text_input("Password", type='password')
            if st.button("Register Now"):
                if new_user and new_pw:
                    conn = get_db_connection()
                    c = conn.cursor()
                    try:
                        c.execute('INSERT INTO users(username, password, business_name) VALUES (?,?,?)', 
                                 (new_user, make_hashes(new_pw), new_biz))
                        conn.commit()
                        st.success("Account Created Successfully!")
                        st.session_state.auth_state = 'login'
                        st.rerun()
                    except sqlite3.IntegrityError:
                        st.error("Username already exists.")
                    finally:
                        conn.close()
                else:
                    st.warning("Please fill all fields.")
            if st.button("Back to Home"):
                st.session_state.auth_state = 'landing'
                st.rerun()

def login_page():
    st.markdown("<h2 style='text-align: center;'>Merchant Login</h2>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        username = st.text_input("Username")
        password = st.text_input("Password", type='password')
        if st.button("Login"):
            conn = get_db_connection()
            c = conn.cursor()
            c.execute('SELECT password FROM users WHERE username = ?', (username,))
            data = c.fetchone()
            conn.close()
            if data and check_hashes(password, data[0]):
                st.session_state.auth_state = 'dashboard'
                st.session_state.user = username
                st.rerun()
            else:
                st.error("Incorrect Username/Password")

def dashboard():
    st.title(f"📊 {st.session_state.user}'s Dashboard")
    
    # Load Data
    conn = get_db_connection()
    df = pd.read_sql(f"SELECT * FROM ledger WHERE merchant = '{st.session_state.user}'", conn)
    conn.close()

    if df.empty:
        st.info("No records found. Please upload a ledger via the sidebar.")
    else:
        # 1. Metrics
        m1, m2, m3, m4 = st.columns(4)
        total_out = df[df['status'] != 'Paid']['amount'].sum()
        total_rec = df[df['status'] == 'Paid']['amount'].sum()
        avg_trust = df['trust_score'].mean()
        recovery = (total_rec / (total_out + total_rec)) * 100 if (total_out + total_rec) > 0 else 0
        
        m1.metric("Outstanding", f"₹{total_out:,.0f}")
        m2.metric("Collected", f"₹{total_rec:,.0f}")
        m3.metric("Recovery Rate", f"{recovery:.1f}%")
        m4.metric("Avg Trust Score", f"{int(avg_trust)}")

        # 2. Visuals
        c1, c2 = st.columns(2)
        with c1:
            fig = px.pie(df, names='status', values='amount', hole=0.5, 
                         color_discrete_sequence=['#0F172A', '#2563EB', '#CBD5E1'],
                         title="Collection Status")
            st.plotly_chart(fig, use_container_width=True)
        with c2:
            fig2 = px.bar(df[df['status'] != 'Paid'].nlargest(5, 'amount'), x='customer', y='amount',
                          title="Top Receivables", color_discrete_sequence=['#EF4444'])
            st.plotly_chart(fig2, use_container_width=True)

def upload_view():
    st.header("Ledger Import")
    file = st.file_uploader("Upload CSV Ledger", type=['csv'])
    if file:
        data = pd.read_csv(file)
        # Standardization logic
        mapping = {
            'customer_id': 'customer', 'Customer_Name': 'customer', 'credit_amount': 'amount', 
            'payment_status': 'status', 'days_overdue': 'days_due'
        }
        final_df = pd.DataFrame()
        for old, new in mapping.items():
            if old in data.columns: final_df[new] = data[old]
        
        if 'trust_score' not in data.columns:
            final_df['trust_score'] = 750 # Default
        
        final_df['merchant'] = st.session_state.user
        
        if st.button("Confirm and Save to Database"):
            conn = get_db_connection()
            final_df.to_sql('ledger', conn, if_exists='append', index=False)
            conn.commit()
            conn.close()
            st.success("Data synced successfully!")

def reminder_view():
    st.header("Smart Reminder Engine")
    conn = get_db_connection()
    df = pd.read_sql(f"SELECT * FROM ledger WHERE merchant = '{st.session_state.user}' AND status != 'Paid'", conn)
    conn.close()
    
    if not df.empty:
        selected = st.selectbox("Select Customer", df['customer'].unique())
        row = df[df['customer'] == selected].iloc[0]
        st.write(f"**Amount Due:** ₹{row['amount']}")
        st.write(f"**Days Overdue:** {row['days_due']}")
        
        msg = f"Dear {selected}, your payment of ₹{row['amount']} is overdue by {row['days_due']} days. Kindly clear at your earliest. - Team Khatakhat AI"
        st.text_area("Message Preview", value=msg)
        
        if st.button("Send Smart Reminder"):
            st.toast("Reminder Sent via WhatsApp API Mock", icon="✅")
    else:
        st.success("Zero pending dues. Great job!")

# --- MAIN CONTROLLER ---
if st.session_state.auth_state == 'landing':
    landing_page()
elif st.session_state.auth_state == 'register':
    registration_page()
elif st.session_state.auth_state == 'login':
    login_page()
elif st.session_state.auth_state == 'dashboard':
    # Sidebar
    st.sidebar.title("Khatakhat AI")
    st.sidebar.markdown(f"Merchant: **{st.session_state.user}**")
    nav = st.sidebar.radio("Navigation", ["Dashboard", "Upload Ledger", "Reminders", "Reports", "Audit Export"])
    
    if nav == "Dashboard":
        dashboard()
    elif nav == "Upload Ledger":
        upload_view()
    elif nav == "Reminders":
        reminder_view()
    elif nav == "Reports":
        st.header("Financial Reports")
        st.info("Advanced reporting module generating weekly summaries...")
    elif nav == "Audit Export":
        st.header("Audit Export")
        conn = get_db_connection()
        full_df = pd.read_sql(f"SELECT * FROM ledger WHERE merchant = '{st.session_state.user}'", conn)
        conn.close()
        st.download_button("Download CSV", full_df.to_csv(index=False), "audit.csv", "text/csv")
        st.dataframe(full_df)

    if st.sidebar.button("Logout"):
        st.session_state.auth_state = 'landing'
        st.session_state.user = None
        st.rerun()
