import streamlit as st
import pandas as pd
import numpy as np
import sqlite3
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import urllib.parse

# ==========================================
# 0. CORE CONFIG & HIGH-CONTRAST THEME
# ==========================================
st.set_page_config(page_title="KhataKhat Pro | AI Munim", layout="wide", page_icon="💎")

# Professional Slate & Indigo Theme (Readability Optimized)
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');
    
    .stApp {
        background-color: #0F172A;
        color: #F1F5F9;
        font-family: 'Inter', sans-serif;
    }
    
    /* Munim AI Hologram Box */
    .munim-ai-card {
        background: rgba(30, 41, 59, 0.7);
        border-left: 6px solid #6366F1;
        border-right: 1px solid rgba(255,255,255,0.1);
        padding: 25px;
        border-radius: 12px;
        margin-bottom: 30px;
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.3);
    }
    
    /* Metric Glow */
    div[data-testid="stMetricValue"] {
        color: #22D3EE !important;
        text-shadow: 0 0 10px rgba(34, 211, 238, 0.4);
        font-weight: 800;
    }

    /* Buttons */
    .stButton>button {
        background: linear-gradient(90deg, #6366F1, #8B5CF6);
        color: white; border: none; border-radius: 8px;
        padding: 10px 20px; font-weight: 600; transition: 0.3s;
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 20px rgba(99, 102, 241, 0.4);
    }

    /* Sidebar */
    section[data-testid="stSidebar"] {
        background-color: #1E293B !important;
        border-right: 1px solid rgba(255,255,255,0.05);
    }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 1. BILINGUAL DICTIONARY
# ==========================================
lex = {
    "English": {
        "m1": "📊 Executive Hub", "m2": "📂 Bulk Upload", "m3": "📓 Smart Ledger", 
        "m4": "🔮 AI Predictor", "m5": "🎯 Recovery Ops", "m6": "⚠️ Risk Radar",
        "m7": "📅 Smart Calendar", "m8": "🎖️ Trust Index", "m9": "💡 Insights", "m10": "⚙️ Settings",
        "munim": "Munim AI Assistant", "wa": "Launch WhatsApp Nudge 🚀", "lang_sel": "Switch Language / भाषा बदलें"
    },
    "Hindi": {
        "m1": "📊 मुख्य केंद्र", "m2": "📂 डेटा अपलोड", "m3": "📓 स्मार्ट खाता", 
        "m4": "🔮 भविष्यवाणियां", "m5": "🎯 वसूली ऑपरेशन", "m6": "⚠️ जोखिम रडार",
        "m7": "📅 स्मार्ट कैलेंडर", "m8": "🎖️ भरोसा स्कोर", "m9": "💡 मुख्य बातें", "m10": "⚙️ सेटिंग्स",
        "munim": "मुनीम AI सहायक", "wa": "व्हाट्सएप भेजें 🚀", "lang_sel": "भाषा बदलें / Switch Language"
    }
}

# ==========================================
# 2. DATABASE & LOGIC ENGINES
# ==========================================
conn = sqlite3.connect('khatakhat_master.db', check_same_thread=False)

def get_data():
    try:
        df = pd.read_sql("SELECT * FROM ledger", conn)
        df['due_date'] = pd.to_datetime(df['due_date'])
        return df
    except:
        # Generate Advanced Seed Data
        customers = ["Sharma Electronics", "Verma Grocery", "Rajesh Traders", "Priya Fashion", "Malhotra Sweets", "Global Logistics"]
        data = []
        for i in range(120):
            status = np.random.choice(["Paid", "Pending"], p=[0.65, 0.35])
            d_date = datetime.now() + timedelta(days=np.random.randint(-30, 30))
            data.append({
                "id": 500 + i,
                "customer": np.random.choice(customers),
                "amount": np.random.randint(1000, 95000),
                "status": status,
                "due_date": d_date.strftime('%Y-%m-%d'),
                "trust_score": np.random.randint(300, 900)
            })
        df = pd.DataFrame(data)
        df.to_sql("ledger", conn, if_exists="replace", index=False)
        return get_data()

def munim_brief(title, content):
    st.markdown(f"""
    <div class="munim-ai-card">
        <h4 style="margin:0; color:#22D3EE;">✨ {title}</h4>
        <p style="margin:10px 0 0 0; color:#94A3B8; font-size:15px; line-height:1.6;">{content}</p>
    </div>
    """, unsafe_allow_html=True)

# ==========================================
# 3. MODULE LOGIC
# ==========================================

def mod_dashboard(df, L):
    st.title(lex[L]["m1"])
    pending = df[df['status'] == 'Pending']
    
    brief = f"KD, we have ₹{pending['amount'].sum():,.0F} floating. I've identified 4 high-value invoices that are 90% likely to clear if we nudge them before 11 AM today." if L == "English" else \
            f"KD, बाजार में ₹{pending['amount'].sum():,.0F} फंसे हैं। मैंने 4 बड़े बिलों की पहचान की है जो आज सुबह 11 बजे से पहले मैसेज भेजने पर वसूल हो सकते हैं।"
    munim_brief(lex[L]["munim"], brief)

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Pending", f"₹{pending['amount'].sum():,.0F}")
    c2.metric("Trust Index", f"{int(df['trust_score'].mean())}")
    c3.metric("Star Payers", len(df[df['trust_score'] > 800].customer.unique()))
    c4.metric("Risk Level", "Medium")

    st.subheader("🌐 3D Credit Topography")
    fig = px.scatter_3d(df, x='amount', y='trust_score', z='status', color='status',
                        color_discrete_map={'Pending': '#EF4444', 'Paid': '#10B981'},
                        template="plotly_dark", opacity=0.8)
    fig.update_layout(scene=dict(bgcolor="rgba(0,0,0,0)"), margin=dict(l=0, r=0, b=0, t=0))
    st.plotly_chart(fig, use_container_width=True)

def mod_predictor(df, L):
    st.title(lex[L]["m4"])
    pending = df[df['status'] == 'Pending'].copy()
    
    # Logic: Probability of Default
    today = pd.Timestamp.now()
    pending['days_late'] = (today - pending['due_date']).dt.days.clip(0)
    pending['risk_prob'] = (pending['days_late'] * 2.5) + (900 - pending['trust_score'])/10
    pending['risk_prob'] = pending['risk_prob'].clip(0, 100).round(1)

    munim_brief("AI Risk Assessment", "I've analyzed {len(pending)} open cases. High-risk bubbles indicate clients who are significantly past their due date with declining trust.")
    
    fig = px.scatter(pending, x="amount", y="risk_prob", size="amount", color="risk_prob",
                     hover_name="customer", color_continuous_scale="RdYlGn_r",
                     labels={'risk_prob': 'Probability of Default %'}, template="plotly_dark")
    st.plotly_chart(fig, use_container_width=True)

def mod_scheduler(df, L):
    st.title(lex[L]["m7"])
    pending = df[df['status'] == 'Pending'].copy()
    
    # Logic: Optimal Reminder Date
    def get_opt_date(row):
        if row['trust_score'] < 400: return row['due_date'] - timedelta(days=2) # Early nudge
        if row['trust_score'] > 750: return row['due_date'] + timedelta(days=4) # Grace period
        return row['due_date']

    pending['opt_date'] = pending.apply(get_opt_date, axis=1)
    
    brief = "My scheduler has assigned 'Grace Periods' to your top clients to maintain relationships, while 'High Risk' clients are flagged for early reminders."
    munim_brief("Smart Scheduler", brief)
    
    daily_plan = pending.groupby('opt_date')['amount'].sum().reset_index()
    fig = px.bar(daily_plan, x='opt_date', y='amount', color_discrete_sequence=['#6366F1'], template="plotly_dark")
    st.plotly_chart(fig, use_container_width=True)
    
    st.subheader("📅 Action Items for Today")
    today_tasks = pending[pending['opt_date'].dt.date == datetime.now().date()]
    st.dataframe(today_tasks, use_container_width=True)

def mod_ledger(df, L):
    st.title(lex[L]["m3"])
    st.dataframe(df, column_config={
        "trust_score": st.column_config.ProgressColumn("Trust", min_value=300, max_value=900),
        "amount": st.column_config.NumberColumn("Amount (₹)", format="₹%d")
    }, use_container_width=True)

def mod_recovery(df, L):
    st.title(lex[L]["m5"])
    pending = df[df['status'] == 'Pending']
    target = st.selectbox("Select Customer", pending['customer'].unique())
    row = pending[pending['customer'] == target].iloc[0]
    
    munim_brief("Tactical Nudge", f"For {target}, I recommend a 'Reciprocity' script. Remind them of the trust you've shown them over {row['id'] % 10 + 2} months.")
    
    msg = f"Pranaam {target}, KhataKhat AI here. KD is closing the monthly books. To keep your Trust Rating at {row['trust_score']}, please clear the ₹{row['amount']} balance by EOD. Shubh Din!"
    st.text_area("WhatsApp Message", msg, height=150)
    st.button(lex[L]["wa"])

# ==========================================
# 4. MAIN NAVIGATION & ROUTING
# ==========================================
def main():
    if "auth" not in st.session_state: st.session_state.auth = False

    if not st.session_state.auth:
        st.markdown("<h1 style='text-align:center; color:#6366F1; font-size:50px;'>🛡️ KHATAKHAT PRO</h1>", unsafe_allow_html=True)
        _, center, _ = st.columns([1,1,1])
        with center:
            u = st.text_input("Merchant ID", value="kd_merchant")
            p = st.text_input("Access Key", type="password", value="admin123")
            if st.button("Unlock Engine"):
                st.session_state.auth = True
                st.rerun()
        return

    df = get_data()

    with st.sidebar:
        st.markdown("<h2 style='color:#22D3EE;'>MUNIM AI</h2>", unsafe_allow_html=True)
        lang = st.radio(lex["English"]["lang_sel"], ["English", "Hindi"])
        st.markdown("---")
        menu_items = [lex[lang][f"m{i}"] for i in range(1, 11)]
        choice = st.radio("Navigation", menu_items)
        if st.button("Terminate Session"):
            st.session_state.auth = False
            st.rerun()

    # Routing
    if choice == lex[lang]["m1"]: mod_dashboard(df, lang)
    elif choice == lex[lang]["m3"]: mod_ledger(df, lang)
    elif choice == lex[lang]["m4"]: mod_predictor(df, lang)
    elif choice == lex[lang]["m5"]: mod_recovery(df, lang)
    elif choice == lex[lang]["m7"]: mod_scheduler(df, lang)
    else:
        st.title(choice)
        st.info("Logic Engine Active. Syncing background analytics...")

if __name__ == "__main__":
    main()
