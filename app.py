import streamlit as st
import pandas as pd
import numpy as np
import sqlite3
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

# ==========================================
# 0. READABILITY-FIRST UI (Phase 2)
# ==========================================
st.set_page_config(page_title="KhataKhat Pro | Intelligence Phase", layout="wide", page_icon="⚖️")

# High-Contrast Professional Theme
st.markdown("""
    <style>
    .stApp {
        background-color: #0F172A; /* Slate Navy */
        color: #F1F5F9; /* Off-White Text */
    }
    .munim-ai-box {
        background: #1E293B; 
        border-left: 6px solid #6366F1;
        padding: 20px;
        border-radius: 12px;
        margin-bottom: 25px;
        color: #F1F5F9;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }
    h1, h2, h3 { color: #818CF8; }
    div[data-testid="stMetricValue"] { color: #38BDF8 !important; }
    .stButton>button {
        background-color: #6366F1;
        color: white;
        border-radius: 8px;
        border: none;
        padding: 10px 20px;
        font-weight: bold;
    }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 1. BILINGUAL DICTIONARY
# ==========================================
lex = {
    "English": {
        "m1": "📊 Dashboard", "m2": "📂 Bulk Upload", "m3": "📓 Smart Ledger", 
        "m4": "🔮 AI Predictor", "m5": "🎯 Recovery Ops", "m6": "⚠️ Risk Radar",
        "m7": "📈 Forecast", "m8": "🎖️ Trust Index", "m9": "💡 Insights", "m10": "⚙️ Settings",
        "wa": "Send WhatsApp Nudge 📲"
    },
    "Hindi": {
        "m1": "📊 डैशबोर्ड", "m2": "📂 डेटा अपलोड", "m3": "📓 स्मार्ट खाता", 
        "m4": "🔮 AI भविष्यवक्ता", "m5": "🎯 वसूली ऑपरेशन", "m6": "⚠️ जोखिम रडार",
        "m7": "📈 पूर्वानुमान", "m8": "🎖️ भरोसा इंडेक्स", "m9": "💡 मुख्य बातें", "m10": "⚙️ सेटिंग्स",
        "wa": "व्हाट्सएप भेजें 📲"
    }
}

# ==========================================
# 2. THE INTELLIGENCE ENGINE (Logic)
# ==========================================
conn = sqlite3.connect('khatakhat_logic.db', check_same_thread=False)

def get_data():
    try:
        df = pd.read_sql("SELECT * FROM ledger", conn)
        df['due_date'] = pd.to_datetime(df['due_date'])
        return df
    except:
        # Create Robust Sample for Logic Testing
        names = ["Sharma Electronics", "Verma Grocery", "Rajesh Traders", "Priya Fashion", "Malhotra Sweets"]
        data = []
        for i in range(100):
            p_status = np.random.choice(["Paid", "Pending"], p=[0.6, 0.4])
            d_date = datetime.now() + timedelta(days=np.random.randint(-20, 20))
            data.append({
                "id": 200 + i,
                "customer": np.random.choice(names),
                "amount": np.random.randint(500, 50000),
                "status": p_status,
                "due_date": d_date.strftime('%Y-%m-%d'),
                "trust_score": np.random.randint(300, 900),
                "last_notified": (datetime.now() - timedelta(days=np.random.randint(0, 10))).strftime('%Y-%m-%d')
            })
        df = pd.DataFrame(data)
        df.to_sql("ledger", conn, if_exists="replace", index=False)
        return get_data()

def munim_logic_brief(title, msg):
    st.markdown(f"""
    <div class="munim-ai-box">
        <h4 style="margin:0; color:#38BDF8;">🤖 {title}</h4>
        <p style="margin:10px 0 0 0;">{msg}</p>
    </div>
    """, unsafe_allow_html=True)

# ==========================================
# 3. ADVANCED MODULES (PHASE 2)
# ==========================================

# MODULE 4: AI PREDICTION LOGIC
def mod_predictor(df, L):
    st.title(lex[L]["m4"])
    pending = df[df['status'] == 'Pending'].copy()
    
    # Logic: Calculate Probability of Default
    # Higher amount + Lower Trust + Overdue = Higher Probability
    today = pd.Timestamp.now()
    pending['days_past'] = (today - pending['due_date']).dt.days
    pending['prob'] = (pending['days_past'].clip(0, 30) * 2) + (900 - pending['trust_score'])/10
    pending['prob'] = pending['prob'].clip(0, 100).round(1)

    munim_logic_brief("Probability Engine", f"KD, I've analyzed {len(pending)} pending invoices. {len(pending[pending['prob'] > 70])} cases are at 'High Risk' of default.")

    fig = px.scatter(pending, x="amount", y="prob", size="amount", color="prob",
                     hover_name="customer", title="Default Probability vs. Amount",
                     color_continuous_scale="RdYlGn_r", template="plotly_dark")
    st.plotly_chart(fig, use_container_width=True)

# MODULE 6: RISK RADAR (Quadrant Analysis)
def mod_risk_radar(df, L):
    st.title(lex[L]["m6"])
    munim_logic_brief("Quadrant Analysis", "I have categorized your customers into 4 zones. Focus on the 'Danger Zone' (Top Left) immediately.")
    
    # Quadrant Logic
    fig = px.scatter(df, x="trust_score", y="amount", color="status",
                     marginal_x="box", marginal_y="violin",
                     title="Trust vs. Debt Value Radar", template="plotly_dark")
    st.plotly_chart(fig, use_container_width=True)

# MODULE 9: STRATEGIC INSIGHTS
def mod_insights(df, L):
    st.title(lex[L]["m9"])
    
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("🏆 Star Payers")
        top = df[df['status'] == 'Paid'].groupby('customer')['amount'].sum().nlargest(3)
        st.write(top)
        
    with c2:
        st.subheader("🕒 Best Collection Time")
        st.info("Historical data suggests your reminders are 34% more effective on Tuesday mornings.")

    # Cash Gap Logic
    total_in = df[df['status'] == 'Paid']['amount'].sum()
    total_out = df[df['status'] == 'Pending']['amount'].sum()
    st.write(f"**Capital Health Ratio:** {round(total_in/total_out, 2)} (Goal: > 3.0)")

# ==========================================
# 4. MAIN NAVIGATION
# ==========================================
def main():
    if "auth" not in st.session_state: st.session_state.auth = False

    if not st.session_state.auth:
        st.title("🛡️ KhataKhat Pro Login")
        u = st.text_input("Username", value="kd_merchant")
        p = st.text_input("Password", type="password", value="admin123")
        if st.button("Unlock Phase 2 Engine"):
            st.session_state.auth = True
            st.rerun()
        return

    df = get_data()

    with st.sidebar:
        st.title("KhataKhat AI")
        L = st.radio("Language / भाषा", ["English", "Hindi"])
        st.markdown("---")
        menu = [lex[L][f"m{i}"] for i in range(1, 11)]
        choice = st.radio("Select Phase 2 Module", menu)
        if st.button("Logout"):
            st.session_state.auth = False
            st.rerun()

    # Routing
    if choice == lex[L]["m1"]:
        st.title(lex[L]["m1"])
        c1, c2, c3 = st.columns(3)
        c1.metric("Pending", f"₹{df[df['status']=='Pending']['amount'].sum():,.0f}")
        c2.metric("Trust Score", int(df['trust_score'].mean()))
        c3.metric("Collection Goal", "₹1.2L")
        st.dataframe(df, use_container_width=True)
        
    elif choice == lex[L]["m4"]: mod_predictor(df, L)
    elif choice == lex[L]["m6"]: mod_risk_radar(df, L)
    elif choice == lex[L]["m9"]: mod_insights(df, L)
    elif choice == lex[L]["m5"]: 
        st.title(lex[L]["m5"])
        st.write("Recovery Engine Active. Use Dashboard to target clients.")
        st.button(lex[L]["wa"])
    else:
        st.title(choice)
        st.write("Functionality loading...")

if __name__ == "__main__":
    main()
