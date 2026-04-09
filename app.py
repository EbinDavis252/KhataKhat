import streamlit as st
import pandas as pd
import numpy as np
import sqlite3
from sklearn.ensemble import RandomForestClassifier
import plotly.express as px

st.set_page_config(page_title="Khatakhat AI", layout="wide")

# -----------------------------
# CLEAN FINTECH UI
# -----------------------------

st.markdown("""
<style>

.stApp{
background-color:#f5f7fb;
}

.hero-title{
font-size:60px;
font-weight:700;
text-align:center;
color:#0f172a;
}

.hero-sub{
font-size:24px;
text-align:center;
color:#334155;
}

.hero-desc{
font-size:18px;
text-align:center;
max-width:800px;
margin:auto;
color:#475569;
}

.card{
background:white;
padding:25px;
border-radius:12px;
box-shadow:0 4px 10px rgba(0,0,0,0.05);
}

</style>
""", unsafe_allow_html=True)

# -----------------------------
# DATABASE
# -----------------------------

conn = sqlite3.connect("khatakhat.db", check_same_thread=False)

conn.execute("""
CREATE TABLE IF NOT EXISTS ledger(
customer TEXT,
amount REAL,
days_due INTEGER,
status TEXT,
trust_score INTEGER
)
""")

# -----------------------------
# DATABASE FUNCTIONS
# -----------------------------

def insert_record(customer, amount, days_due, status, trust_score):

    conn.execute(
        "INSERT INTO ledger VALUES (?,?,?,?,?)",
        (customer, amount, days_due, status, trust_score)
    )

    conn.commit()


def load_data():

    try:
        df = pd.read_sql("SELECT * FROM ledger", conn)
        return df
    except:
        return pd.DataFrame()

# -----------------------------
# AI MODEL
# -----------------------------

def train_model(df):

    df["late"] = df["status"].apply(lambda x: 1 if x == "Pending" else 0)

    X = df[["amount","days_due","trust_score"]]
    y = df["late"]

    model = RandomForestClassifier(n_estimators=100)

    model.fit(X, y)

    return model

# -----------------------------
# RECOVERY RECOMMENDATION
# -----------------------------

def generate_recovery_strategy(risk):

    if risk > 0.7:
        return "High Risk → Send urgent reminder and restrict credit"

    elif risk > 0.4:
        return "Medium Risk → Send friendly reminder"

    else:
        return "Low Risk → Customer reliable"


# -----------------------------
# WHATSAPP MESSAGE GENERATOR
# -----------------------------

def generate_whatsapp_message(customer, amount):

    message = f"""
Hello {customer},

This is a friendly reminder from Khatakhat AI.

Our records show an outstanding balance of ₹{amount}.

Kindly clear the dues at your earliest convenience to maintain smooth business relations.

You can pay instantly using the UPI link provided.

Thank you for your continued support.

Regards
Khatakhat AI Collections
"""

    return message


# -----------------------------
# UPI PAYMENT LINK
# -----------------------------

def generate_upi_link(amount):

    upi_link = f"upi://pay?pa=khatakhat@upi&pn=KhatakhatAI&am={amount}"

    return upi_link


# -----------------------------
# LANDING PAGE
# -----------------------------

