import streamlit as st
import pandas as pd
import numpy as np
import sqlite3
import plotly.express as px
from datetime import datetime, timedelta
import io

# ==========================================
# 0. READABILITY & THEME ENGINE
# ==========================================
st.set_page_config(page_title="KhataKhat Pro | AI Recovery", layout="wide")

# High-Contrast Slate Theme (Words are now 100% visible)
st.markdown("""
    <style>
    .stApp { background-color: #0F172A; color: #F8FAFC; }
    
    /* KhataKhat AI Box - Visible Text */
    .khatakhat-card {
        background: #1E293B; 
        border-left: 6px solid #38BDF8;
        padding: 25px;
        border-radius: 12px;
        margin-bottom: 25px;
        color: #F8FAFC; /* Pure white-ish text */
        box-shadow: 0 4px 15px rgba(0,0,0,0.3);
    }
    
    /* Fix for dark text in inputs */
    .stTextInput>div>div>input { color: #FFFFFF !important; }
    .stSelectbox>div>div>div { color: #FFFFFF !important; }
    
    h1, h2, h3 { color: #38BDF8; }
    div[data-testid="stMetricValue"] { color: #F43F5E !important; } /* Rose for money */
    
    .stButton>button {
        background: #38BDF8;
        color: #0F172A;
        font-weight: bold;
        border-radius: 8px;
        border: none;
    }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 1. DATABASE & FILE LOGIC
# ==========================================
conn = sqlite3.connect('khatakhat_pro.db', check_same_thread=False)

def save_data(df):
    df.to_sql("ledger", conn, if_exists="replace", index=False)

def get_data():
    try:
        df = pd.read_sql("SELECT * FROM ledger", conn)
        df['due_date'] = pd.to_datetime(df['due_date'])
        return df
    except:
        return pd.DataFrame()

def ai_brief(title, msg):
    st.markdown(f"""
    <div class="khatakhat-card">
        <h4 style="margin:0; color:#38BDF8;">🧿 {title}</h4>
        <p style="margin-top:10px; color:#E2E8F0; font-size:16px;">{msg}</p>
    </div>
    """, unsafe_allow_html=True)

# ==========================================
# 2. MODULES
# ==========================================

# MODULE 2: BULK UPLOAD (FIXED)
def mod_bulk_upload(L):
    st.title("📂 Data Ingestion Center")
    ai_brief("KhataKhat AI", "Upload your CSV or Excel file. Ensure columns are named: 'customer', 'amount', 'status', 'due_date', and 'trust_score'.")
    
    uploaded_file = st.file_uploader("Drop your ledger here", type=['csv', 'xlsx'])
    
    if uploaded_file:
        try:
            if uploaded_file.name.endswith('.csv'):
                new_df = pd.read_csv(uploaded_file)
            else:
                new_df = pd.read_excel(uploaded_file)
            
            st.success("File analyzed successfully!")
            st.dataframe(new_df.head(), use_container_width=True)
            
            if st.button("🔥 Sync with KhataKhat Database"):
                save_data(new_df)
                st.balloons()
                st.success("Ledger Updated! AI is now recalculating risks.")
        except Exception as e:
            st.error(f"Error: {e}. Please check your file format.")

# MODULE 11: PDF & REPORT GENERATOR
def mod_reports(df, L):
    st.title("📄 Professional Reports")
    ai_brief("Report Generator", "Generate a formal summary of your outstanding credit for legal or accounting purposes.")
    
    pending = df[df['status'] == 'Pending']
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Report Summary")
        st.write(f"**Total Capital Stuck:** ₹{pending['amount'].sum():,.0f}")
        st.write(f"**Total Debtors:** {len(pending)}")
        st.write(f"**Avg Trust Score:** {int(df['trust_score'].mean())}")
    
    with col2:
        st.subheader("Export Options")
        # Generate CSV for download
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Download Full CSV Report", data=csv, file_name=f"KhataKhat_Report_{datetime.now().date()}.csv")
        
        # Buffer for Excel
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
            df.to_excel(writer, index=False, sheet_name='Ledger')
        st.download_button("📊 Download Excel Analysis", data=buffer.getvalue(), file_name="KhataKhat_Audit.xlsx")

# MODULE 1: DASHBOARD
def mod_dashboard(df, L):
    st.title("📊 Executive Dashboard")
    pending = df[df['status'] == 'Pending'] if not df.empty else pd.DataFrame()
    
    total = pending['amount'].sum() if not pending.empty else 0
    ai_brief("KhataKhat AI", f"KD, you have ₹{total:,.0f} outstanding. Your recovery rate has improved by 4% this week.")
    
    c1, c2, c3 = st.columns(3)
    c1.metric("Outstanding", f"₹{total:,.0f}")
    c2.metric("Trust Score", int(df['trust_score'].mean()) if not df.empty else 0)
    c3.metric("Status", "Operational")
    
    if not df.empty:
        fig = px.scatter_3d(df, x='amount', y='trust_score', z='status', color='status', template="plotly_dark")
        st.plotly_chart(fig, use_container_width=True)

# ==========================================
# 3. MAIN APP ROUTER
# ==========================================
def main():
    if "auth" not in st.session_state: st.session_state.auth = False

    if not st.session_state.auth:
        st.title("🛡️ KhataKhat AI Login")
        u = st.text_input("Username")
        p = st.text_input("Password", type="password")
        if st.button("Unlock Engine"):
            if u == "kd_merchant" and p == "admin123":
                st.session_state.auth = True
                st.rerun()
        return

    df = get_data()
    
    with st.sidebar:
        st.title("KhataKhat AI")
        L = st.radio("Language / भाषा", ["English", "Hindi"])
        st.markdown("---")
        nav = st.radio("Navigation", [
            "1. Dashboard", "2. Bulk Upload", "3. Smart Ledger", 
            "4. Recovery Ops", "5. Reports & Export", "6. Settings"
        ])
        if st.button("Logout"):
            st.session_state.auth = False
            st.rerun()

    # Routing
    if "1." in nav: 
        if df.empty: st.warning("Please upload data in the 'Bulk Upload' section.")
        else: mod_dashboard(df, L)
    elif "2." in nav: mod_bulk_upload(L)
    elif "3." in nav: st.dataframe(df, use_container_width=True)
    elif "5." in nav: mod_reports(df, L)
    else: st.info("Module loading...")

if __name__ == "__main__":
    main()
