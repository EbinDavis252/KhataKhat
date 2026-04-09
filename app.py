import streamlit as st
import pandas as pd
import numpy as np
import sqlite3
import plotly.express as px
import time

from datetime import datetime, timedelta
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LinearRegression

# =========================================
# PAGE CONFIG
# =========================================
st.set_page_config(
    page_title="Khatakhat AI",
    layout="wide",
)

# =========================================
# FINTECH UI THEME
# =========================================
st.markdown("""
<style>

/* ===== GLOBAL BACKGROUND ===== */

.stApp{
background: linear-gradient(135deg,#020617,#0f172a,#020617);
color:#E2E8F0;
}

/* GRID EFFECT */

.stApp::before{
content:"";
position:fixed;
top:0;
left:0;
width:100%;
height:100%;
background-image:
linear-gradient(rgba(255,255,255,0.04) 1px, transparent 1px),
linear-gradient(90deg, rgba(255,255,255,0.04) 1px, transparent 1px);
background-size:50px 50px;
pointer-events:none;
z-index:-1;
}

/* HEADINGS */

h1,h2,h3{
font-family:monospace;
color:#1DE9B6;
}

/* METRICS */

div[data-testid="stMetricValue"]{
font-size:36px;
font-family:monospace;
color:white;
}

/* BUTTONS */

.stButton>button{
background:transparent;
border:1px solid #1DE9B6;
color:#1DE9B6;
height:3em;
border-radius:5px;
}

.stButton>button:hover{
background:#1DE9B6;
color:black;
box-shadow:0 0 10px #1DE9B6;
}

/* SIDEBAR */

section[data-testid="stSidebar"]{
background:#020617;
}

/* TABLE */

.stDataFrame{
border:1px solid #1DE9B6;
}

</style>
""", unsafe_allow_html=True)

# =========================================
# DATABASE
# =========================================
conn = sqlite3.connect("khatakhat_ai.db", check_same_thread=False)

conn.execute("""
CREATE TABLE IF NOT EXISTS ledger(
customer TEXT,
amount REAL,
status TEXT,
due_date TEXT,
trust_score INTEGER
)
""")

# =========================================
# DATA FUNCTIONS
# =========================================

def get_data():

    try:
        df = pd.read_sql("SELECT * FROM ledger", conn)

        if not df.empty:
            df["due_date"] = pd.to_datetime(df["due_date"])

        return df

    except:
        return pd.DataFrame()


def persist_data(df):

    df.columns = [c.lower().replace(" ", "_") for c in df.columns]

    mapping = {
        "customer_name": "customer",
        "payment_status": "status"
    }

    df = df.rename(columns=mapping)

    df.to_sql("ledger", conn, if_exists="replace", index=False)

# =========================================
# SAMPLE DATA
# =========================================

def generate_sample():

    customers = [
        "Alpha Traders",
        "Matrix Retail",
        "Zenith Logistics",
        "Global Hardware",
        "Vision Electronics"
    ]

    rows = []

    for i in range(150):

        status = np.random.choice(["Paid", "Pending"], p=[0.65,0.35])

        rows.append({

            "customer":np.random.choice(customers),

            "amount":np.random.randint(2000,100000),

            "status":status,

            "due_date":(datetime.now()+timedelta(days=np.random.randint(-30,30))).strftime("%Y-%m-%d"),

            "trust_score":np.random.randint(300,900)

        })

    df = pd.DataFrame(rows)

    persist_data(df)

    return df


# =========================================
# AI MODEL
# =========================================

def train_model(df):

    model_df = df.copy()

    model_df["status"] = model_df["status"].str.lower()

    model_df["target"] = model_df["status"].apply(lambda x:1 if x=="pending" else 0)

    X = model_df[["amount","trust_score"]]

    y = model_df["target"]

    X_train,X_test,y_train,y_test = train_test_split(X,y,test_size=0.2)

    model = RandomForestClassifier()

    model.fit(X_train,y_train)

    return model


# =========================================
# CASHFLOW FORECAST
# =========================================

def forecast_cashflow(df):

    df["due_date"] = pd.to_datetime(df["due_date"])

    pending = df[df["status"]=="Pending"]

    if pending.empty:
        return pd.DataFrame()

    grouped = pending.groupby("due_date")["amount"].sum().reset_index()

    grouped["days"] = (grouped["due_date"]-grouped["due_date"].min()).dt.days

    model = LinearRegression()

    model.fit(grouped[["days"]], grouped["amount"])

    future = np.arange(grouped["days"].max()+1, grouped["days"].max()+15)

    preds = model.predict(future.reshape(-1,1))

    forecast = pd.DataFrame({

        "days":future,
        "predicted_cashflow":preds

    })

    return forecast


# =========================================
# DASHBOARD
# =========================================