def landing():

    st.markdown('<div class="hero-title">Khatakhat AI</div>', unsafe_allow_html=True)

    st.markdown('<div class="hero-sub">Turn Outstanding Credit Into Predictable Cashflow</div>', unsafe_allow_html=True)

    st.write("")

    st.markdown("""
    <div class="hero-desc">
    Khatakhat AI is an intelligent receivables analytics platform designed for small
    and medium businesses. Instead of simply recording transactions, it analyzes
    customer payment behavior to predict delays, assess credit risk, and improve
    recovery strategies.
    </div>
    """, unsafe_allow_html=True)

    st.write("")
    st.write("")

    if st.button("Enter Platform"):

        st.session_state.page = "dashboard"
        st.rerun()

    st.write("")
    st.subheader("Platform Capabilities")

    col1,col2,col3 = st.columns(3)

    with col1:
        st.markdown("""
        <div class="card">
        <h4>AI Payment Risk Prediction</h4>
        Identify customers likely to delay payments using predictive analytics.
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class="card">
        <h4>Cashflow Forecasting</h4>
        Estimate expected incoming payments and manage working capital.
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown("""
        <div class="card">
        <h4>Recovery Intelligence</h4>
        Generate recovery strategies and automated reminders.
        </div>
        """, unsafe_allow_html=True)


# -----------------------------
# DASHBOARD
# -----------------------------

def dashboard():

    st.title("Receivables Intelligence Dashboard")

    df = load_data()

    if df.empty:

        st.warning("No data available. Upload ledger dataset or add manual records.")

        return

    model = train_model(df)

    X = df[["amount","days_due","trust_score"]]

    df["risk_probability"] = model.predict_proba(X)[:,1]

    df["recovery_strategy"] = df["risk_probability"].apply(generate_recovery_strategy)

    # -----------------------------
    # METRICS
    # -----------------------------

    col1,col2,col3 = st.columns(3)

    outstanding = df[df.status=="Pending"]["amount"].sum()
    recovered = df[df.status=="Paid"]["amount"].sum()

    col1.metric("Outstanding Credit", f"₹{outstanding:,.0f}")
    col2.metric("Recovered Payments", f"₹{recovered:,.0f}")
    col3.metric("Average Trust Score", int(df.trust_score.mean()))

    st.write("")

    # -----------------------------
    # RISK VISUALIZATION
    # -----------------------------

    st.subheader("Customer Risk Distribution")

    fig = px.scatter(
        df,
        x="amount",
        y="trust_score",
        color="risk_probability",
        size="days_due",
        hover_name="customer",
        title="Customer Payment Risk Analysis"
    )

    st.plotly_chart(fig, use_container_width=True)

    # -----------------------------
    # CASHFLOW FORECAST
    # -----------------------------

    st.subheader("Cashflow Forecast")

    predicted_recovery = outstanding * 0.65

    st.info(f"Estimated recovery in next 30 days: ₹{predicted_recovery:,.0f}")

    # -----------------------------
    # LEDGER INTELLIGENCE TABLE
    # -----------------------------

    st.subheader("Customer Ledger Intelligence")

    st.dataframe(df, use_container_width=True)

    # -----------------------------
    # RECOVERY ENGINE
    # -----------------------------

    st.subheader("Recovery Communication Engine")

    pending_df = df[df.status=="Pending"]

    for index,row in pending_df.iterrows():

        st.markdown(f"### {row['customer']}")

        message = generate_whatsapp_message(row["customer"], row["amount"])

        upi_link = generate_upi_link(row["amount"])

        st.text_area("WhatsApp Recovery Message", message, height=150)

        st.write("UPI Payment Link")

        st.code(upi_link)

        st.divider()


# -----------------------------
# MANUAL ENTRY
# -----------------------------

def manual_entry():

    st.title("Add Ledger Record")

    customer = st.text_input("Customer Name")

    amount = st.number_input("Transaction Amount")

    days_due = st.number_input("Days Payment Delayed")

    trust_score = st.slider("Customer Trust Score",300,900,650)

    status = st.selectbox("Payment Status",["Paid","Pending"])

    if st.button("Save Record"):

        insert_record(customer, amount, days_due, status, trust_score)

        st.success("Record added successfully")


# -----------------------------
# DATA UPLOAD
# -----------------------------

def upload_data():

    st.title("Upload Ledger Dataset")

    file = st.file_uploader("Upload CSV or Excel")

    if file:

        if file.name.endswith(".csv"):

            df = pd.read_csv(file)

        else:

            df = pd.read_excel(file)

        df.to_sql("ledger", conn, if_exists="replace", index=False)

        st.success("Ledger uploaded successfully")

        st.dataframe(df)


# -----------------------------
# MAIN APP
# -----------------------------

def main():

    if "page" not in st.session_state:

        st.session_state.page = "landing"

    if st.session_state.page == "landing":

        landing()

    else:

        menu = st.sidebar.radio(
            "Navigation",
            [
                "Dashboard",
                "Upload Ledger",
                "Manual Entry"
            ]
        )

        if menu == "Dashboard":
            dashboard()

        elif menu == "Upload Ledger":
            upload_data()

        elif menu == "Manual Entry":
            manual_entry()


main()
