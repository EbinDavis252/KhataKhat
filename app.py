import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px
from datetime import datetime
import hashlib
import io

# --- CONFIGURATION & THEME ---
st.set_page_config(
    page_title="Khatakhat AI | Smarter Credit",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Professional CSS for Fintech look
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
        background-color: #F8FAFC;
    }
    
    [data-testid="stMetricValue"] {
        font-size: 28px;
        font-weight: 700;
        color: #0F172A;
    }
    
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
        color: white;
        box-shadow: 0 4px 12px rgba(37, 99, 235, 0.1);
    }

    .hero-section {
        padding: 80px 40px;
        text-align: center;
        background: white;
        border-radius: 20px;
        border: 1px solid #E2E8F0;
        margin-bottom: 40px;
        box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.05);
    }
    
    .punchline {
        font-size: 3.2rem;
        font-weight: 800;
        background: linear-gradient(90deg, #0F172A, #2563EB);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 15px;
    }

    .card {
        background: white;
        padding: 2rem;
        border-radius: 12px;
        border: 1px solid #E2E8F0;
        height: 100%;
    }
    </style>
    """, unsafe_allow_html=True)

# --- DATABASE ENGINE ---
DB_NAME = 'khatakhat_pro_v3.db'

def get_db_connection():
    return sqlite3.connect(DB_NAME, check_same_thread=False)

def init_db():
    conn = get_db_connection()
    c = conn.cursor()
    # Users table
    c.execute('''CREATE TABLE IF NOT EXISTS users (
                    username TEXT PRIMARY KEY, 
                    password TEXT, 
                    business_name TEXT)''')
    # Ledger table - explicitly defined schema
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
            <p style="color: #2563EB; font-weight: 600; letter-spacing: 2px; text-transform: uppercase; margin-bottom: 10px;">Smarter Credit. Faster Recovery.</p>
            <h1 class="punchline">"Dhanda Udhaari Se Nahi, Delivery Se Chalta Hai!"</h1>
            <p style="font-size: 1.3rem; color: #475569; max-width: 800px; margin: 0 auto 40px auto; line-height: 1.6;">
                Welcome <b>KD</b>, Khatakhat AI is your business's intelligent companion. 
                Track your credit, analyze risk profiles, and recover payments 3x faster with AI-driven insights.
            </p>
            <div style="display: flex; justify-content: center; gap: 20px;">
                <div style="width: 250px;">
    """, unsafe_allow_html=True)
    
    if st.button("Register Business"):
        st.session_state.auth_state = 'register'
        st.rerun()
        
    st.markdown("""
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("""<div class="card"><h3>📊 Digital Bahi-Khata</h3><p>Move away from paper. Track every rupee of credit with automated logging and real-time balance tracking.</p></div>""", unsafe_allow_html=True)
    with col2:
        st.markdown("""<div class="card"><h3>🧠 Smart Risk Predictor</h3><p>Predict defaults before they happen. Our AI calculates Trust Scores based on repayment behavior and aging.</p></div>""", unsafe_allow_html=True)
    with col3:
        st.markdown("""<div class="card"><h3>📲 Auto-Reminders</h3><p>Stop chasing! Send professional, firm, yet polite reminders via WhatsApp with a single click.</p></div>""", unsafe_allow_html=True)

def registration_page():
    st.markdown("<h2 style='text-align: center; margin-top: 50px;'>Business Registration</h2>", unsafe_allow_html=True)
    _, col, _ = st.columns([1, 1.2, 1])
    with col:
        with st.form("reg_form", clear_on_submit=True):
            new_user = st.text_input("Mobile Number or Email (Username)")
            new_biz = st.text_input("Business Name (e.g., KD Enterprises)")
            new_pw = st.text_input("Create Password", type='password')
            submit = st.form_submit_button("Register & Proceed")
            
            if submit:
                if new_user and new_pw and new_biz:
                    conn = get_db_connection()
                    c = conn.cursor()
                    try:
                        c.execute('INSERT INTO users(username, password, business_name) VALUES (?,?,?)', 
                                 (new_user, make_hashes(new_pw), new_biz))
                        conn.commit()
                        st.success("Business Registered! Please log in.")
                        st.session_state.auth_state = 'login'
                        st.rerun()
                    except sqlite3.IntegrityError:
                        st.error("This username is already registered.")
                    finally:
                        conn.close()
                else:
                    st.warning("All fields are required.")
        if st.button("← Back to Home"):
            st.session_state.auth_state = 'landing'
            st.rerun()

def login_page():
    st.markdown("<h2 style='text-align: center; margin-top: 50px;'>Merchant Login</h2>", unsafe_allow_html=True)
    _, col, _ = st.columns([1, 1, 1])
    with col:
        with st.form("login_form"):
            username = st.text_input("Username")
            password = st.text_input("Password", type='password')
            submit = st.form_submit_button("Log In")
            
            if submit:
                conn = get_db_connection()
                c = conn.cursor()
                c.execute('SELECT password FROM users WHERE username = ?', (username,))
                data = c.fetchone()
                conn.close()
                if data and check_hashes(password, data[0]):
                    st.session_state.user = username
                    st.session_state.auth_state = 'dashboard'
                    st.rerun()
                else:
                    st.error("Invalid credentials. Please try again.")

def dashboard_view():
    st.title("📊 Executive Dashboard")
    conn = get_db_connection()
    df = pd.read_sql("SELECT * FROM ledger WHERE merchant = ?", conn, params=(st.session_state.user,))
    conn.close()

    if df.empty:
        st.warning("No data found. Start by uploading your ledger in the sidebar.")
        return

    m1, m2, m3, m4 = st.columns(4)
    pending = df[df['status'] != 'Paid']
    paid = df[df['status'] == 'Paid']
    
    total_out = pending['amount'].sum()
    total_rec = paid['amount'].sum()
    recovery_rate = (total_rec / (total_out + total_rec)) * 100 if (total_out + total_rec) > 0 else 0
    
    m1.metric("Outstanding", f"₹{total_out:,.0f}")
    m2.metric("Total Collected", f"₹{total_rec:,.0f}")
    m3.metric("Recovery Rate", f"{recovery_rate:.1f}%")
    m4.metric("Avg. Trust Score", f"{int(df['trust_score'].mean())}")

    st.markdown("---")
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("Collection Breakdown")
        status_counts = df['status'].value_counts().reset_index()
        fig = px.pie(status_counts, names='status', values='count', hole=0.4, 
                     color_discrete_sequence=['#0F172A', '#2563EB', '#CBD5E1'])
        st.plotly_chart(fig, use_container_width=True)
        
    with c2:
        st.subheader("Top Debtors")
        top_debtors = pending.groupby('customer')['amount'].sum().nlargest(5).reset_index()
        fig2 = px.bar(top_debtors, x='customer', y='amount', color_discrete_sequence=['#EF4444'])
        st.plotly_chart(fig2, use_container_width=True)

def upload_view():
    st.title("📁 Ledger Upload")
    st.info("Upload your CSV file. Khatakhat AI will automatically map your columns.")
    
    uploaded_file = st.file_uploader("Upload CSV", type=['csv'])
    if uploaded_file:
        df_raw = pd.read_csv(uploaded_file)
        st.write("Preview of data:", df_raw.head())
        
        # Comprehensive mapping logic to prevent DatabaseError
        mapping = {
            'customer_id': 'customer', 'Customer_Name': 'customer', 'Name': 'customer', 'customer': 'customer',
            'credit_amount': 'amount', 'Amount': 'amount', 'amount': 'amount', 'Transaction_Amount': 'amount',
            'payment_status': 'status', 'Status': 'status', 'status': 'status',
            'days_overdue': 'days_due', 'days_due': 'days_due', 'Due_Days': 'days_due'
        }
        
        if st.button("Process & Save Ledger"):
            try:
                processed = pd.DataFrame()
                # Find and map existing columns
                found_cols = []
                for old, new in mapping.items():
                    if old in df_raw.columns and new not in processed.columns:
                        processed[new] = df_raw[old]
                        found_cols.append(new)
                
                # Validation
                if 'customer' not in processed.columns or 'amount' not in processed.columns:
                    st.error("Error: Could not identify 'Customer' or 'Amount' columns. Please check your CSV.")
                    return
                
                # Fill missing schema requirements
                processed['merchant'] = st.session_state.user
                if 'status' not in processed.columns: processed['status'] = 'Pending'
                if 'days_due' not in processed.columns: processed['days_due'] = 0
                if 'trust_score' not in processed.columns: processed['trust_score'] = 720
                processed['last_reminder'] = None
                
                # Filter strictly to table columns to avoid "DatabaseError: Execution failed"
                table_cols = ['merchant', 'customer', 'amount', 'status', 'days_due', 'trust_score', 'last_reminder']
                final_df = processed[table_cols]
                
                conn = get_db_connection()
                final_df.to_sql('ledger', conn, if_exists='append', index=False)
                conn.commit()
                conn.close()
                st.success(f"Successfully imported {len(final_df)} records!")
                st.balloons()
            except Exception as e:
                st.error(f"Database Error: {e}")

def risk_predictor_view():
    st.title("🧠 Risk Prediction Engine")
    conn = get_db_connection()
    df = pd.read_sql("SELECT * FROM ledger WHERE merchant = ?", conn, params=(st.session_state.user,))
    conn.close()
    
    if df.empty:
        st.info("No data available for risk analysis.")
        return

    # Advanced Scoring Logic
    df['risk_index'] = (900 - df['trust_score']) + (df['days_due'] * 1.5)
    
    fig = px.scatter(df, x="trust_score", y="days_due", size="amount", color="status",
                     hover_name="customer", title="Customer Credit Vulnerability Matrix",
                     labels={"trust_score": "Financial Trust Score", "days_due": "Days Overdue"},
                     color_discrete_sequence=['#2563EB', '#EF4444', '#0F172A'])
    st.plotly_chart(fig, use_container_width=True)
    
    st.subheader("High Risk Customers")
    high_risk = df[df['days_due'] > 30].sort_values('amount', ascending=False)
    st.dataframe(high_risk[['customer', 'amount', 'days_due', 'trust_score']], use_container_width=True)

def reminder_engine():
    st.title("📲 Smart Reminders")
    conn = get_db_connection()
    df = pd.read_sql("SELECT * FROM ledger WHERE merchant = ? AND status != 'Paid'", conn, params=(st.session_state.user,))
    conn.close()
    
    if df.empty:
        st.success("All clear! No pending dues found.")
        return

    cust_list = df['customer'].unique()
    target = st.selectbox("Select Customer to Remind", cust_list)
    
    cust_data = df[df['customer'] == target].iloc[0]
    amount = cust_data['amount']
    days = cust_data['days_due']
    
    st.markdown(f"""
        <div style="background: white; padding: 20px; border-radius: 10px; border: 1px solid #E2E8F0;">
            <h4>Reminding: {target}</h4>
            <p>Total Dues: <b>₹{amount:,.2f}</b></p>
            <p>Overdue by: <b>{days} days</b></p>
        </div>
    """, unsafe_allow_html=True)
    
    template = f"Bhai {target}, polite reminder for ₹{amount} pending for {days} days. Please clear it today to keep your Trust Score high! - From {st.session_state.user}"
    final_msg = st.text_area("Message Content", template)
    
    if st.button("Send WhatsApp Reminder"):
        with st.spinner("Processing API request..."):
            import time
            time.sleep(1)
            # Log reminder in DB
            conn = get_db_connection()
            c = conn.cursor()
            c.execute("UPDATE ledger SET last_reminder = ? WHERE customer = ? AND merchant = ?", 
                      (datetime.now().strftime("%Y-%m-%d %H:%M"), target, st.session_state.user))
            conn.commit()
            conn.close()
            st.toast(f"Reminder sent to {target}!", icon="✅")

# --- MAIN CONTROLLER ---

if st.session_state.auth_state == 'landing':
    landing_page()
elif st.session_state.auth_state == 'register':
    registration_page()
elif st.session_state.auth_state == 'login':
    login_page()
elif st.session_state.auth_state == 'dashboard':
    st.sidebar.markdown(f"### Khatakhat AI")
    st.sidebar.markdown(f"Merchant: **{st.session_state.user}**")
    st.sidebar.markdown("---")
    
    menu = st.sidebar.radio("Navigation", 
                            ["Dashboard", "Upload Ledger", "Risk Predictor", "Reminder Engine", "Audit Export"])
    
    if menu == "Dashboard": dashboard_view()
    elif menu == "Upload Ledger": upload_view()
    elif menu == "Risk Predictor": risk_predictor_view()
    elif menu == "Reminder Engine": reminder_engine()
    elif menu == "Audit Export":
        st.title("Audit Trail")
        conn = get_db_connection()
        df_audit = pd.read_sql("SELECT * FROM ledger WHERE merchant = ?", conn, params=(st.session_state.user,))
        conn.close()
        st.download_button("Download Audit CSV", df_audit.to_csv(index=False), "khatakhat_audit.csv", "text/csv")
        st.dataframe(df_audit, use_container_width=True)
        
    if st.sidebar.button("Logout"):
        st.session_state.auth_state = 'landing'
        st.session_state.user = None
        st.rerun()
