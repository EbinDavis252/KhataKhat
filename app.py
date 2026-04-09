import streamlit as st
import pandas as pd
import numpy as np
import sqlite3
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import urllib.parse

# ==========================================
# 0. THE "JAW-DROPPING" UI ENGINE
# ==========================================
st.set_page_config(page_title="KhataKhat Ultra | AI Command", layout="wide", page_icon="🧿")

# Advanced CSS: Glassmorphism + Neon Aura
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&family=Inter:wght@300;400;600&display=swap');

    .stApp {
        background: radial-gradient(circle at 20% 30%, #0D1117 0%, #010409 100%);
        color: #E6EDF3;
        font-family: 'Inter', sans-serif;
    }

    /* Glassmorphism Card */
    .glass-card {
        background: rgba(255, 255, 255, 0.03);
        backdrop-filter: blur(15px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 20px;
        padding: 30px;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.8);
        margin-bottom: 25px;
        transition: 0.4s ease;
    }
    .glass-card:hover {
        border: 1px solid #00D4FF;
        box-shadow: 0 0 25px rgba(0, 212, 255, 0.3);
    }

    /* Holographic AI Munim */
    .munim-hologram {
        background: linear-gradient(135deg, rgba(0, 212, 255, 0.1) 0%, rgba(186, 1, 255, 0.1) 100%);
        border-left: 5px solid #00D4FF;
        border-right: 5px solid #BA01FF;
        padding: 25px;
        border-radius: 15px;
        animation: breathe 4s infinite ease-in-out;
    }

    @keyframes breathe {
        0% { box-shadow: 0 0 10px rgba(0, 212, 255, 0.2); }
        50% { box-shadow: 0 0 30px rgba(186, 1, 255, 0.4); }
        100% { box-shadow: 0 0 10px rgba(0, 212, 255, 0.2); }
    }

    /* Metrics with Glow */
    div[data-testid="stMetricValue"] {
        font-family: 'Orbitron', sans-serif;
        color: #00D4FF !important;
        text-shadow: 0 0 15px rgba(0, 212, 255, 0.6);
        font-size: 2.5rem !important;
    }

    /* Neon Buttons */
    .stButton>button {
        background: linear-gradient(90deg, #00D4FF, #BA01FF);
        border: none; color: white; border-radius: 50px;
        padding: 12px 30px; font-weight: 700; font-family: 'Orbitron';
        letter-spacing: 1px; transition: 0.5s;
    }
    .stButton>button:hover {
        transform: translateY(-3px);
        box-shadow: 0 10px 20px rgba(186, 1, 255, 0.5);
    }

    /* Clean Sidebar */
    section[data-testid="stSidebar"] {
        background-color: rgba(1, 4, 9, 0.95) !important;
        border-right: 1px solid rgba(255, 255, 255, 0.05);
    }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 1. BILINGUAL DICTIONARY
# ==========================================
strings = {
    "English": {
        "m1": "📊 Executive Hub", "m3": "📓 Digital Khata", "m5": "🎯 Recovery Ops", "m7": "📈 Capital Forecast",
        "m6": "⚠️ Risk Radar", "m4": "🔮 AI Predictor", "m8": "🎖️ Trust Index",
        "m9": "💡 Insights", "m2": "📂 Upload", "m10": "⚙️ Config",
        "munim": "Munim AI Assistant", "pending": "Capital Outflow", "wa": "Launch WhatsApp Nudge 🚀"
    },
    "Hindi": {
        "m1": "📊 मुख्य केंद्र", "m3": "📓 डिजिटल खाता", "m5": "🎯 वसूली ऑपरेशन", "m7": "📈 आने वाला पैसा",
        "m6": "⚠️ जोखिम रडार", "m4": "🔮 AI भविष्यवक्ता", "m8": "🎖️ भरोसा स्कोर",
        "m9": "💡 मुख्य बातें", "m2": "📂 अपलोड", "m10": "⚙️ सेटिंग्स",
        "munim": "मुनीम AI सहायक", "pending": "कुल बकाया उधार", "wa": "व्हाट्सएप संदेश भेजें 🚀"
    }
}

# ==========================================
# 2. DATA CORE
# ==========================================
conn = sqlite3.connect('khatakhat_ultra.db', check_same_thread=False)

def get_data():
    try:
        df = pd.read_sql("SELECT * FROM ledger", conn)
        df['due_date'] = pd.to_datetime(df['due_date'])
        return df
    except:
        names = ["Sharma Electronics", "Verma Ji", "Royal Traders", "Modern Retail", "Global Mart", "Arora Sweets"]
        data = []
        for i in range(80):
            status = np.random.choice(["Paid", "Pending"], p=[0.7, 0.3])
            data.append({
                "id": 1000 + i,
                "customer": np.random.choice(names),
                "phone": "919876543210",
                "amount": np.random.randint(500, 85000),
                "status": status,
                "due_date": (datetime.now() + timedelta(days=np.random.randint(-25, 25))).strftime('%Y-%m-%d'),
                "trust_score": np.random.randint(300, 900)
            })
        df = pd.DataFrame(data)
        df.to_sql("ledger", conn, if_exists="replace", index=False)
        return get_data()

# ==========================================
# 3. AI MUNIM HOLOGRAPHIC BRIEF
# ==========================================
def render_munim_brief(title, msg, lang):
    st.markdown(f"""
    <div class="munim-hologram">
        <h4 style="margin:0; color:#00D4FF; font-family:'Orbitron';">✨ {title}</h4>
        <p style="margin-top:10px; color:#A9B2C3; font-size:16px;">{msg}</p>
    </div>
    """, unsafe_allow_html=True)

# ==========================================
# 4. MODULES
# ==========================================

def mod_dashboard(df, l):
    st.markdown(f"<h1 style='font-family:Orbitron;'>{strings[l]['m1']}</h1>", unsafe_allow_html=True)
    pending = df[df['status'] == 'Pending']
    
    brief = f"KD, we have detected ₹{pending['amount'].sum():,.0f} in high-risk zones. The AI Munim has identified 3 clients with declining trust scores. Action is required." if l == "English" else \
            f"KD, हमने ₹{pending['amount'].sum():,.0f} को जोखिम क्षेत्र में पाया है। मुनीम ने 3 ऐसे ग्राहकों की पहचान की है जिनका भरोसा स्कोर गिर रहा है।"
    
    render_munim_brief(strings[l]["munim"], brief, l)

    c1, c2, c3 = st.columns(3)
    with c1: st.metric(strings[l]["pending"], f"₹{pending['amount'].sum():,.0f}")
    with c2: st.metric("Active Cases", len(pending))
    with c3: st.metric("Market Sentiment", "Bullish" if df['trust_score'].mean() > 600 else "Bearish")

    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.subheader("🌐 3D Risk Topography")
    fig = px.scatter_3d(df, x='amount', y='trust_score', z='status', color='status',
                        color_discrete_map={'Pending': '#BA01FF', 'Paid': '#00D4FF'},
                        opacity=0.8, template="plotly_dark")
    fig.update_layout(scene=dict(bgcolor="rgba(0,0,0,0)"), margin=dict(l=0, r=0, b=0, t=0))
    st.plotly_chart(fig, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

def mod_recovery(df, l):
    st.title(strings[l]["m5"])
    pending = df[df['status'] == 'Pending']
    
    col1, col2 = st.columns([1, 1.2])
    with col1:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        target = st.selectbox("Select Debtor", pending['customer'].unique())
        client = pending[pending['customer'] == target].iloc[0]
        st.write(f"### Debt: ₹{client['amount']:,.0f}")
        st.progress(client['trust_score']/900, text=f"Trust Score: {client['trust_score']}")
        st.markdown('</div>', unsafe_allow_html=True)
        
    with col2:
        brief = f"Munim suggests a 'Loss Aversion' strategy for {target}. Frame the message around losing their Gold-tier status." if l == "English" else \
                f"मुनीम {target} के लिए 'नुकसान से बचाव' की रणनीति का सुझाव देते हैं।"
        render_munim_brief("Strategic Recovery", brief, l)
        msg = f"Pranaam {target}, KhataKhat AI Assistant here. KD is finalizing the audit. To prevent a drop in your {client['trust_score']} Trust Score, please settle the ₹{client['amount']} balance today."
        st.text_area("AI Drafted Script", msg, height=150)
        st.button(strings[l]["wa"])

def mod_ledger(df, l):
    st.title(strings[l]["m3"])
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.dataframe(df, column_config={
        "trust_score": st.column_config.ProgressColumn("Trust Index", min_value=300, max_value=900),
        "amount": st.column_config.NumberColumn("Amount (₹)", format="₹%d")
    }, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

# ==========================================
# 5. AUTH & MAIN
# ==========================================
def main():
    if "auth" not in st.session_state: st.session_state.auth = False

    if not st.session_state.auth:
        st.markdown("<h1 style='text-align:center; font-family:Orbitron; color:#00D4FF; font-size:60px; margin-top:100px;'>KHATAKHAT ULTRA</h1>", unsafe_allow_html=True)
        st.markdown("<p style='text-align:center; color:#BA01FF; letter-spacing:3px;'>AI-POWERED RECOVERY ENGINE</p>", unsafe_allow_html=True)
        
        _, center, _ = st.columns([1, 0.8, 1])
        with center:
            st.markdown('<div class="glass-card">', unsafe_allow_html=True)
            u = st.text_input("Merchant ID", value="kd_merchant")
            p = st.text_input("Access Key", type="password", value="admin123")
            if st.button("Initialize Command Center"):
                st.session_state.auth = True
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
        return

    df = get_data()

    # Sidebar
    with st.sidebar:
        st.markdown("<h2 style='font-family:Orbitron; color:#00D4FF;'>MUNIM AI</h2>", unsafe_allow_html=True)
        lang = st.radio("System Language", ["English", "Hindi"])
        st.markdown("---")
        menu = [strings[lang][f"m{i}"] for i in [1, 3, 5, 7, 6, 4, 8, 9, 2, 10]]
        choice = st.radio("Navigation", menu)
        if st.button("Terminate Session"):
            st.session_state.auth = False
            st.rerun()

    # Routing
    if choice == strings[lang]["m1"]: mod_dashboard(df, lang)
    elif choice == strings[lang]["m3"]: mod_ledger(df, lang)
    elif choice == strings[lang]["m5"]: mod_recovery(df, lang)
    else:
        st.title(choice)
        st.info("Module active. Real-time background sync in progress...")

if __name__ == "__main__":
    main()
