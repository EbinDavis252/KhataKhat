import streamlit as st
import pandas as pd
import numpy as np
import sqlite3
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import urllib.parse

# ==========================================
# 0. BALANCED PROFESSIONAL UI
# ==========================================
st.set_page_config(page_title="KhataKhat | AI Ledger", layout="wide", page_icon="📈")

# Balanced "FinTech Dark" CSS
st.markdown("""
    <style>
    .stApp {
        background-color: #0F172A; /* Deep Navy */
        color: #F8FAFC;
    }
    [data-testid="stMetricValue"] {
        color: #6366F1 !important; /* Indigo Accent */
        font-weight: 800;
    }
    .ai-card {
        background: rgba(30, 41, 59, 0.7);
        border-left: 5px solid #6366F1;
        padding: 20px;
        border-radius: 10px;
        margin-bottom: 20px;
        border: 1px solid rgba(255,255,255,0.1);
    }
    .stButton>button {
        background: #6366F1;
        color: white;
        border-radius: 8px;
        width: 100%;
        border: none;
        transition: 0.3s;
    }
    .stButton>button:hover {
        background: #4F46E5;
        box-shadow: 0 4px 12px rgba(99, 102, 241, 0.4);
    }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 1. BILINGUAL DICTIONARY
# ==========================================
lang_data = {
    "English": {
        "brand": "KhataKhat AI",
        "m1": "📊 Dashboard", "m2": "📂 Upload Data", "m3": "📓 Digital Ledger",
        "m4": "🔮 AI Prediction", "m5": "🎯 Recovery Room", "m6": "⚠️ Risk Radar",
        "m7": "📈 Cash Forecast", "m8": "🏅 Trust Score", "m9": "💡 Insights", "m10": "⚙️ Settings",
        "outstanding": "Outstanding Amount", "trust": "Trust Rating", "action": "Take Action"
    },
    "Hindi": {
        "brand": "खटाखट AI",
        "m1": "📊 डैशबोर्ड", "m2": "📂 डेटा अपलोड", "m3": "📓 डिजिटल खाता",
        "m4": "🔮 भविष्यवाणियां", "m5": "🎯 वसूली केंद्र", "m6": "⚠️ जोखिम रडार",
        "m7": "📈 कैश फ्लो", "m8": "🏅 भरोसा स्कोर", "m9": "💡 मुख्य बातें", "m10": "⚙️ सेटिंग्स",
        "outstanding": "कुल बकाया", "trust": "भरोसा रेटिंग", "action": "कार्यवाही करें"
    }
}

# ==========================================
# 2. DATA CORE
# ==========================================
conn = sqlite3.connect('khatakhat_pro.db', check_same_thread=False)

def get_data():
    try:
        df = pd.read_sql("SELECT * FROM ledger", conn)
        df['due_date'] = pd.to_datetime(df['due_date'])
        return df
    except:
        # Create Dummy Data for project start
        data = []
        for i in range(50):
            status = np.random.choice(["Paid", "Pending"], p=[0.7, 0.3])
            data.append({
                "customer": np.random.choice(["Amit Kumar", "Sita Devi", "Rajesh Traders", "Kapoor Electronics", "Priya Stores"]),
                "amount": np.random.randint(1000, 50000),
                "status": status,
                "due_date": (datetime.now() + timedelta(days=np.random.randint(-20, 20))).strftime('%Y-%m-%d'),
                "trust_score": np.random.randint(300, 900)
            })
        df = pd.DataFrame(data)
        df.to_sql("ledger", conn, if_exists="replace", index=False)
        return get_data()

# ==========================================
# 3. COMPONENT: AI ASSISTANT
# ==========================================
def ai_assistant(title, text, lang):
    st.markdown(f"""
    <div class="ai-card">
        <h4 style="margin-top:0; color:#818CF8;">🤖 {title}</h4>
        <p style="color:#CBD5E1; font-size:15px;">{text}</p>
    </div>
    """, unsafe_allow_html=True)

# ==========================================
# 4. MODULES
# ==========================================

def show_dashboard(df, l):
    st.title(lang_data[l]["m1"])
    pending = df[df['status'] == 'Pending']
    
    # AI Logic
    total = pending['amount'].sum()
    ai_text = f"KD, you have ₹{total:,.0f} to recover. 3 customers are currently overdue. I recommend prioritizing 'Rajesh Traders' as their trust score is slipping." if l == "English" else \
              f"KD, आपके पास वसूलने के लिए ₹{total:,.0f} हैं। 3 ग्राहक वर्तमान में विलंबित हैं। मैं 'राजेश ट्रेडर्स' को प्राथमिकता देने की सलाह देता हूं।"
    ai_assistant(lang_data[l]["brand"], ai_text, l)

    c1, c2, c3 = st.columns(3)
    c1.metric(lang_data[l]["outstanding"], f"₹{total:,.0f}")
    c2.metric("Active Debtors", len(pending))
    c3.metric("Avg Trust", int(df['trust_score'].mean()))

    st.subheader("3D Debt Analysis")
    fig = px.scatter_3d(df, x='amount', y='trust_score', z='status', color='status', 
                        template="plotly_dark", color_discrete_sequence=['#10B981', '#F43F5E'])
    st.plotly_chart(fig, use_container_width=True)

def show_ledger(df, l):
    st.title(lang_data[l]["m3"])
    ai_assistant(lang_data[l]["brand"], "Here is your filtered ledger. I have added color bars to 'Trust Scores' so you can spot risky clients instantly.", l)
    
    # FIX: Using st.column_config instead of df.style to avoid ImportError
    st.dataframe(
        df,
        column_config={
            "trust_score": st.column_config.ProgressColumn(
                "Trust Rating", help="Score from 300 to 900", min_value=300, max_value=900, format="%d"
            ),
            "amount": st.column_config.NumberColumn("Amount (₹)", format="₹%d"),
            "status": st.column_config.SelectboxColumn("Status", options=["Paid", "Pending"])
        },
        use_container_width=True
    )

def show_recovery(df, l):
    st.title(lang_data[l]["m5"])
    pending = df[df['status'] == 'Pending']
    
    col1, col2 = st.columns([1, 1])
    with col1:
        target = st.selectbox("Select Customer", pending['customer'].unique())
        client = pending[pending['customer'] == target].iloc[0]
        st.write(f"### Debt: ₹{client['amount']}")
        st.write(f"### Trust Score: {client['trust_score']}")
        
    with col2:
        ai_assistant("Strategy Room", f"For {target}, a 'Reciprocity' nudge is best. Remind them of your long-term relationship.", l)
        msg = f"Hello {target}, KD here. Hope business is good! Just a reminder for the pending ₹{client['amount']}. Let's clear this to keep your Trust Rating at {client['trust_score']}!"
        st.text_area("Recovery Draft", msg, height=120)
        st.button("Send via WhatsApp 📲")

def show_forecast(df, l):
    st.title(lang_data[l]["m7"])
    ai_assistant(lang_data[l]["brand"], "Analyzing your future cash inflow based on due dates.", l)
    
    daily = df.groupby('due_date')['amount'].sum().reset_index()
    fig = px.area(daily, x='due_date', y='amount', title="Expected Daily Collection", template="plotly_dark")
    fig.update_traces(line_color='#6366F1')
    st.plotly_chart(fig, use_container_width=True)

# ==========================================
# 5. MAIN ROUTING
# ==========================================
def main():
    if "logged_in" not in st.session_state: st.session_state.logged_in = False

    if not st.session_state.logged_in:
        st.markdown("<h1 style='text-align:center;'>🛡️ KhataKhat AI Login</h1>", unsafe_allow_html=True)
        c1, c2, c3 = st.columns([1,1,1])
        with col2 := c2:
            u = st.text_input("User")
            p = st.text_input("Pass", type="password")
            if st.button("Login"):
                if u == "kd_merchant" and p == "admin123":
                    st.session_state.logged_in = True
                    st.rerun()
        return

    # Sidebar Navigation
    with st.sidebar:
        st.title("KhataKhat 🚀")
        language = st.radio("Language / भाषा", ["English", "Hindi"])
        st.markdown("---")
        choice = st.radio("Menu", [lang_data[language][f"m{i}"] for i in range(1, 11)])
        if st.button("Logout"):
            st.session_state.logged_in = False
            st.rerun()

    df = get_data()

    # Routing
    if choice == lang_data[language]["m1"]: show_dashboard(df, language)
    elif choice == lang_data[language]["m3"]: show_ledger(df, language)
    elif choice == lang_data[language]["m5"]: show_recovery(df, language)
    elif choice == lang_data[language]["m7"]: show_forecast(df, language)
    else:
        st.title(choice)
        st.info("Module active. Data processing in progress...")

if __name__ == "__main__":
    main()
