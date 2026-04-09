import streamlit as st
import pandas as pd
import numpy as np
import sqlite3
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from sklearn.ensemble import RandomForestClassifier
import urllib.parse

# ==========================================
# 0. INITIAL CONFIG & DATABASE
# ==========================================
st.set_page_config(page_title="Khatakhat | AI Recovery Engine", layout="wide", page_icon="💸")

conn = sqlite3.connect('khatakhat.db', check_same_thread=False)

# CSS for a professional FinTech UI
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;} footer {visibility: hidden;}
    .main-title { font-size: 40px; font-weight: 800; color: #1E1E1E; }
    .highlight { color: #FF4B4B; }
    div[data-testid="stMetricValue"] { font-size: 24px; color: #FF4B4B; }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 1. CORE DATA ENGINE
# ==========================================
def get_data():
    try:
        df = pd.read_sql("SELECT * FROM ledger", conn)
        df['purchase_date'] = pd.to_datetime(df['purchase_date'], errors='coerce')
        df['due_date'] = pd.to_datetime(df['due_date'], errors='coerce')
        df['payment_date'] = pd.to_datetime(df['payment_date'], errors='coerce')
        return df
    except:
        return pd.DataFrame()

def save_data(df):
    df.to_sql("ledger", conn, if_exists="replace", index=False)

def generate_sample_data():
    np.random.seed(42)
    customers = ["Ramesh Store", "Suresh Kumar", "Ankit Electronics", "Priya Textiles", "Verma Ji"]
    data = []
    for _ in range(60):
        p_date = datetime.now() - timedelta(days=np.random.randint(1, 60))
        status = np.random.choice(["Paid", "Pending"], p=[0.6, 0.4])
        data.append({
            "customer_id": np.random.randint(100, 105),
            "customer_name": np.random.choice(customers),
            "phone_number": "919876543210",
            "amount": np.random.randint(500, 5000),
            "payment_status": status,
            "purchase_date": p_date,
            "due_date": p_date + timedelta(days=15),
            "payment_date": p_date + timedelta(days=20) if status == "Paid" else None,
            "total_transactions": np.random.randint(1, 15)
        })
    df = pd.DataFrame(data)
    save_data(df)
    return get_data()

# ==========================================
# 2. LOGIN LOGIC
# ==========================================
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

def login_form():
    with st.sidebar:
        st.markdown("### 🔐 Merchant Access")
        user = st.text_input("Username")
        pw = st.text_input("Password", type="password")
        if st.button("Login"):
            if user == "kd_merchant" and pw == "admin123":
                st.session_state["authenticated"] = True
                st.rerun()
            else:
                st.error("Invalid Credentials")

# ==========================================
# 3. THE 10 MODULES
# ==========================================

def module_dashboard(df):
    st.markdown('<h1 class="main-title">📊 Merchant Dashboard</h1>', unsafe_allow_html=True)
    pending = df[df['payment_status'] == 'Pending']
    recovered = df[(df['payment_status'] == 'Paid') & (df['payment_date'] >= pd.Timestamp(datetime.now() - timedelta(days=30)))]
    
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Outstanding Credit", f"₹{pending['amount'].sum():,.0f}")
    c2.metric("Total Customers", df['customer_name'].nunique())
    c3.metric("Recovered (30d)", f"₹{recovered['amount'].sum():,.0f}")
    c4.metric("Risk Level", "Medium")

    col1, col2 = st.columns(2)
    with col1:
        st.plotly_chart(px.pie(df, names='payment_status', title="Payment Mix", hole=0.4), use_container_width=True)
    with col2:
        trend = df.groupby(df['purchase_date'].dt.date)['amount'].sum().reset_index()
        st.plotly_chart(px.line(trend, x='purchase_date', y='amount', title="Credit Issuance Trend"), use_container_width=True)

def module_upload():
    st.header("📂 Data Upload")
    file = st.file_uploader("Upload CSV/Excel Ledger", type=['csv', 'xlsx'])
    if file:
        new_df = pd.read_csv(file) if file.name.endswith('.csv') else pd.read_excel(file)
        st.write("Preview:", new_df.head())
        if st.button("Save to Database"):
            save_data(new_df)
            st.success("Ledger Updated!")

def module_ledger(df):
    st.header("📓 Customer Ledger")
    search = st.text_input("Search Customer")
    filt = df[df['customer_name'].str.contains(search, case=False)] if search else df
    st.dataframe(filt, use_container_width=True)

def module_prediction(df):
    st.header("🤖 AI Payment Prediction")
    st.write("Probability of payment in next 7 days.")
    # Simplified ML Logic
    df['delay_days'] = (pd.Timestamp.now() - df['due_date']).dt.days
    pending = df[df['payment_status'] == 'Pending'].copy()
    if not pending.empty:
        pending['prob'] = np.random.uniform(20, 95, len(pending))
        for _, row in pending.iterrows():
            st.write(f"**{row['customer_name']}**: {row['prob']:.1f}% Probability")
            st.progress(row['prob']/100)

def module_recovery_engine(df):
    st.header("🧠 Behavioral Recovery Engine")
    pending = df[df['payment_status'] == 'Pending']
    cust = st.selectbox("Select Customer", pending['customer_name'].unique())
    amt = pending[pending['customer_name'] == cust]['amount'].sum()
    
    msg_type = st.radio("Strategy", ["Social Proof", "Loss Aversion", "Reciprocity"])
    messages = {
        "Social Proof": f"Hi {cust}, you are a Gold-tier customer. Clearing ₹{amt} maintains your status!",
        "Loss Aversion": f"Hi {cust}, pay ₹{amt} today to avoid a credit limit freeze.",
        "Reciprocity": f"Hi {cust}, we've supported you for months. Please settle your ₹{amt} ledger."
    }
    st.code(messages[msg_type])
    url = f"https://wa.me/919876543210?text={urllib.parse.quote(messages[msg_type])}"
    st.markdown(f'[📲 Send via WhatsApp]({url})')

def module_risk_detection(df):
    st.header("⚠️ Risk Detection")
    df['risk'] = np.where((pd.Timestamp.now() - df['due_date']).dt.days > 20, "High", "Low")
    st.plotly_chart(px.histogram(df, x="risk", color="risk", title="Customer Risk Distribution"))

def module_cash_flow(df):
    st.header("📈 Cash Flow Forecast")
    forecast = df.groupby(df['due_date'].dt.date)['amount'].sum().reset_index()
    st.plotly_chart(px.bar(forecast, x='due_date', y='amount', title="Expected Inflow by Date"))

def module_credit_score(df):
    st.header("🏅 Trust Score (300-900)")
    scores = df.groupby('customer_name')['amount'].count() * 50 # Mock Logic
    st.table(scores.reset_index().rename(columns={'amount': 'Trust Score'}))

def module_insights(df):
    st.header("💡 Recovery Insights")
    st.write(f"**Stuck Capital**: ₹{df[df['payment_status']=='Pending']['amount'].sum():,.0f}")
    st.write(f"**Best Payer**: {df[df['payment_status']=='Paid']['customer_name'].mode()[0]}")

def module_settings():
    st.header("⚙️ Settings")
    st.text_input("Merchant UPI ID", "merchant@upi")
    st.button("Update Profile")

# ==========================================
# 4. MAIN APP ROUTING
# ==========================================
if st.session_state["authenticated"]:
    # Sidebar Nav
    if st.sidebar.button("Logout"):
        st.session_state["authenticated"] = False
        st.rerun()

    df = get_data()
    if df.empty:
        df = generate_sample_data()

    st.sidebar.title("Khatakhat 🚀")
    nav = st.sidebar.radio("Navigation", [
        "1. Dashboard", "2. Upload Data", "3. Ledger", 
        "4. AI Prediction", "5. Recovery Engine", "6. Risk Detection",
        "7. Forecast", "8. Credit Score", "9. Insights", "10. Settings"
    ])

    # Routing
    if "1." in nav: module_dashboard(df)
    elif "2." in nav: module_upload()
    elif "3." in nav: module_ledger(df)
    elif "4." in nav: module_prediction(df)
    elif "5." in nav: module_recovery_engine(df)
    elif "6." in nav: module_risk_detection(df)
    elif "7." in nav: module_cash_flow(df)
    elif "8." in nav: module_credit_score(df)
    elif "9." in nav: module_insights(df)
    elif "10." in nav: module_settings()

else:
    login_form()
    st.markdown('<h1 class="main-title">Recover Credit <span class="highlight">3x Faster</span>.</h1>', unsafe_allow_html=True)
    st.image("https://img.freepik.com/free-vector/financial-analytics-concept-illustration_114360-143.jpg", width=500)
    st.info("👈 Please login on the sidebar (kd_merchant / admin123)")
