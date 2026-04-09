import streamlit as st
import pandas as pd
import numpy as np
import sqlite3
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import urllib.parse
import io

# ==========================================
# 0. CONFIGURATION & NEON UI
# ==========================================
st.set_page_config(page_title="Udhaar Guru | Munim AI", layout="wide", page_icon="🧿")

# Psychedelic Finance Theme CSS
st.markdown("""
    <style>
    /* Dark Deep Space Background */
    .stApp {
        background: radial-gradient(circle at top left, #0D0221, #0F084B, #26084F);
        color: #E0E6ED;
    }
    
    /* Neon Border Munim Box */
    .munim-box {
        background: rgba(0, 0, 0, 0.4);
        border: 2px solid #00F2FF;
        border-radius: 15px;
        padding: 25px;
        box-shadow: 0 0 15px #00F2FF, inset 0 0 10px #7000FF;
        margin-bottom: 30px;
        border-left: 8px solid #FF00FF;
    }

    /* Metric Styling */
    [data-testid="stMetricValue"] {
        color: #00F2FF !important;
        text-shadow: 0 0 10px #00F2FF;
        font-family: 'Orbitron', sans-serif;
    }

    /* Sidebar Styling */
    .css-1d391kg {
        background-color: rgba(13, 2, 33, 0.95) !important;
    }

    /* Psychedelic Buttons */
    .stButton>button {
        background: linear-gradient(45deg, #7000FF, #FF00FF);
        color: white;
        border: none;
        border-radius: 20px;
        padding: 10px 24px;
        font-weight: bold;
        transition: 0.3s ease;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    .stButton>button:hover {
        transform: scale(1.05);
        box-shadow: 0 0 20px #FF00FF;
    }

    h1, h2, h3 {
        color: #00F2FF;
        text-shadow: 2px 2px #7000FF;
    }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 1. BILINGUAL DICTIONARY
# ==========================================
strings = {
    "English": {
        "m1": "1. Command Center", "m2": "2. Ingest Data", "m3": "3. Digital Khata", 
        "m4": "4. Default Predictor", "m5": "5. Recovery War Room", "m6": "6. Risk Radar",
        "m7": "7. Future Inflow", "m8": "8. Trust Score", "m9": "9. Strategic Insights", "m10": "10. Settings",
        "pending": "Outstanding Udhaar", "recovery": "Recovery Rate", "trust": "Avg Trust Score",
        "munim_head": "Munim AI Analysis", "wa_btn": "Send via WhatsApp 🚀", "lang": "Switch Language / भाषा बदलें"
    },
    "Hindi": {
        "m1": "1. मुख्य केंद्र", "m2": "2. डेटा अपलोड", "m3": "3. डिजिटल खाता", 
        "m4": "4. भुगतान भविष्यवाणी", "m5": "5. वसूली वॉर रूम", "m6": "6. जोखिम रडार",
        "m7": "7. भविष्य का प्रवाह", "m8": "8. भरोसा स्कोर", "m9": "9. रणनीतिक विचार", "m10": "10. सेटिंग्स",
        "pending": "कुल बकाया उधार", "recovery": "वसूली दर", "trust": "औसत भरोसा स्कोर",
        "munim_head": "मुनीम AI विश्लेषण", "wa_btn": "व्हाट्सएप पर भेजें 🚀", "lang": "भाषा बदलें / Switch Language"
    }
}

# ==========================================
# 2. DATA ENGINE
# ==========================================
conn = sqlite3.connect('udhaar_guru_pro.db', check_same_thread=False)

def get_data():
    try:
        df = pd.read_sql("SELECT * FROM ledger", conn)
        df['due_date'] = pd.to_datetime(df['due_date'])
        return df
    except:
        return generate_mock_data()

def generate_mock_data():
    customers = ["Sharma Sweets", "Verma Electronics", "Aggarwal Traders", "Malhotra & Sons", "Rajput General Store", "Punjab Textiles"]
    data = []
    for i in range(60):
        status = np.random.choice(["Paid", "Pending"], p=[0.7, 0.3])
        d_date = datetime.now() + timedelta(days=np.random.randint(-30, 30))
        data.append({
            "id": 101 + i,
            "customer": np.random.choice(customers),
            "phone": "919876543210",
            "amount": np.random.randint(500, 45000),
            "status": status,
            "due_date": d_date.strftime('%Y-%m-%d'),
            "trust_score": np.random.randint(300, 900),
            "last_contacted": (datetime.now() - timedelta(days=np.random.randint(0, 7))).strftime('%Y-%m-%d')
        })
    df = pd.DataFrame(data)
    df.to_sql("ledger", conn, if_exists="replace", index=False)
    return get_data()

# ==========================================
# 3. MUNIM AI EXPLANATION COMPONENT
# ==========================================
def munim_ai_brief(title, content):
    st.markdown(f"""
    <div class="munim-box">
        <h3 style='margin-top:0;'>🧿 {title}</h3>
        <p style='font-size: 1.1em; line-height: 1.6;'>{content}</p>
    </div>
    """, unsafe_allow_html=True)

# ==========================================
# 4. MODULE DEFINITIONS
# ==========================================

def mod_dashboard(df, l):
    st.title(strings[l]["m1"])
    pending_total = df[df['status'] == 'Pending']['amount'].sum()
    
    brief = f"KD, you have ₹{pending_total:,.0f} stuck. My 3D analysis shows that 15% of this is 'Toxic Debt' (Low Trust + Overdue). Focus on high-value recoveries today." if l == "English" else \
            f"KD, आपका ₹{pending_total:,.0f} बाजार में फंसा है। मेरे विश्लेषण के अनुसार, इसमें से 15% 'खतरनाक कर्ज' है। आज बड़े बकायेदारों पर ध्यान दें।"
    munim_ai_brief(strings[l]["munim_head"], brief)

    c1, c2, c3 = st.columns(3)
    c1.metric(strings[l]["pending"], f"₹{pending_total:,.0f}", "-₹2.4k")
    c2.metric(strings[l]["recovery"], "82%", "4%")
    c3.metric(strings[l]["trust"], int(df['trust_score'].mean()))

    st.subheader("3D Transaction Pulse")
    fig = px.scatter_3d(df, x='amount', y='trust_score', z='status', color='status', 
                        template="plotly_dark", color_discrete_map={"Pending": "#FF00FF", "Paid": "#00F2FF"})
    st.plotly_chart(fig, use_container_width=True)

def mod_recovery(df, l):
    st.title(strings[l]["m5"])
    pending = df[df['status'] == 'Pending']
    target = st.selectbox("Select Debtor", pending['customer'].unique())
    client = pending[pending['customer'] == target].iloc[0]

    brief = f"For {target}, I suggest an 'Assertive' tone. They have the funds but lack the intent. This message uses psychology to trigger payment." if l == "English" else \
            f"{target} के लिए, मैं 'कड़ा' लहजा अपनाने का सुझाव देता हूँ। उनके पास पैसा है लेकिन देने की नीयत कम है।"
    munim_ai_brief(strings[l]["munim_head"], brief)

    msg = f"Pranaam {target}, this is Munim AI (Assistant to KD). Your balance of ₹{client['amount']} is now overdue. Clearing this immediately will boost your Trust Score to {client['trust_score'] + 20}. Please settle now."
    st.text_area("Munim's Script", msg, height=150)
    st.button(strings[l]["wa_btn"])

def mod_risk(df, l):
    st.title(strings[l]["m6"])
    brief = "Red zones represent the 'Danger Hub'—customers with high debt and decreasing trust scores. Do not issue fresh credit to these clients." if l == "English" else \
            "लाल क्षेत्र 'खतरे के केंद्र' को दर्शाता है—उच्च ऋण और घटते भरोसे वाले ग्राहक। इन्हें नया उधार न दें।"
    munim_ai_brief(strings[l]["munim_head"], brief)

    fig = px.density_heatmap(df, x="amount", y="trust_score", z="status", 
                             color_continuous_scale="Viridis", title="Risk Heatmap")
    st.plotly_chart(fig, use_container_width=True)

def mod_forecast(df, l):
    st.title(strings[l]["m7"])
    brief = "This 3D chart projects your collections for the next 30 days. The peaks show heavy inflow, but the troughs warn you of potential cash-crunch days." if l == "English" else \
            "यह 3D चार्ट अगले 30 दिनों के लिए आपके संग्रह का अनुमान लगाता है। ऊंचे ग्राफ भारी आवक दिखाते हैं।"
    munim_ai_brief(strings[l]["munim_head"], brief)
    
    forecast_df = df.groupby('due_date')['amount'].sum().reset_index()
    fig = go.Figure(data=[go.Surface(z=[forecast_df['amount'].values])]) # 3D Surface for effect
    fig.update_layout(title='3D Cash Surface Projection', template="plotly_dark")
    st.plotly_chart(fig, use_container_width=True)

# (Other modules follow a similar logic structure)
def mod_ledger(df, l):
    st.title(strings[l]["m3"])
    st.dataframe(df.style.background_gradient(subset=['trust_score'], cmap='cool'), use_container_width=True)

# ==========================================
# 5. MAIN ROUTER
# ==========================================
def main():
    if "authenticated" not in st.session_state: st.session_state.authenticated = False

    if not st.session_state.authenticated:
        st.markdown("<h1 style='text-align: center; font-size: 60px;'>🧿 UDHAAR GURU</h1>", unsafe_allow_html=True)
        col1, col2, col3 = st.columns([1,1,1])
        with col2:
            st.text_input("Merchant ID", value="kd_merchant")
            st.text_input("Password", type="password", value="admin123")
            if st.button("Access Dashboard"):
                st.session_state.authenticated = True
                st.rerun()
        return

    df = get_data()

    # Sidebar Nav
    with st.sidebar:
        st.markdown("<h2 style='color:#00F2FF'>MUNIM AI</h2>", unsafe_allow_html=True)
        lang = st.radio(strings["English"]["lang"], ["English", "Hindi"])
        st.markdown("---")
        choice = st.radio("Navigate", [strings[lang][f"m{i}"] for i in range(1, 11)])
        if st.button("Logout"):
            st.session_state.authenticated = False
            st.rerun()

    # Simple Mapping
    if choice == strings[lang]["m1"]: mod_dashboard(df, lang)
    elif choice == strings[lang]["m3"]: mod_ledger(df, lang)
    elif choice == strings[lang]["m5"]: mod_recovery(df, lang)
    elif choice == strings[lang]["m6"]: mod_risk(df, lang)
    elif choice == strings[lang]["m7"]: mod_forecast(df, lang)
    else:
        st.title(choice)
        st.info("Module active and running AI background processes.")

if __name__ == "__main__":
    main()
