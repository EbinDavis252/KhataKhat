import streamlit as st
import pandas as pd
import numpy as np
import sqlite3
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import time

# ==========================================
# 0. CORE ARCHITECTURE & INDUSTRIAL THEME
# ==========================================
st.set_page_config(page_title="KhataKhat AI | Enterprise", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Roboto+Mono:wght@400;700&family=Inter:wght@400;700&display=swap');
    
    .stApp { background-color: #0B0E14; color: #CFD8DC; font-family: 'Inter', sans-serif; }
    
    /* Intelligence Advisory Box */
    .ai-advisory {
        background: #151921;
        border-top: 1px solid #1DE9B6;
        border-bottom: 1px solid #1DE9B6;
        padding: 25px;
        margin-bottom: 30px;
    }
    
    .ai-tag { color: #1DE9B6; font-family: 'Roboto Mono', monospace; font-size: 11px; font-weight: bold; letter-spacing: 2px; }
    
    h1, h2, h3 { font-family: 'Roboto Mono', monospace; color: #FFFFFF; font-weight: 700; letter-spacing: -1px; }
    
    /* Data Presentation */
    div[data-testid="stMetricValue"] { color: #FFFFFF !important; font-family: 'Roboto Mono'; font-size: 32px !important; }
    
    /* Sharp Industrial Buttons */
    .stButton>button {
        background: transparent;
        color: #1DE9B6;
        border: 1px solid #1DE9B6;
        border-radius: 0px;
        font-family: 'Roboto Mono';
        transition: 0.3s;
        height: 3.2em;
        width: 100%;
        text-transform: uppercase;
    }
    .stButton>button:hover { background: #1DE9B6; color: #000000; box-shadow: 0 0 15px #1DE9B6; }
    
    .stDataFrame { border: 1px solid #263238; }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 1. SMART API GATEWAY (COMMUNICATION LAYER)
# ==========================================
class KhataKhatAPI:
    @staticmethod
    def trigger_nudge(customer, amount):
        """Simulates an asynchronous REST API call to a messaging gateway."""
        # Simulated Latency
        time.sleep(0.5)
        return {
            "status": "SUCCESS",
            "provider": "TWILIO_WA_PRO",
            "trace_id": f"KK-{np.random.randint(1000, 9999)}-X",
            "timestamp": datetime.now().strftime("%H:%M:%S")
        }

# ==========================================
# 2. DATABASE & SAFETY-WRAPPED LOGIC
# ==========================================
conn = sqlite3.connect('khatakhat_enterprise_v5.db', check_same_thread=False)

def get_engine_data():
    try:
        df = pd.read_sql("SELECT * FROM ledger", conn)
        if not df.empty:
            df['due_date'] = pd.to_datetime(df['due_date'], errors='coerce')
        return df
    except Exception:
        return pd.DataFrame()

def persist_to_db(df):
    try:
        df.columns = [c.lower().strip().replace(' ', '_') for c in df.columns]
        mapping = {'customer_name': 'customer', 'payment_status': 'status', 'trust': 'trust_score'}
        df = df.rename(columns=mapping)
        df.to_sql("ledger", conn, if_exists="replace", index=False)
        return True
    except Exception as e:
        st.error(f"DATABASE_SYNC_ERROR: {str(e)}")
        return False

def initialize_system():
    customers = ["Enterprise Corp", "Global Systems", "Matrix Retail", "Alpha Logistics", "Vision Tech", "Zenith Solutions"]
    data = []
    for i in range(150):
        status = np.random.choice(["Paid", "Pending"], p=[0.65, 0.35])
        data.append({
            "customer": np.random.choice(customers),
            "amount": float(np.random.randint(5000, 200000)),
            "status": status,
            "due_date": (datetime.now() + timedelta(days=np.random.randint(-60, 60))).strftime('%Y-%m-%d'),
            "trust_score": int(np.random.randint(300, 900))
        })
    df = pd.DataFrame(data)
    persist_to_db(df)
    return get_engine_data()

def ai_intelligence_brief(title, analysis):
    st.markdown(f"""
    <div class="ai-advisory">
        <div class="ai-tag">ENTERPRISE_AI_CORE_v6.0</div>
        <h4 style="margin: 10px 0; color: #FFFFFF; font-family: 'Roboto Mono';">{title}</h4>
        <p style="color: #90A4AE; font-size: 14px; line-height: 1.6; font-family: 'Inter';">{analysis}</p>
    </div>
    """, unsafe_allow_html=True)

# ==========================================
# 3. MISSION CRITICAL MODULES
# ==========================================

def mod_dashboard(df):
    st.title("EXECUTIVE_COMMAND_CENTER")
    
    # Safety Check for Calculations
    if df.empty:
        st.warning("SYSTEM_IDLE: NO DATA DETECTED.")
        return

    pending_df = df[df['status'].str.lower() == 'pending']
    paid_df = df[df['status'].str.lower() == 'paid']
    
    total_val = pending_df['amount'].sum() if not pending_df.empty else 0
    paid_val = paid_df['amount'].sum() if not paid_df.empty else 0
    health_ratio = (paid_val / (total_val + paid_val)) * 100 if (total_val + paid_val) > 0 else 0

    # Cluster Analysis Logic
    risk_cluster = len(pending_df[pending_df['trust_score'] < 450])
    
    brief = (f"Capital Health Audit complete. Efficiency at {health_ratio:.1f}%. "
             f"Identified {risk_cluster} critical risk clusters. "
             "Recommended Action: Systematic liquidations of Grade-D accounts to stabilize cash flow.")
    ai_intelligence_brief("CAPITAL_HEALTH_AUDIT", brief)

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("TOTAL_OUTSTANDING", f"₹{total_val:,.0f}")
    c2.metric("HEALTH_RATIO", f"{health_ratio:.1f}%")
    c3.metric("NETWORK_TRUST", f"{int(df['trust_score'].mean())}")
    c4.metric("RISK_CLUSTER", risk_cluster)

    st.subheader("3D_CREDIT_TOPOGRAPHY")
    fig = px.scatter_3d(df, x='amount', y='trust_score', z='status', color='status',
                        color_discrete_map={'Pending': '#FF5252', 'Paid': '#1DE9B6'},
                        template="plotly_dark", opacity=0.8)
    fig.update_layout(scene=dict(bgcolor="#0B0E14"), margin=dict(l=0,r=0,b=0,t=0))
    st.plotly_chart(fig, use_container_width=True)

def mod_recovery_ops(df):
    st.title("RECOVERY_PROTOCOL_ENGINE")
    pending = df[df['status'].str.lower() == 'pending']
    
    if pending.empty:
        st.success("NO_PENDING_OPERATIONS.")
        return

    col1, col2 = st.columns([1, 1.5])
    with col1:
        target = st.selectbox("TARGET_SELECTION", pending['customer'].unique())
        client = pending[pending['customer'] == target].iloc[0]
        st.write(f"EXPOSURE: ₹{client['amount']:,.0f}")
        st.progress(client['trust_score']/900, text=f"TRUST: {client['trust_score']}")
    
    with col2:
        # AI Decision Logic
        prob = (client['trust_score'] / 900) * 100
        ai_intelligence_brief("SMART_RECOVERY_STRATEGY", 
                            f"Entity {target} maintains a {prob:.1f}% trust confidence. "
                            "API-Enabled Nudge Protocol is prepped. Suggested tone: " + 
                            ("Assertive-Legal" if prob < 50 else "Collaborative-Nudge"))
        
        if st.button("EXECUTE_API_NUDGE_PROTOCOL"):
            with st.spinner("INITIATING_REST_HANDSHAKE..."):
                response = KhataKhatAPI.trigger_nudge(target, client['amount'])
                st.toast(f"PROTOCOL_SUCCESS: {response['trace_id']}", icon="✅")
                st.code(f"API_LOG: Status={response['status']} | Provider={response['provider']} | Time={response['timestamp']}")

# ==========================================
# 4. SYSTEM ROUTING & AUTH
# ==========================================
def main():
    if "auth" not in st.session_state: st.session_state.auth = False
    
    if not st.session_state.auth:
        st.title("KHATAKHAT_AI_SYSTEM_ACCESS")
        _, cent, _ = st.columns([1, 0.8, 1])
        with cent:
            u = st.text_input("ENTITY_ID", value="kd_merchant")
            p = st.text_input("SECURE_KEY", type="password", value="admin123")
            if st.button("AUTHORIZE_SYSTEM_ACCESS"):
                if u == "kd_merchant" and p == "admin123":
                    st.session_state.auth = True
                    st.rerun()
                else:
                    st.error("ACCESS_DENIED")
        return

    # Load and Guard Data
    df = get_engine_data()
    if df.empty:
        df = initialize_system()

    with st.sidebar:
        st.title("KHATAKHAT_AI")
        st.markdown("---")
        menu = ["DASHBOARD", "SMART_LEDGER", "RISK_PREDICTOR", "RECOVERY_OPS", "AUDIT_RECON"]
        choice = st.radio("NAVIGATION", menu)
        st.markdown("---")
        if st.button("TERMINATE_SESSION"):
            st.session_state.auth = False
            st.rerun()

    # Routing
    if choice == "DASHBOARD":
        mod_dashboard(df)
    elif choice == "SMART_LEDGER":
        st.title("SMART_LEDGER_SYSTEM")
        st.dataframe(df, use_container_width=True, hide_index=True)
    elif choice == "RISK_PREDICTOR":
        st.title("RISK_PREDICTIVE_MODEL")
        if not df.empty:
            pend = df[df['status'].str.lower() == 'pending'].copy()
            pend['risk_index'] = (900 - pend['trust_score']) / 6
            fig = px.scatter(pend, x="amount", y="risk_index", size="amount", color="risk_index", 
                             color_continuous_scale="Viridis", template="plotly_dark")
            st.plotly_chart(fig, use_container_width=True)
    elif choice == "RECOVERY_OPS":
        mod_recovery_ops(df)
    elif choice == "AUDIT_RECON":
        st.title("AUDIT_RECONCILIATION")
        ai_intelligence_brief("INTEGRITY_REPORT", "SQL persistence active. Audit logs synchronized. Ready for external JSON/CSV serialization.")
        st.download_button("EXPORT_SYSTEM_AUDIT", df.to_csv(index=False), "khatakhat_audit.csv")

if __name__ == "__main__":
    main()
