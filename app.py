import streamlit as st
import pandas as pd
import numpy as np
import sqlite3
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import io

# ==========================================
# 0. TITANIUM CYBER UI CONFIG
# ==========================================
st.set_page_config(page_title="KhataKhat Pro | Enterprise AI", layout="wide", page_icon="🛡️")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&family=Inter:wght@300;400;600&display=swap');
    
    .stApp { background: linear-gradient(135deg, #05070A 0%, #0F172A 100%); color: #F8FAFC; font-family: 'Inter', sans-serif; }
    
    /* Neon Cyber Cards */
    .khatakhat-panel {
        background: rgba(30, 41, 59, 0.4);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(0, 242, 255, 0.2);
        border-left: 5px solid #00F2FF;
        padding: 25px;
        border-radius: 15px;
        margin-bottom: 25px;
        color: #F8FAFC;
    }
    
    /* High-Readability Headers */
    h1, h2, h3 { color: #00F2FF; font-family: 'Orbitron', sans-serif; text-transform: uppercase; letter-spacing: 2px; }
    
    /* Glowing Metrics */
    div[data-testid="stMetricValue"] { color: #10B981 !important; text-shadow: 0 0 10px rgba(16, 185, 129, 0.5); }

    /* Buttons: Gradient Psychedelic */
    .stButton>button {
        background: linear-gradient(90deg, #6366F1, #00F2FF);
        color: white; border: none; border-radius: 12px;
        padding: 12px 24px; font-weight: bold; transition: 0.3s;
    }
    .stButton>button:hover { transform: scale(1.02); box-shadow: 0 0 20px rgba(0, 242, 255, 0.6); }
    
    /* Sidebar */
    section[data-testid="stSidebar"] { background-color: #020617 !important; border-right: 1px solid #00F2FF33; }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 1. BILINGUAL DICTIONARY
# ==========================================
lex = {
    "English": {
        "m1": "📊 Executive Command", "m2": "📂 Bulk Data Ingest", "m3": "📓 Smart Khata", 
        "m4": "🔮 AI Predictor", "m5": "🎯 Recovery Ops", "m6": "⚠️ Risk Radar",
        "m7": "📅 Action Scheduler", "m8": "🎖️ Trust Leaderboard", "m9": "⚖️ Legal Center", 
        "m10": "🏦 Bankability", "m11": "🤖 Auto-Logs", "m12": "📄 Audit Reports",
        "ai_head": "KhataKhat AI Intelligence", "wa": "Launch WhatsApp Nudge 🚀"
    },
    "Hindi": {
        "m1": "📊 मुख्य डैशबोर्ड", "m2": "📂 डेटा अपलोड", "m3": "📓 स्मार्ट खाता", 
        "m4": "🔮 जोखिम भविष्यवाणी", "m5": "🎯 वसूली केंद्र", "m6": "⚠️ जोखिम रडार",
        "m7": "📅 स्मार्ट कैलेंडर", "m8": "🎖️ भरोसा स्कोर", "m9": "⚖️ कानूनी केंद्र", 
        "m10": "🏦 बैंक योग्यता", "m11": "🤖 ऑटो-लॉग्स", "m12": "📄 ऑडिट रिपोर्ट",
        "ai_head": "खटाखट AI विश्लेषण", "wa": "व्हाट्सएप भेजें 🚀"
    }
}

# ==========================================
# 2. DATA PROTECTION & PERSISTENCE
# ==========================================
conn = sqlite3.connect('khatakhat_enterprise.db', check_same_thread=False)

def get_data():
    try:
        df = pd.read_sql("SELECT * FROM ledger", conn)
        df['due_date'] = pd.to_datetime(df['due_date'])
        return df
    except:
        return pd.DataFrame()

def save_data(df):
    df.columns = [c.lower().replace(' ', '_') for c in df.columns]
    mapping = {'customer_name': 'customer', 'payment_status': 'status', 'trust': 'trust_score'}
    df = df.rename(columns=mapping)
    df.to_sql("ledger", conn, if_exists="replace", index=False)

def generate_enterprise_seeds():
    names = ["Sharma Electronics", "Verma Grocery", "Rajesh Traders", "Priya Fashion", "Malhotra Sweets", "Global Mart", "Arora Logistics"]
    data = []
    for i in range(150):
        status = np.random.choice(["Paid", "Pending"], p=[0.65, 0.35])
        data.append({
            "customer": np.random.choice(names),
            "amount": np.random.randint(5000, 95000),
            "status": status,
            "due_date": (datetime.now() + timedelta(days=np.random.randint(-40, 40))).strftime('%Y-%m-%d'),
            "trust_score": np.random.randint(300, 900)
        })
    df = pd.DataFrame(data)
    save_data(df)
    return get_data()

def ai_brief(title, msg):
    st.markdown(f"<div class='khatakhat-panel'><h4 style='margin:0; color:#00F2FF;'>🤖 {title}</h4><p style='margin-top:10px; line-height:1.6;'>{msg}</p></div>", unsafe_allow_html=True)

# ==========================================
# 3. ENTERPRISE MODULES
# ==========================================

# MODULE 9: LEGAL COMMAND CENTER
def mod_legal(df, L):
    st.title(lex[L]["m9"])
    pending = df[df['status'].str.lower() == 'pending']
    critical = pending[pending['trust_score'] < 450]
    
    ai_brief("Legal Risk Analysis", f"KD, we have {len(critical)} accounts that have crossed the 'Settlement window'. I recommend generating formal notices for invoices above ₹50,000.")
    
    target = st.selectbox("Select Account for Legal Notice", critical['customer'].unique() if not critical.empty else ["No Critical Accounts"])
    if target != "No Critical Accounts":
        client = critical[critical['customer'] == target].iloc[0]
        st.markdown(f"""
        <div style='background:white; color:black; padding:30px; border: 1px solid gray;'>
        <h2 style='text-align:center; color:black;'>LETTER OF DEMAND</h2>
        <p><b>Date:</b> {datetime.now().strftime('%d %b, %Y')}</p>
        <p><b>To:</b> {target}</p>
        <p>This is a formal notice regarding the outstanding balance of <b>₹{client['amount']:,.0f}</b> which was due on {client['due_date'].date()}. 
        Failure to settle this amount within 7 days will result in legal proceedings and a report to credit bureaus.</p>
        <p><b>Signed,</b><br>KhataKhat Legal Department (for KD)</p>
        </div>
        """, unsafe_allow_html=True)
        st.button("📥 Download Legal PDF (Mock)")

# MODULE 10: MERCHANT BANKABILITY
def mod_bankability(df, L):
    st.title(lex[L]["m10"])
    paid_total = df[df['status'].str.lower() == 'paid']['amount'].sum()
    total = df['amount'].sum()
    b_score = (paid_total / total) * 100
    
    ai_brief("Lending Readiness", f"Your Merchant Score is **{int(b_score)}/100**. This makes you eligible for working capital loans up to ₹5.5 Lakhs based on your collection efficiency.")
    
    fig = go.Figure(go.Indicator(
        mode = "gauge+number", value = b_score, title = {'text': "Bankability Score"},
        gauge = {'axis': {'range': [None, 100]}, 'bar': {'color': "#10B981"}}
    ))
    fig.update_layout(template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig, use_container_width=True)

# MODULE 11: AUTOMATION LOGS
def mod_logs(L):
    st.title(lex[L]["m11"])
    ai_brief("System Health", "All automated triggers are firing correctly. Here is the last 24-hour activity log.")
    log_data = [
        {"Time": "10:00 AM", "Action": "WhatsApp Sent", "Target": "Sharma Electronics", "Result": "Delivered"},
        {"Time": "11:30 AM", "Action": "Risk Level Update", "Target": "System-Wide", "Result": "Success"},
        {"Time": "01:15 PM", "Action": "Auto-Nudge", "Target": "Verma Grocery", "Result": "Opened"}
    ]
    st.table(log_data)

# ==========================================
# 4. MAIN NAV & ROUTING
# ==========================================
def main():
    if "auth" not in st.session_state: st.session_state.auth = False
    if not st.session_state.auth:
        st.markdown("<h1 style='text-align:center; font-size:50px;'>🛡️ KHATAKHAT PRO</h1>", unsafe_allow_html=True)
        _, center, _ = st.columns([1,1,1])
        with center:
            u = st.text_input("Merchant ID", value="kd_merchant")
            p = st.text_input("Access Key", type="password", value="admin123")
            if st.button("Access Command Center"):
                st.session_state.auth = True
                st.rerun()
        return

    df = get_data()
    if df.empty: df = generate_enterprise_seeds()

    with st.sidebar:
        st.title("KhataKhat")
        L = st.radio("Language / भाषा", ["English", "Hindi"])
        st.markdown("---")
        menu = [lex[L][f"m{i}"] for i in range(1, 13)]
        choice = st.radio("Enterprise Navigation", menu)
        if st.button("Terminate Session"):
            st.session_state.auth = False
            st.rerun()

    # Routing Table
    if choice == lex[L]["m1"]: 
        st.title(lex[L]["m1"])
        p = df[df['status'].str.lower() == 'pending']
        c1, c2, c3 = st.columns(3)
        c1.metric("Floating Debt", f"₹{p['amount'].sum():,.0F}")
        c2.metric("Trust Health", f"{int(df['trust_score'].mean())}")
        c3.metric("System Load", "Optimal")
        fig = px.scatter_3d(df, x='amount', y='trust_score', z='status', color='status', template="plotly_dark")
        st.plotly_chart(fig, use_container_width=True)
        
    elif choice == lex[L]["m2"]:
        st.title(lex[L]["m2"]); f = st.file_uploader("Drop Ledger")
        if f: d = pd.read_csv(f) if f.name.endswith('.csv') else pd.read_excel(f); save_data(d); st.success("Synced!"); st.rerun()

    elif choice == lex[L]["m3"]: st.title(lex[L]["m3"]); st.dataframe(df, column_config={"trust_score": st.column_config.ProgressColumn("Trust")}, use_container_width=True)
    elif choice == lex[L]["m4"]: 
        st.title(lex[L]["m4"])
        pend = df[df['status'].str.lower() == 'pending'].copy()
        pend['risk'] = (900 - pend['trust_score']) / 6
        st.plotly_chart(px.scatter(pend, x="amount", y="risk", size="amount", color="risk", template="plotly_dark"))

    elif choice == lex[L]["m9"]: mod_legal(df, L)
    elif choice == lex[L]["m10"]: mod_bankability(df, L)
    elif choice == lex[L]["m11"]: mod_logs(L)
    elif choice == lex[L]["m12"]: st.title(lex[L]["m12"]); st.download_button("Export CSV", df.to_csv(index=False), "khata_audit.csv")
    else: st.info(f"{choice} is active. Intelligence background sync running...")

if __name__ == "__main__":
    main()
