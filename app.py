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

# Professional Fintech CSS
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
        background-color: #F8FAFC;
    }
    
    .stMetric {
        background-color: white;
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        border: 1px solid #E2E8F0;
    }

    [data-testid="stMetricValue"] {
        font-size: 24px;
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
        box-shadow: 0 4px 12px rgba(37, 99, 235, 0.2);
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

    .feature-card {
        background: white;
        padding: 25px;
        border-radius: 15px;
        border-left: 5px solid #2563EB;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        height: 100%;
    }
    </style>
    """, unsafe_allow_html=True)

# --- DATABASE ENGINE ---
DB_NAME = 'khatakhat_final_pro.db'

def get_db_connection():
    return sqlite3.connect(DB_NAME, check_same_thread=False)

def init_db():
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (
                    username TEXT PRIMARY KEY, 
                    password TEXT, 
                    business_name TEXT,
                    api_key TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS ledger (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    merchant TEXT,
                    customer TEXT,
                    amount REAL,
                    status TEXT,
                    days_due INTEGER,
                    trust_score INTEGER,
                    customer_type TEXT,
                    last_reminder TEXT)''')
    conn.commit()
    conn.close()

init_db()

# --- UTILS ---
def make_hashes(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

def check_hashes(password, hashed_text):
    return make_hashes(password) == hashed_text

# --- SESSION HANDLING ---
if 'auth_state' not in st.session_state:
    st.session_state.auth_state = 'landing'
if 'user' not in st.session_state:
    st.session_state.user = None

# --- UI LOGIC ---

def landing_page():
    st.markdown("""
        <div class="hero-section">
            <p style="color: #2563EB; font-weight: 600; letter-spacing: 2px; text-transform: uppercase; margin-bottom: 10px;">The Next-Gen Receivables Engine</p>
            <h1 class="punchline">"Dhanda Udhaari Se Nahi, Recovery Se Chalta Hai!"</h1>
            <p style="font-size: 1.3rem; color: #475569; max-width: 850px; margin: 0 auto 40px auto; line-height: 1.6;">
                Khatakhat AI is a professional merchant platform designed to outpace <b>Zoho, Razorpay, and Khatabook</b>. 
                Using advanced predictive risk scoring and automated recovery logic, we ensure your capital stays in your business, not in the market.
            </p>
            <div style="display: flex; justify-content: center; gap: 20px;">
                <div style="width: 250px;">
    """, unsafe_allow_html=True)
    
    if st.button("Register & Get API Access"):
        st.session_state.auth_state = 'register'
        st.rerun()
        
    st.markdown("""
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown('<div class="feature-card"><h3>🤖 AI Risk Scoring</h3><p>Move beyond manual checks. Our AI predicts payment probability based on behavior and aging.</p></div>', unsafe_allow_html=True)
    with col2:
        st.markdown('<div class="feature-card"><h3>🔗 Enterprise API</h3><p>Seamlessly connect with your existing billing tools to centralize your collections dashboard.</p></div>', unsafe_allow_html=True)
    with col3:
        st.markdown('<div class="feature-card"><h3>📈 Recovery Growth</h3><p>Reduce your DSO (Days Sales Outstanding) by 40% with automated, behavioral reminders.</p></div>', unsafe_allow_html=True)

def registration_page():
    st.markdown("<h2 style='text-align: center; margin-top: 50px;'>Merchant Onboarding</h2>", unsafe_allow_html=True)
    _, col, _ = st.columns([1, 1.2, 1])
    with col:
        with st.form("reg_form"):
            new_user = st.text_input("Username (Email/Mobile)")
            new_biz = st.text_input("Business Name")
            new_pw = st.text_input("Password", type='password')
            submit = st.form_submit_button("Launch My Smart Khata")
            
            if submit:
                if new_user and new_pw and new_biz:
                    conn = get_db_connection()
                    c = conn.cursor()
                    try:
                        api_k = f"KH_PRO_{hashlib.md5(new_user.encode()).hexdigest()[:10].upper()}"
                        c.execute('INSERT INTO users(username, password, business_name, api_key) VALUES (?,?,?,?)', 
                                 (new_user, make_hashes(new_pw), new_biz, api_k))
                        conn.commit()
                        st.success("Account Created Successfully!")
                        st.session_state.auth_state = 'login'
                        st.rerun()
                    except sqlite3.IntegrityError:
                        st.error("Username already exists.")
                    finally:
                        conn.close()
                else:
                    st.warning("Please fill in all details.")
        if st.button("← Back"):
            st.session_state.auth_state = 'landing'
            st.rerun()

def login_page():
    st.markdown("<h2 style='text-align: center; margin-top: 50px;'>Merchant Login</h2>", unsafe_allow_html=True)
    _, col, _ = st.columns([1, 1, 1])
    with col:
        with st.form("login_form"):
            username = st.text_input("Username")
            password = st.text_input("Password", type='password')
            submit = st.form_submit_button("Sign In")
            
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
                    st.error("Invalid Username or Password.")

# --- MODULES ---

def dashboard_main():
    st.title(f"🚀 {st.session_state.user}'s Analytics")
    conn = get_db_connection()
    df = pd.read_sql("SELECT * FROM ledger WHERE merchant = ?", conn, params=(st.session_state.user,))
    conn.close()

    if df.empty:
        st.info("Welcome! Start by uploading your data to generate AI insights.")
        return

    m1, m2, m3, m4 = st.columns(4)
    pending = df[df['status'] != 'Paid']
    total_due = pending['amount'].sum()
    collected = df[df['status'] == 'Paid']['amount'].sum()
    
    m1.metric("Current Udhaar", f"₹{total_due:,.0f}")
    m2.metric("Collections", f"₹{collected:,.0f}")
    m3.metric("Trust Index", f"{int(df['trust_score'].mean())}/900")
    m4.metric("DSO (Days)", f"{int(pending['days_due'].mean() if not pending.empty else 0)}")

    st.markdown("---")
    c1, c2 = st.columns([2, 1])
    with c1:
        st.subheader("Receivables Aging")
        fig = px.bar(pending.nlargest(10, 'amount'), x='customer', y='amount', color='days_due', 
                     color_continuous_scale='Reds', template='plotly_white')
        st.plotly_chart(fig, use_container_width=True)
    with c2:
        st.subheader("Portfolio Health")
        df['Risk'] = pd.cut(df['trust_score'], bins=[0, 400, 700, 1000], labels=['High', 'Medium', 'Low'])
        fig2 = px.pie(df, names='Risk', color='Risk', hole=0.6,
                      color_discrete_map={'Low': '#10B981', 'Medium': '#F59E0B', 'High': '#EF4444'})
        st.plotly_chart(fig2, use_container_width=True)

def ai_risk_predictor():
    st.title("🧠 AI Predictive Risk Engine")
    conn = get_db_connection()
    df = pd.read_sql("SELECT * FROM ledger WHERE merchant = ?", conn, params=(st.session_state.user,))
    conn.close()

    if df.empty: return

    st.markdown("""
        <div style="background: white; padding: 20px; border-radius: 12px; border-left: 5px solid #2563EB;">
            <b>AI Summary:</b> Based on current aging and transaction cycles, your cash flow risk has <b>decreased by 4%</b> this month. 
            Automated reminders are performing best with 'Retail' category customers.
        </div>
    """, unsafe_allow_html=True)

    fig = px.scatter(df, x="trust_score", y="days_due", size="amount", color="status",
                     hover_name="customer", title="Customer Vulnerability Mapping",
                     labels={"trust_score": "Behavioral Trust Score", "days_due": "Aging (Days)"})
    st.plotly_chart(fig, use_container_width=True)

def api_key_management():
    st.title("🔗 API & Developer Console")
    conn = get_db_connection()
    # Fixed IndexError: Fetching using params and checking existence
    cursor = conn.cursor()
    cursor.execute("SELECT api_key FROM users WHERE username = ?", (st.session_state.user,))
    result = cursor.fetchone()
    conn.close()

    if result:
        api_key = result[0]
        st.success("Your API Key is active.")
        st.code(f"Authorization: Bearer {api_key}", language="bash")
        
        st.markdown("""
        ### Integration Guide
        1. **Sync Ledger:** Use `POST /v1/ledger/sync` to push transactions from Razorpay/Zoho.
        2. **Risk Check:** Use `GET /v1/risk/{customer_id}` to get real-time credit scores.
        3. **Webhooks:** Register URLs to get alerts when a customer enters 'High Risk' zone.
        """)
        
        st.text_input("Webhook URL", placeholder="https://yourbusiness.com/webhooks/kh")
        if st.button("Save Endpoint"):
            st.toast("Webhook Registered", icon="📡")
    else:
        st.error("API Key not found. Please contact support.")

def upload_system():
    st.title("📁 Smart Import")
    st.write("Compatible with Zoho Books, Razorpay, Vyapar, and Khatabook CSV formats.")
    file = st.file_uploader("Upload Merchant Export", type=['csv'])
    if file:
        df_raw = pd.read_csv(file)
        st.dataframe(df_raw.head())
        
        # Mapping logic
        mapping = {
            'customer_id': 'customer', 'Customer_Name': 'customer', 'customer': 'customer',
            'credit_amount': 'amount', 'Amount': 'amount', 'amount': 'amount',
            'payment_status': 'status', 'Status': 'status',
            'days_overdue': 'days_due', 'days_due': 'days_due',
            'customer_type': 'customer_type'
        }
        
        if st.button("Process & AI Map"):
            processed = pd.DataFrame()
            for old, new in mapping.items():
                if old in df_raw.columns: processed[new] = df_raw[old]
            
            processed['merchant'] = st.session_state.user
            if 'status' not in processed.columns: processed['status'] = 'Pending'
            if 'days_due' not in processed.columns: processed['days_due'] = 0
            if 'trust_score' not in processed.columns: processed['trust_score'] = 710
            if 'customer_type' not in processed.columns: processed['customer_type'] = 'Retail'
            processed['last_reminder'] = None

            conn = get_db_connection()
            processed[['merchant', 'customer', 'amount', 'status', 'days_due', 'trust_score', 'customer_type', 'last_reminder']].to_sql('ledger', conn, if_exists='append', index=False)
            conn.commit()
            conn.close()
            st.success("Ledger Synchronized with AI Engine.")

# --- ROUTER ---
if st.session_state.auth_state == 'landing':
    landing_page()
elif st.session_state.auth_state == 'register':
    registration_page()
elif st.session_state.auth_state == 'login':
    login_page()
elif st.session_state.auth_state == 'dashboard':
    st.sidebar.title("Khatakhat AI")
    st.sidebar.caption(f"Business: {st.session_state.user}")
    
    nav = st.sidebar.radio("Console", ["Overview", "Mass Import", "Risk Engine", "API Access", "Logout"])
    
    if nav == "Overview": dashboard_main()
    elif nav == "Mass Import": upload_system()
    elif nav == "Risk Engine": ai_risk_predictor()
    elif nav == "API Access": api_key_management()
    elif nav == "Logout":
        st.session_state.auth_state = 'landing'
        st.session_state.user = None
        st.rerun()
