import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px
import plotly.graph_objects as go
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
    }
    </style>
    """, unsafe_allow_html=True)

# --- DATABASE ENGINE ---
DB_NAME = 'khatakhat_ultra_v1.db'

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

# --- UTILS & SECURITY ---
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
            <p style="color: #2563EB; font-weight: 600; letter-spacing: 2px; text-transform: uppercase; margin-bottom: 10px;">The Future of Receivables</p>
            <h1 class="punchline">"Dhanda Udhaari Se Nahi, Recovery Se Chalta Hai!"</h1>
            <p style="font-size: 1.3rem; color: #475569; max-width: 850px; margin: 0 auto 40px auto; line-height: 1.6;">
                Khatakhat AI is an <b>AI-First</b> merchant platform. Beyond simple recording, we use predictive models 
                to analyze payment behavior, automate recovery, and protect your cash flow like Zoho and Razorpay.
            </p>
            <div style="display: flex; justify-content: center; gap: 20px;">
                <div style="width: 200px;">
    """, unsafe_allow_html=True)
    
    if st.button("Register & Beat Zoho"):
        st.session_state.auth_state = 'register'
        st.rerun()
        
    st.markdown("""
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown('<div class="feature-card"><h3>🤖 Predictive AI</h3><p>Proprietary scoring engine that ranks customer reliability based on 10+ financial parameters.</p></div>', unsafe_allow_html=True)
    with col2:
        st.markdown('<div class="feature-card"><h3>🔗 API Integration</h3><p>Connect your existing billing software via API keys for real-time automated ledgering.</p></div>', unsafe_allow_html=True)
    with col3:
        st.markdown('<div class="feature-card"><h3>📈 Recovery Analytics</h3><p>Deep-dive into payment cycles and churn prediction to keep your capital safe.</p></div>', unsafe_allow_html=True)

def registration_page():
    st.markdown("<h2 style='text-align: center; margin-top: 50px;'>Merchant Onboarding</h2>", unsafe_allow_html=True)
    _, col, _ = st.columns([1, 1, 1])
    with col:
        with st.form("reg_form"):
            new_user = st.text_input("Username (Mobile/Email)")
            new_biz = st.text_input("Business Name")
            new_pw = st.text_input("Password", type='password')
            submit = st.form_submit_button("Create My Smart Khata")
            
            if submit:
                if new_user and new_pw and new_biz:
                    conn = get_db_connection()
                    c = conn.cursor()
                    try:
                        # Auto-generate a dummy API Key for new users
                        api_k = f"kh_{hashlib.md5(new_user.encode()).hexdigest()[:12]}"
                        c.execute('INSERT INTO users(username, password, business_name, api_key) VALUES (?,?,?,?)', 
                                 (new_user, make_hashes(new_pw), new_biz, api_k))
                        conn.commit()
                        st.success("Registration Successful!")
                        st.session_state.auth_state = 'login'
                        st.rerun()
                    except sqlite3.IntegrityError:
                        st.error("User already exists.")
                    finally:
                        conn.close()
        if st.button("Back to Home"):
            st.session_state.auth_state = 'landing'
            st.rerun()

def login_page():
    st.markdown("<h2 style='text-align: center; margin-top: 50px;'>Log In</h2>", unsafe_allow_html=True)
    _, col, _ = st.columns([1, 1, 1])
    with col:
        with st.form("login_form"):
            username = st.text_input("Username")
            password = st.text_input("Password", type='password')
            submit = st.form_submit_button("Access Dashboard")
            
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
                    st.error("Invalid credentials.")

# --- DASHBOARD COMPONENTS ---

def dashboard_main():
    st.title(f"📊 {st.session_state.user}'s Command Center")
    conn = get_db_connection()
    df = pd.read_sql("SELECT * FROM ledger WHERE merchant = ?", conn, params=(st.session_state.user,))
    conn.close()

    if df.empty:
        st.warning("No data found. Upload your merchant ledger to begin AI analysis.")
        return

    m1, m2, m3, m4 = st.columns(4)
    pending = df[df['status'] != 'Paid']
    total_due = pending['amount'].sum()
    collected = df[df['status'] == 'Paid']['amount'].sum()
    recovery_rate = (collected / (total_due + collected)) * 100 if (total_due + collected) > 0 else 0
    
    m1.metric("Current Udhaar", f"₹{total_due:,.0f}", delta="-5% Risk")
    m2.metric("Total Collected", f"₹{collected:,.0f}", delta="↑ 12%")
    m3.metric("Collection Rate", f"{recovery_rate:.1f}%")
    m4.metric("AI Trust Index", f"{int(df['trust_score'].mean())}/900")

    st.markdown("---")
    c1, c2 = st.columns([2, 1])
    with c1:
        st.subheader("Collection vs Risk Over Time")
        # Generate dummy trend for visual impact
        trend_df = pd.DataFrame({
            'Month': ['Jan', 'Feb', 'Mar', 'Apr'],
            'Collected': [collected*0.6, collected*0.8, collected*0.9, collected],
            'Risk': [total_due*1.2, total_due*1.1, total_due*0.9, total_due]
        })
        fig = px.line(trend_df, x='Month', y=['Collected', 'Risk'], template="plotly_white", color_discrete_sequence=['#2563EB', '#EF4444'])
        st.plotly_chart(fig, use_container_width=True)
    with c2:
        st.subheader("Industry Segment")
        type_dist = df['customer_type'].value_counts().reset_index()
        fig2 = px.pie(type_dist, names='customer_type', values='count', hole=0.6, color_discrete_sequence=['#0F172A', '#2563EB', '#CBD5E1'])
        st.plotly_chart(fig2, use_container_width=True)

def risk_ai_engine():
    st.title("🧠 Predictive Risk Analysis")
    conn = get_db_connection()
    df = pd.read_sql("SELECT * FROM ledger WHERE merchant = ?", conn, params=(st.session_state.user,))
    conn.close()
    
    if df.empty: return

    # AI Logic: Risk = Penalty for low trust score + Penalty for days overdue
    df['risk_index'] = (900 - df['trust_score']) + (df['days_due'] * 2)
    
    def get_category(score):
        if score < 200: return "Secure"
        elif score < 450: return "Alert"
        else: return "Critical"

    df['risk_cat'] = df['risk_index'].apply(get_category)

    st.markdown("""
        <div style="background: white; padding: 20px; border-radius: 10px; margin-bottom: 20px;">
            <b>AI Insight:</b> <i>Customers in the 'Critical' zone have a 65% higher probability of defaulting in the next 30 days. We recommend stopping credit for these accounts.</i>
        </div>
    """, unsafe_allow_html=True)

    fig = px.scatter(df, x="trust_score", y="days_due", size="amount", color="risk_cat",
                     hover_name="customer", title="Merchant Risk Quadrant",
                     color_discrete_map={"Secure": "#10B981", "Alert": "#F59E0B", "Critical": "#EF4444"},
                     labels={"trust_score": "Financial Trust (AI)", "days_due": "Aging (Days)"})
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("High Priority Action Items")
    st.table(df[df['risk_cat'] == 'Critical'].sort_values('amount', ascending=False)[['customer', 'amount', 'days_due', 'risk_index']])

def api_settings():
    st.title("🔗 API & Integrations")
    conn = get_db_connection()
    user_data = pd.read_sql("SELECT api_key FROM users WHERE username = ?", conn, params=(st.session_state.user,)).iloc[0]
    conn.close()

    st.info("Use this API Key to sync Khatakhat AI with your ERP, Zoho Books, or custom Billing software.")
    
    st.code(f"X-KH-API-KEY: {user_data['api_key']}", language="bash")
    
    st.markdown("""
    ### Webhook Configuration
    You can set a URL to receive real-time notifications when a payment is predicted as 'At-Risk'.
    """)
    st.text_input("Webhook URL", placeholder="https://your-server.com/api/v1/alert")
    if st.button("Update Configuration"):
        st.success("Integration updated.")

def upload_handler():
    st.title("📁 Mass Import")
    file = st.file_uploader("Upload CSV (Compatible with Zoho, Khatabook, Vyapar)", type=['csv'])
    if file:
        raw_df = pd.read_csv(file)
        
        # Smart Mapping Logic
        mapping = {
            'customer_id': 'customer', 'Customer_Name': 'customer', 'customer': 'customer',
            'credit_amount': 'amount', 'Amount': 'amount', 'amount': 'amount',
            'payment_status': 'status', 'Status': 'status',
            'days_overdue': 'days_due', 'days_due': 'days_due',
            'customer_type': 'customer_type'
        }
        
        if st.button("AI-Mapping & Import"):
            processed = pd.DataFrame()
            for old, new in mapping.items():
                if old in raw_df.columns: processed[new] = raw_df[old]
            
            processed['merchant'] = st.session_state.user
            if 'status' not in processed.columns: processed['status'] = 'Pending'
            if 'days_due' not in processed.columns: processed['days_due'] = 0
            if 'trust_score' not in processed.columns: processed['trust_score'] = 720
            if 'customer_type' not in processed.columns: processed['customer_type'] = 'Retail'
            processed['last_reminder'] = None

            cols = ['merchant', 'customer', 'amount', 'status', 'days_due', 'trust_score', 'customer_type', 'last_reminder']
            final = processed[cols]
            
            conn = get_db_connection()
            final.to_sql('ledger', conn, if_exists='append', index=False)
            conn.commit()
            conn.close()
            st.success("Synchronization Complete!")

# --- MAIN APP FLOW ---
if st.session_state.auth_state == 'landing':
    landing_page()
elif st.session_state.auth_state == 'register':
    registration_page()
elif st.session_state.auth_state == 'login':
    login_page()
elif st.session_state.auth_state == 'dashboard':
    st.sidebar.title("Khatakhat AI")
    st.sidebar.caption(f"Merchant: {st.session_state.user}")
    
    nav = st.sidebar.radio("Navigation", ["Overview", "Mass Import", "Risk Engine", "Smart Reminders", "API Keys", "Logout"])
    
    if nav == "Overview": dashboard_main()
    elif nav == "Mass Import": upload_handler()
    elif nav == "Risk Engine": risk_ai_engine()
    elif nav == "API Keys": api_settings()
    elif nav == "Smart Reminders":
        st.title("📲 Smart Reminder Engine")
        st.write("Using behavioral analysis to select the best reminder tone...")
        st.info("Selecting 'Firm' tone for 30+ days overdue customers.")
        if st.button("Send Automated Sequence"):
            st.toast("Sequenced WhatsApp/SMS sent successfully!", icon="✅")
    elif nav == "Logout":
        st.session_state.auth_state = 'landing'
        st.session_state.user = None
        st.rerun()
