import streamlit as st
import pandas as pd
import numpy as np
import sqlite3
import plotly.express as px
from sklearn.ensemble import RandomForestClassifier
from datetime import datetime

st.set_page_config(page_title="Khatakhat AI", layout="wide")

# -----------------------------
# STYLE
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

.feature-card{
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
# LANDING PAGE
# -----------------------------

def landing():

    st.markdown('<div class="hero-title">Khatakhat AI</div>', unsafe_allow_html=True)
    st.markdown('<div class="hero-sub">Turn Outstanding Credit Into Predictable Cashflow</div>', unsafe_allow_html=True)

    st.write("")

    st.markdown("""
    <div class="hero-desc">
    Khatakhat AI is a receivables intelligence platform designed for small and medium businesses.
    It analyzes customer payment behavior, predicts default risks, and recommends recovery strategies
    to improve business cashflow.
    </div>
    """, unsafe_allow_html=True)

    st.write("")
    st.write("")

    if st.button("Enter Platform"):
        st.session_state.page = "dashboard"
        st.rerun()

    st.write("")
    st.write("")

    st.subheader("Platform Capabilities")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("""
        <div class="feature-card">
        <h4>AI Payment Risk Prediction</h4>
        Identify customers likely to delay payments using predictive analytics.
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class="feature-card">
        <h4>Cashflow Forecasting</h4>
        Estimate expected incoming payments and manage working capital.
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown("""
        <div class="feature-card">
        <h4>Recovery Intelligence</h4>
        Get smart recommendations for recovering pending payments.
        </div>
        """, unsafe_allow_html=True)

# -----------------------------
# DATA FUNCTIONS
# -----------------------------

def insert_data(customer, amount, days_due, status, trust):

    conn.execute(
        "INSERT INTO ledger VALUES (?,?,?,?,?)",
        (customer, amount, days_due, status, trust)
    )

    conn.commit()


def load_data():

    df = pd.read_sql("SELECT * FROM ledger", conn)

    return df


# -----------------------------
# AI MODEL
# -----------------------------

def train_model(df):

    df["late"] = df["status"].apply(lambda x: 1 if x == "Pending" else 0)

    X = df[["amount", "days_due", "trust_score"]]
    y = df["late"]

    model = RandomForestClassifier()

    model.fit(X, y)

    return model


# -----------------------------
# RECOVERY MESSAGE
# -----------------------------

def recovery_message(row):

    if row["risk"] > 0.7:
        return f"Customer {row['customer']} is high risk. Send urgent payment reminder."

    if row["risk"] > 0.4:
        return f"Friendly reminder recommended for {row['customer']}."

    return f"{row['customer']} is reliable. Standard reminder sufficient."


# -----------------------------
# DASHBOARD
# -----------------------------

def dashboard():

    st.title("Receivables Intelligence Dashboard")

    df = load_data()

    if df.empty:

        st.info("No ledger data available")

    else:

        model = train_model(df)

        X = df[["amount", "days_due", "trust_score"]]

        df["risk"] = model.predict_proba(X)[:,1]

        col1, col2, col3 = st.columns(3)

        col1.metric("Total Outstanding", f"₹{df[df.status=='Pending']['amount'].sum():,.0f}")

        col2.metric("Recovered Payments", f"₹{df[df.status=='Paid']['amount'].sum():,.0f}")

        col3.metric("Avg Trust Score", int(df.trust_score.mean()))

        st.write("")

        st.subheader("Customer Risk Analysis")

        fig = px.scatter(
            df,
            x="amount",
            y="trust_score",
            color="risk",
            hover_name="customer"
        )

        st.plotly_chart(fig, use_container_width=True)

        st.write("")

        st.subheader("Recovery Recommendations")

        df["recommendation"] = df.apply(recovery_message, axis=1)

        st.dataframe(df)

        # CASHFLOW FORECAST

        st.subheader("Cashflow Forecast")

        expected = df[df.status=="Pending"]["amount"].sum() * 0.6

        st.write(f"Expected Recovery Next 30 Days: ₹{expected:,.0f}")


# -----------------------------
# DATA INPUT
# -----------------------------

def data_input():

    st.subheader("Add Ledger Record")

    customer = st.text_input("Customer Name")

    amount = st.number_input("Amount")

    days_due = st.number_input("Days Due")

    trust = st.slider("Trust Score", 300, 900, 650)

    status = st.selectbox("Payment Status", ["Paid", "Pending"])

    if st.button("Add Record"):

        insert_data(customer, amount, days_due, status, trust)

        st.success("Record Added")


# -----------------------------
# DATA UPLOAD
# -----------------------------

def upload():

    st.subheader("Upload Ledger Data")

    file = st.file_uploader("Upload CSV or Excel")

    if file:

        if file.name.endswith("csv"):

            df = pd.read_csv(file)

        else:

            df = pd.read_excel(file)

        df.to_sql("ledger", conn, if_exists="replace", index=False)

        st.success("Data uploaded successfully")


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

        if menu == "Upload Ledger":
            upload()

        if menu == "Manual Entry":
            data_input()

main()
