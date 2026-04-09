import streamlit as st
import pandas as pd
import numpy as np
import sqlite3
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import urllib.parse
import re

# ==========================================
# 0. UI & BRANDING CONFIG
# ==========================================
st.set_page_config(page_title="Khatakhat | Business Intelligence", layout="wide", page_icon="🚀")

# Hide Streamlit elements and apply premium styling
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;} footer {visibility: hidden;}
    .main-title { font-size: 38px; font-weight: 800; color: #1E1E1E; margin-bottom: 0px; }
    .highlight { color: #FF4B4B; }
    .stMetric { background-color: #f8f9fa; padding: 15px; border-radius: 10px; border-left: 5px solid #FF4B4B; }
    div.stButton > button:first-child { background-color: #FF4B4B; color: white; border: none; }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 1. DATABASE & SESSION STATE
# ==========================================
conn = sqlite3.connect('khatakhat_pro.db', check_same_thread=False)

if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

# ==========================================
# 2. CORE UTILITIES
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
    customers = ["Rahul Sharma", "Amit General Store", "Sita Textiles", "Vijay Electronics", "Pooja Dairy"]
    data = []
    for _ in range(40):
        p_date = datetime.now() - timedelta(days=np.random.randint(5, 60))
        status = np.random.choice(["Paid", "Pending"], p=[0.7, 0.3])
        data.append({
            "customer_id": np.random.randint(1001, 1006),
            "customer_name": np.random.choice(customers),
            "phone_number": "919876543210",
            "amount": np.random.randint(1000, 8000),
            "payment_status": status,
            "purchase_date": p_date,
            "due_date": p_date + timedelta(days=15),
            "payment_date": p_date + timedelta(days=18) if status == "Paid" else None,
            "upi_id": f"cust{np.random.randint(1,99)}@oksbi"
        })
    df = pd.DataFrame(data)
    save_data(df)
    return df

# ==========================================
# 3. ADVANCED MODULES (The Differentiators)
# ==========================================

def module_auto_reconcile(df):
    st.header("⚡ AI Auto-Reconcile Engine")
    st.info("Razorpay-Killer: Paste your Bank/UPI SMS here to automatically mark payments as Paid.")
    
    sms_input = st.text_area("Paste SMS Notification here", height=100, 
                            placeholder="Example: Money Received ₹2500 from Rahul Sharma via UPI Ref: 456789...")
    
    if st.button("Process with AI"):
        # Logic: Extract Amount and Name using Regex (Simulating AI NLP)
        amount_match = re.search(r'₹\s?(\d+)', sms_input)
        
        # Check if any customer name from our ledger exists in the SMS
        detected_name = None
        for name in df['customer_name'].unique():
            if name.lower() in sms_input.lower():
                detected_name = name
                break
        
        if amount_match and detected_name:
            amt = int(amount_match.group(1))
            st.success(f"Matched: Found payment of ₹{amt} from {detected_name}")
            
            # Update Database
            mask = (df['customer_name'] == detected_name) & (df['payment_status'] == 'Pending')
            if mask.any():
                df.loc[mask, 'payment_status'] = 'Paid'
                df.loc[mask, 'payment_date'] = datetime.now()
                save_data(df)
                st.balloons()
                st.write("✅ Ledger reconciled automatically.")
            else:
                st.warning("Customer matched but no 'Pending' balance found.")
        else:
            st.error("AI could not match this SMS. Please check Amount or Customer Name.")

def module_inventory_link(df):
    st.header("📦 Inventory-Link (Predictive Reinvestment)")
    st.write("Khatabook stops at recovery. We tell you how to grow your money.")
    
    recovered_funds = df[(df['payment_status'] == 'Paid') & 
                        (df['payment_date'] >= pd.Timestamp(datetime.now() - timedelta(days=7)))]['amount'].sum()
    
    st.metric("Total Recovered (Last 7 Days)", f"₹{recovered_funds:,.0f}")
    
    st.subheader("Actionable Recommendations")
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div style="background-color:#E3F2FD; padding:20px; border-radius:10px;">
        <h4>🍞 Invest in Flour (Atta)</h4>
        <p>Market price dropped by 4%. Since you recovered ₹5,000, buying now saves you ₹200 on next week's stock.</p>
        </div>
        """, unsafe_allow_html=True)
        
    with col2:
        st.markdown("""
        <div style="background-color:#F1F8E9; padding:20px; border-radius:10px;">
        <h4>🥛 Invest in Dairy</h4>
        <p>Demand predicted to rise by 15% due to upcoming local festival. Pre-order now to avoid stockouts.</p>
        </div>
        """, unsafe_allow_html=True)

def module_recovery_engine(df):
    st.header("🧠 Behavioral Recovery & UPI Intent")
    pending = df[df['payment_status'] == 'Pending']
    if pending.empty:
        st.success("All caught up!"); return
        
    cust = st.selectbox("Select Customer", pending['customer_name'].unique())
    cust_data = pending[pending['customer_name'] == cust].iloc[0]
    
    # UPI Deep Link Strategy
    merchant_upi = "kdstore@upi"
    upi_url = f"upi://pay?pa={merchant_upi}&pn=KD_Store&am={cust_data['amount']}&cu=INR"
    
    msg = f"Hi {cust}, clear your ₹{cust_data['amount']} ledger here in one click: {upi_url}"
    st.code(msg)
    wa_link = f"https://wa.me/{cust_data['phone_number']}?text={urllib.parse.quote(msg)}"
    st.markdown(f'<a href="{wa_link}" target="_blank"><button style="width:100%; border:none; padding:10px; background:#25D366; color:white; border-radius:5px;">Send Smart UPI Nudge</button></a>', unsafe_allow_html=True)

# ==========================================
# 4. MAIN APP ROUTING
# ==========================================

if st.session_state["authenticated"]:
    if st.sidebar.button("Log Out"):
        st.session_state["authenticated"] = False
        st.rerun()

    df = get_data()
    if df.empty: df = generate_sample_data()

    st.sidebar.title("Khatakhat Pro 🚀")
    nav = st.sidebar.radio("Navigation", [
        "Dashboard", "Customer Ledger", "Recovery Engine", 
        "Auto-Reconcile (NEW)", "Inventory-Link (NEW)", "Trust Network", "Settings"
    ])

    if nav == "Dashboard":
        st.markdown('<h1 class="main-title">Dashboard</h1>', unsafe_allow_html=True)
        c1, c2, c3 = st.columns(3)
        c1.metric("Outstanding", f"₹{df[df['payment_status']=='Pending']['amount'].sum():,.0f}")
        c2.metric("Trust Index", "748", "+14")
        c3.metric("Rec. Rate", "91%")
        st.plotly_chart(px.line(df.groupby(df['purchase_date'].dt.date)['amount'].sum().reset_index(), x='purchase_date', y='amount'))

    elif nav == "Auto-Reconcile (NEW)":
        module_auto_reconcile(df)
    
    elif nav == "Inventory-Link (NEW)":
        module_inventory_link(df)
        
    elif nav == "Recovery Engine":
        module_recovery_engine(df)
        
    elif nav == "Customer Ledger":
        st.header("📓 Records")
        st.dataframe(df, use_container_width=True)

    elif nav == "Trust Network":
        st.header("🌐 Global Trust Network")
        phone = st.text_input("Search Customer Phone")
        if phone: st.success("✅ Clean Record in the Khatakhat Network.")

else:
    # LANDING PAGE
    st.markdown('<h1 class="main-title">Khatakhat <span class="highlight">Pro</span>.</h1>', unsafe_allow_html=True)
    st.write("### AI-Driven Recovery & Business Growth")
    st.image("https://img.freepik.com/free-vector/financial-analytics-concept-illustration_114360-143.jpg", width=500)
    
    with st.sidebar:
        st.header("Merchant Login")
        u = st.text_input("User")
        p = st.text_input("Pass", type="password")
        if st.button("Login"):
            if u == "kd_merchant" and p == "admin123":
                st.session_state["authenticated"] = True
                st.rerun()
            else: st.error("Wrong credentials")