def dashboard(df):

    st.title("KHATAKHAT AI COMMAND CENTER")

    if df.empty:
        st.warning("NO DATA")
        return

    pending = df[df["status"]=="Pending"]

    paid = df[df["status"]=="Paid"]

    total_pending = pending["amount"].sum()

    total_paid = paid["amount"].sum()

    health = (total_paid/(total_pending+total_paid))*100

    c1,c2,c3,c4 = st.columns(4)

    c1.metric("OUTSTANDING CREDIT",f"₹{total_pending:,.0f}")

    c2.metric("CAPITAL HEALTH",f"{health:.1f}%")

    c3.metric("AVG TRUST SCORE",int(df["trust_score"].mean()))

    c4.metric("TOTAL CUSTOMERS",df["customer"].nunique())

    st.subheader("3D CREDIT TOPOGRAPHY")

    fig = px.scatter_3d(
        df,
        x="amount",
        y="trust_score",
        z="status",
        color="status",
        template="plotly_dark"
    )

    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)"
    )

    st.plotly_chart(fig,use_container_width=True)

    st.subheader("AI CASHFLOW FORECAST")

    forecast = forecast_cashflow(df)

    if not forecast.empty:

        fig2 = px.line(
            forecast,
            x="days",
            y="predicted_cashflow",
            template="plotly_dark"
        )

        st.plotly_chart(fig2,use_container_width=True)


# =========================================
# UPLOAD MODULE
# =========================================

def upload():

    st.title("UPLOAD LEDGER DATA")

    file = st.file_uploader("Upload CSV or Excel",type=["csv","xlsx"])

    if file:

        if file.name.endswith("csv"):
            df = pd.read_csv(file)

        else:
            df = pd.read_excel(file)

        st.dataframe(df)

        if st.button("SAVE DATA"):
            persist_data(df)
            st.success("Data Stored")


# =========================================
# RISK PREDICTOR
# =========================================

def risk_predictor(df):

    st.title("AI CREDIT RISK ENGINE")

    model = train_model(df)

    probs = model.predict_proba(df[["amount","trust_score"]])

    df["default_probability"] = probs[:,1]*100

    fig = px.scatter(

        df,

        x="amount",

        y="default_probability",

        size="amount",

        color="default_probability",

        color_continuous_scale="Reds",

        template="plotly_dark"

    )

    st.plotly_chart(fig,use_container_width=True)


# =========================================
# RECOVERY ENGINE
# =========================================

def recovery(df):

    st.title("RECOVERY ENGINE")

    pending = df[df["status"]=="Pending"]

    if pending.empty:
        st.success("No Pending Payments")
        return

    customer = st.selectbox("Customer",pending["customer"].unique())

    client = pending[pending["customer"]==customer].iloc[0]

    st.write("Outstanding Amount:",f"₹{client['amount']:,.0f}")

    messages = {

        "Social Proof":
        f"You are a trusted client. Please clear ₹{client['amount']} today.",

        "Loss Aversion":
        f"Your credit privileges may pause unless ₹{client['amount']} is cleared.",

        "Reciprocity":
        f"Thank you for your loyalty. Kindly settle ₹{client['amount']}."

    }

    choice = st.selectbox("Recovery Strategy",list(messages.keys()))

    st.code(messages[choice])

    upi="merchant@upi"

    link = f"upi://pay?pa={upi}&pn=Merchant&am={client['amount']}"

    st.code(link)

    if st.button("SEND RECOVERY MESSAGE"):

        time.sleep(1)

        st.success("Recovery Message Sent")


# =========================================
# LEDGER VIEW
# =========================================

def ledger(df):

    st.title("SMART LEDGER")

    st.dataframe(df,use_container_width=True)


# =========================================
# AUDIT
# =========================================

def audit(df):

    st.title("SYSTEM AUDIT")

    st.download_button(
        "Export Ledger",
        df.to_csv(index=False),
        "ledger_export.csv"
    )


# =========================================
# LOGIN
# =========================================

def login():

    st.title("KHATAKHAT AI ACCESS")

    u = st.text_input("Username",value="merchant")

    p = st.text_input("Password",type="password",value="admin123")

    if st.button("Login"):

        if u=="merchant" and p=="admin123":

            st.session_state.auth=True

            st.rerun()

        else:

            st.error("Access Denied")


# =========================================
# MAIN APP
# =========================================

def main():

    if "auth" not in st.session_state:
        st.session_state.auth=False

    if not st.session_state.auth:
        login()
        return

    df = get_data()

    if df.empty:
        df = generate_sample()

    with st.sidebar:

        st.title("KHATAKHAT AI")

        menu = [

            "Dashboard",
            "Upload Ledger",
            "Smart Ledger",
            "Risk Predictor",
            "Recovery Engine",
            "Audit"

        ]

        choice = st.radio("Navigation",menu)

        if st.button("Logout"):

            st.session_state.auth=False
            st.rerun()

    if choice=="Dashboard":
        dashboard(df)

    elif choice=="Upload Ledger":
        upload()

    elif choice=="Smart Ledger":
        ledger(df)

    elif choice=="Risk Predictor":
        risk_predictor(df)

    elif choice=="Recovery Engine":
        recovery(df)

    elif choice=="Audit":
        audit(df)


if __name__=="__main__":
    main()
