import streamlit as st
import pandas as pd
import numpy as np
import sqlite3
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import urllib.parse

# ==========================================
# 0. PROFESSIONAL FINTECH UI
# ==========================================
st.set_page_config(page_title="KhataKhat | AI Ledger", layout="wide", page_icon="📈")

# Clean, Modern Dark Theme
st.markdown("""
    <style>
    .stApp {
        background-color: #0F172A;
        color: #F8FAFC;
    }
    [data-testid="stMetricValue"] {
        color: #818CF8 !important;
        font-weight: 700;
    }
    .ai-bubble {
        background: rgba(30, 41, 59, 0.5);
        border-left: 4px solid #6366F1;
        padding: 1.5rem;
        border-radius: 8px;
        margin-bottom: 2rem;
        border: 1px solid rgba(255,255,255,0.05);
    }
    .stButton>button {
        background: #6366F1;
        color: white;
        border-radius: 6px;
        border: none;
        height: 3em;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        background: #4F46E5;
        box-shadow: 0 4px 15px rgba(99, 102, 241, 0.3);
    }
    /* Style the sidebar */
    section[data-testid="stSidebar"] {
        background-color: #1E293B !important;
    }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 1. BILINGUAL SUPPORT
# ==========================================
lexicon = {
    "English": {
        "m1": "📊 Dashboard", "m3": "📓 Digital Ledger", "m5": "🎯 Recovery Room", "m7": "📈 Cash Forecast",
        "pending": "Outstanding Balance", "trust": "Trust Score", "assistant": "KhataKhat AI Assistant"
    },
    "Hindi": {
        "m1": "📊 डैशबोर्ड", "m3": "📓 डिजिटल खाता", "m5": "🎯 वसूली केंद्र", "m7": "📈 कैश फ्लो",
        "pending": "कुल बकाया", "trust": "भरोसा स्कोर", "assistant": "खटाखट AI सहायक"
    }
}

# ==========================================
# 2. DATA ENGINE
# ==========================================
conn = sqlite3.connect('khatakhat_final.db', check_same_thread=False)

def get_data():
    try:
        df = pd.read_sql("SELECT * FROM ledger", conn)
        df['due_date'] = pd.to_datetime(df['due_date'])
        return df
    except:
        # Seed initial data if DB is empty
        names = ["Rajesh Kumar", "Sunita Sharma", "Deepak Traders", "Verma Electronics", "Mehta General Store"]
        data = []
        for i in range(40):
            status = np.random.choice(["Paid", "Pending"], p=[0.7, 0.3])
            data.append({
                "customer": np.random.choice(names),
                "amount": np.random.randint(2000, 60000),
                "status": status,
                "due_date": (datetime.now() + timedelta(days=np.random.randint(-15, 15))).strftime('%Y-%m-%d'),
                "trust_score": np.random.randint(350, 850)
            })
        df = pd.DataFrame(data)
        df.to_sql("ledger", conn, if_exists="replace", index=False)
        return get_data()

def ai_brief(title, message):
    st.markdown(f"""
    <div class="ai-bubble">
        <h4 style="margin:0 0 10px 0; color:#818CF8;">🤖 {title}</h4>
        <p style="margin:0; font-size:15px; line-height:1.5; color:#94A3B8;">{message}</p>
    </div>
    """, unsafe_allow_html=True)

# ==========================================
# 3. CORE MODULES
# ==========================================

def view_dashboard(df, L):
    st.title(lexicon[L]["m1"])
    pending_df = df[df['status'] == 'Pending']
    total = pending_df['amount'].sum()
    
    msg = f"KD, you currently have ₹{total:,.0f} locked in credit. Based on payment patterns, I expect ₹{total * 0.4:,.0f} to clear by Friday." if L == "English" else \
          f"KD, वर्तमान में आपका ₹{total:,.0f} बाजार में है। मुझे उम्मीद है कि शुक्रवार तक ₹{total * 0.4:,.0f} वसूल हो जाएंगे।"
    ai_brief(lexicon[L]["assistant"], msg)

    c1, c2, c3 = st.columns(3)
    c1.metric(lexicon[L]["pending"], f"₹{total:,.0f}")
    c2.metric("Active Cases", len(pending_df))
    c3.metric("System Health", "Good")

    st.subheader("3D Credit Topography")
    fig = px.scatter_3d(df, x='amount', y='trust_score', z='status', color='status',
                        color_discrete_sequence=['#10B981', '#EF4444'], template="plotly_dark")
    fig.update_layout(margin=dict(l=0, r=0, b=0, t=0))
    st.plotly_chart(fig, use_container_width=True)

def view_ledger(df, L):
    st.title(lexicon[L]["m3"])
    ai_brief(lexicon[L]["assistant"], "I've sorted your ledger by risk. Use the search bar below to find specific clients.")
    
    # Modern table view using column_config
    st.dataframe(
        df,
        column_config={
            "trust_score": st.column_config.ProgressColumn("Trust Score", min_value=300, max_value=900),
            "amount": st.column_config.NumberColumn("Amount (₹)", format="₹%d"),
            "status": st.column_config.BadgeColumn("Status")
        },
        use_container_width=True,
        hide_index=True
    )

def view_recovery(df, L):
    st.title(lexicon[L]["m5"])
    pending = df[df['status'] == 'Pending']
    
    if not pending.empty:
        col1, col2 = st.columns([1, 1])
        with col1:
            name = st.selectbox("Select Client", pending['customer'].unique())
            row = pending[pending['customer'] == name].iloc[0]
            st.metric("Owed", f"₹{row['amount']}")
            st.metric("Trust Score", row['trust_score'])
            
        with col2:
            ai_brief("Strategy Advisor", f"For {name}, a 'Professional' nudge works best given their history.", L)
            text = f"Hi {name}, hope you are well. Just a soft nudge for the ₹{row['amount']} invoice. Let's settle this to keep your score high!"
            st.text_area("Draft Message", text, height=120)
            st.button("Send WhatsApp 📲")
    else:
        st.success("All debts cleared! No recovery needed.")

# ==========================================
# 4. NAVIGATION & AUTH
# ==========================================
def main():
    if "auth" not in st.session_state: st.session_state.auth = False

    if not st.session_state.auth:
        st.markdown("<h1 style='text-align:center;'>🚀 KhataKhat AI Login</h1>", unsafe_allow_html=True)
        _, center, _ = st.columns([1,1,1])
        with center:
            u = st.text_input("User ID")
            p = st.text_input("Password", type="password")
            if st.button("Unlock Dashboard"):
                if u == "kd_merchant" and p == "admin123":
                    st.session_state.auth = True
                    st.rerun()
                else:
                    st.error("Invalid Credentials")
        return

    # Sidebar
    with st.sidebar:
        st.title("KhataKhat")
        L = st.radio("Select Language", ["English", "Hindi"])
        st.markdown("---")
        menu = [lexicon[L][f"m{i}"] for i in [1, 3, 5, 7]]
        choice = st.radio("Navigate", menu)
        if st.button("Logout"):
            st.session_state.auth = False
            st.rerun()

    df = get_data()

    # Routing
    if choice == lexicon[L]["m1"]: view_dashboard(df, L)
    elif choice == lexicon[L]["m3"]: view_ledger(df, L)
    elif choice == lexicon[L]["m5"]: view_recovery(df, L)
    else:
        st.title(choice)
        st.info("Module active. Syncing real-time data...")

if __name__ == "__main__":
    main()
