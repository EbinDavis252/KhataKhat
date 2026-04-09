import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import io

# --- CONFIGURATION & STYLING ---
st.set_page_config(page_title="Khatakhat AI | Smarter Credit", layout="wide", initial_sidebar_state="expanded")

# Custom CSS for Fintech Look
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
        background-color: #F5F7FA;
    }
    
    .main {
        background-color: #F5F7FA;
    }
    
    .stButton>button {
        background-color: #0F172A;
        color: white;
        border-radius: 8px;
        border: none;
        padding: 0.6rem 1.2rem;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    
    .stButton>button:hover {
        background-color: #2563EB;
        color: white;
        box-shadow: 0 4px 12px rgba(37, 99, 235, 0.2);
    }
    
    .metric-card {
        background-color: white;
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        border: 1px solid #E2E8F0;
    }
    
    .sidebar .sidebar-content {
        background-color: #FFFFFF;
    }

    h1, h2, h3 {
        color: #0F172A;
        font-weight: 700;
    }

    .landing-hero {
        padding: 100px 20px;
        text-align: center;
        background: linear-gradient(135deg, #F8FAFC 0%, #E2E8F0 100%);
        border-radius: 20px;
        margin-bottom: 40px;
    }
    
    .tagline {
        color: #2563EB;
        font-size: 1.2rem;
        font-weight: 600;
        letter-spacing: 1px;
        text-transform: uppercase;
    }
    
    .stAlert {
        border-radius: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- DATABASE SETUP ---
def init_db():
    conn = sqlite3.connect('khatakhat.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS ledger (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    customer TEXT,
                    amount REAL,
                    status TEXT,
                    days_due INTEGER,
                    trust_score INTEGER,
                    last_reminder_date TEXT
                )''')
    conn.commit()
    conn.close()

def load_data():
    conn = sqlite3.connect('khatakhat.db')
    df = pd.read_sql_query("SELECT * FROM ledger", conn)
    conn.close()
    return df

def save_to_db(df):
    conn = sqlite3.connect('khatakhat.db')
    df.to_sql('ledger', conn, if_exists='append', index=False)
    conn.commit()
    conn.close()

init_db()

# --- AUTHENTICATION ---
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False

def login():
    st.markdown("<div style='max-width: 400px; margin: 0 auto; padding: 50px 0;'>", unsafe_allow_html=True)
    st.title("Secure Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Sign In"):
        if username == "admin" and password == "khatakhat123":
            st.session_state['logged_in'] = True
            st.rerun()
        else:
            st.error("Invalid credentials")
    st.markdown("</div>", unsafe_allow_html=True)

# --- PAGES ---

def landing_page():
    st.markdown("""
        <div class="landing-hero">
            <p class="tagline">Smarter Credit. Faster Recovery.</p>
            <h1>Khatakhat AI</h1>
            <p style="font-size: 1.2rem; color: #475569; max-width: 700px; margin: 0 auto;">
                Khatakhat AI helps small businesses track credit transactions, predict payment risks, 
                and recover dues faster using intelligent analytics.
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.subheader("About")
        st.write("Khatakhat AI is a purpose-built receivables engine for the modern Indian merchant, digitizing the traditional 'Bahi Khata'.")
    with col2:
        st.subheader("Why Choose Us")
        st.write("Stop chasing payments manually. Let AI prioritize your collections based on customer behavior and risk profile.")
    with col3:
        st.subheader("Key Features")
        st.write("• Automated Ledgering\n• Smart Risk Scoring\n• One-tap Reminders\n• Multi-format Export")

    st.markdown("<br><br>", unsafe_allow_html=True)
    if st.button("Enter Dashboard →", use_container_width=True):
        st.session_state['page'] = 'login'
        st.rerun()

def dashboard_view():
    st.title("Business Insights")
    df = load_data()
    
    if df.empty:
        st.info("No data available. Please upload a ledger to get started.")
        return

    # Metrics
    total_outstanding = df[df['status'] != 'Paid']['amount'].sum()
    total_collected = df[df['status'] == 'Paid']['amount'].sum()
    recovery_rate = (total_collected / (total_outstanding + total_collected)) * 100 if (total_outstanding + total_collected) > 0 else 0
    avg_trust = df['trust_score'].mean()

    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.metric("Total Outstanding", f"₹{total_outstanding:,.0f}")
    with m2:
        st.metric("Total Collected", f"₹{total_collected:,.0f}")
    with m3:
        st.metric("Recovery Rate", f"{recovery_rate:.1f}%")
    with m4:
        st.metric("Avg. Trust Score", f"{avg_trust:.0f}")

    # Charts
    c1, c2 = st.columns(2)
    
    with c1:
        st.subheader("Receivables by Customer")
        pending_df = df[df['status'] != 'Paid'].groupby('customer')['amount'].sum().sort_values(ascending=False).head(10).reset_index()
        fig1 = px.bar(pending_df, x='amount', y='customer', orientation='h', 
                      color_discrete_sequence=['#2563EB'], template='plotly_white')
        st.plotly_chart(fig1, use_container_width=True)

    with c2:
        st.subheader("Payment Status Distribution")
        status_counts = df['status'].value_counts().reset_index()
        fig2 = px.pie(status_counts, values='count', names='status', 
                      color_discrete_sequence=['#0F172A', '#2563EB', '#94A3B8'], hole=0.4)
        st.plotly_chart(fig2, use_container_width=True)

    st.subheader("Risk Heatmap (Due vs Amount)")
    fig3 = px.density_heatmap(df, x="days_due", y="amount", nbinsx=20, nbinsy=20, color_continuous_scale='Viridis')
    st.plotly_chart(fig3, use_container_width=True)

def upload_ledger_view():
    st.title("Upload Ledger Data")
    uploaded_file = st.file_uploader("Choose a CSV file", type="csv")
    
    if uploaded_file is not None:
        try:
            raw_df = pd.read_csv(uploaded_file)
            st.write("Preview of Raw Data:", raw_df.head())
            
            # Standardization Logic
            mapping = {
                'customer_id': 'customer', 'Customer_Name': 'customer', 'Name': 'customer', 'customer': 'customer',
                'credit_amount': 'amount', 'Transaction_Amount': 'amount', 'amount': 'amount', 'Amount': 'amount',
                'payment_status': 'status', 'Payment_Status': 'status', 'status': 'status', 'Status': 'status',
                'days_overdue': 'days_due', 'days_due': 'days_due', 'Due_Days': 'days_due', 'Overdue': 'days_due'
            }
            
            new_df = pd.DataFrame()
            cols_found = 0
            for old_col, new_col in mapping.items():
                if old_col in raw_df.columns and new_col not in new_df.columns:
                    new_df[new_col] = raw_df[old_col]
                    cols_found += 1
            
            # Handle missing Trust Score (Derive for demo if not present)
            if 'trust_score' not in raw_df.columns:
                # Mock trust score logic: base 800 minus penalty for overdue
                new_df['trust_score'] = 800 - (new_df['days_due'] * 2)
                new_df['trust_score'] = new_df['trust_score'].clip(300, 900)
            else:
                new_df['trust_score'] = raw_df['trust_score']

            if cols_found >= 3:
                if st.button("Standardize & Save to DB"):
                    save_to_db(new_df)
                    st.success(f"Successfully processed {len(new_df)} records.")
            else:
                st.error("Could not find enough matching columns (Customer, Amount, Status). Please check column names.")
        
        except Exception as e:
            st.error(f"Error processing file: {e}")

def receivables_view():
    st.title("Receivables Management")
    df = load_data()
    if df.empty:
        st.warning("No data found.")
        return

    pending = df[df['status'] != 'Paid'].copy()
    
    # Filters
    col1, col2, col3 = st.columns(3)
    cust_filter = col1.multiselect("Filter Customer", options=pending['customer'].unique())
    amt_range = col2.slider("Amount Range", 0, int(pending['amount'].max() or 10000), (0, int(pending['amount'].max() or 10000)))
    due_range = col3.slider("Days Overdue", 0, int(pending['days_due'].max() or 365), (0, int(pending['days_due'].max() or 365)))

    filtered = pending[
        (pending['amount'] >= amt_range[0]) & (pending['amount'] <= amt_range[1]) &
        (pending['days_due'] >= due_range[0]) & (pending['days_due'] <= due_range[1])
    ]
    if cust_filter:
        filtered = filtered[filtered['customer'].isin(cust_filter)]

    def highlight_overdue(val):
        color = '#FEE2E2' if val > 30 else 'white'
        return f'background-color: {color}'

    st.dataframe(filtered.style.applymap(highlight_overdue, subset=['days_due']), use_container_width=True)

def risk_predictor_view():
    st.title("AI Risk Predictor")
    df = load_data()
    if df.empty: return

    # Logic: Risk Score = (900 - trust_score) + days_due
    df['risk_score'] = (900 - df['trust_score']) + df['days_due']
    
    def categorize(score):
        if score < 200: return "Low Risk"
        elif score < 500: return "Medium Risk"
        else: return "High Risk"

    df['risk_category'] = df['risk_score'].apply(categorize)

    fig = px.scatter(df, x="trust_score", y="days_due", size="amount", color="risk_category",
                     hover_name="customer", title="Customer Risk Matrix",
                     color_discrete_map={"Low Risk": "green", "Medium Risk": "orange", "High Risk": "red"})
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Risk Breakdown")
    st.table(df[['customer', 'trust_score', 'days_due', 'risk_score', 'risk_category']].sort_values('risk_score', ascending=False).head(10))

def reminder_engine_view():
    st.title("Smart Reminder Engine")
    df = load_data()
    pending = df[df['status'] != 'Paid']
    
    if pending.empty:
        st.info("Great! No pending payments found.")
        return

    customer_list = pending['customer'].unique()
    selected_cust = st.selectbox("Select Customer to Remind", customer_list)
    
    cust_data = pending[pending['customer'] == selected_cust].iloc[0]
    
    st.info(f"Customer: {selected_cust} | Due: ₹{cust_data['amount']} | Overdue: {cust_data['days_due']} days")
    
    msg_template = f"Hi {selected_cust}, a payment of ₹{cust_data['amount']} is pending for {cust_data['days_due']} days at Khatakhat Merchant. Please clear it soon. Pay here: https://pay.kh/123"
    st.text_area("Message Preview", value=msg_template, height=100)

    if st.button("Send Reminder via WhatsApp/SMS"):
        # Mock API Call
        import time
        with st.spinner("Connecting to Gateway..."):
            time.sleep(1)
            st.toast(f"Reminder Sent Successfully to {selected_cust}!", icon='✅')
            
            # Log it in DB (Update last reminder date)
            conn = sqlite3.connect('khatakhat.db')
            c = conn.cursor()
            c.execute("UPDATE ledger SET last_reminder_date = ? WHERE customer = ?", 
                      (datetime.now().strftime("%Y-%m-%d %H:%M"), selected_cust))
            conn.commit()
            conn.close()

def reports_view():
    st.title("Financial Reports")
    df = load_data()
    if df.empty: return

    c1, c2 = st.columns(2)
    
    with c1:
        st.subheader("Top Defaulters (By Amount)")
        defaulters = df[df['status'] != 'Paid'].groupby('customer')['amount'].sum().nlargest(5)
        st.bar_chart(defaulters)

    with c2:
        st.subheader("Top Payers (Trust Score)")
        top_payers = df.groupby('customer')['trust_score'].mean().nlargest(5)
        st.bar_chart(top_payers)

    st.subheader("Aging Summary")
    df['age_group'] = pd.cut(df['days_due'], bins=[0, 30, 60, 90, 1000], labels=['0-30', '31-60', '61-90', '90+'])
    aging = df[df['status'] != 'Paid'].groupby('age_group')['amount'].sum()
    st.table(aging)

def audit_export_view():
    st.title("Audit & Export")
    df = load_data()
    st.write("Export your full transaction ledger for accounting.")
    
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="Download Full Ledger CSV",
        data=csv,
        file_name=f"khatakhat_audit_{datetime.now().strftime('%Y%m%d')}.csv",
        mime='text/csv',
    )
    st.dataframe(df)

# --- MAIN APP LOGIC ---

if not st.session_state['logged_in']:
    if 'page' not in st.session_state:
        st.session_state['page'] = 'landing'
    
    if st.session_state['page'] == 'landing':
        landing_page()
    else:
        login()
else:
    # Navigation
    st.sidebar.title("Khatakhat AI")
    menu = ["Dashboard", "Upload Ledger", "Receivables", "Risk Predictor", "Reminder Engine", "Reports", "Audit Export", "Logout"]
    choice = st.sidebar.radio("Navigation", menu)

    if choice == "Dashboard":
        dashboard_view()
    elif choice == "Upload Ledger":
        upload_ledger_view()
    elif choice == "Receivables":
        receivables_view()
    elif choice == "Risk Predictor":
        risk_predictor_view()
    elif choice == "Reminder Engine":
        reminder_engine_view()
    elif choice == "Reports":
        reports_view()
    elif choice == "Audit Export":
        audit_export_view()
    elif choice == "Logout":
        st.session_state['logged_in'] = False
        st.session_state['page'] = 'landing'
        st.rerun()

    st.sidebar.markdown("---")
    st.sidebar.caption("v1.0.4 Premium • KD Enterprise")
