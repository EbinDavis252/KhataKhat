import streamlit as st
import pandas as pd
import numpy as np
import sqlite3
import plotly.express as px
from datetime import datetime, timedelta

st.set_page_config(page_title="Khatakhat AI", layout="wide")

# ---------------------------
# Minimal Clean UI
# ---------------------------

st.markdown("""
<style>

.stApp{
background-color:#f8fafc;
}

h1{
font-size:52px;
font-weight:700;
color:#0f172a;
}

h2{
color:#0f172a;
}

h3{
color:#1e293b;
}

.tagline{
font-size:22px;
color:#475569;
}

.feature-card{
background:white;
padding:25px;
border-radius:12px;
box-shadow:0 4px 12px rgba(0,0,0,0.05);
}

.main-btn button{
background:#2563eb;
color:white;
border:none;
padding:10px 25px;
border-radius:8px;
font-weight:600;
}

</style>
""", unsafe_allow_html=True)

# ---------------------------
# DATABASE
# ---------------------------

conn = sqlite3.connect("khatakhat.db", check_same_thread=False)

conn.execute("""
CREATE TABLE IF NOT EXISTS ledger(
customer TEXT,
amount REAL,
status TEXT,
due_date TEXT,
trust_score INTEGER
)
""")


# ---------------------------
# SAMPLE DATA
# ---------------------------

def generate_sample():

    customers = [
        "Alpha Retail",
        "Metro Electronics",
        "Zenith Traders",
        "City Hardware",
        "Nova Distributors"
    ]

    rows=[]

    for i in range(120):

        status=np.random.choice(["Paid","Pending"],p=[0.7,0.3])

        rows.append({

        "customer":np.random.choice(customers),

        "amount":np.random.randint(2000,50000),

        "status":status,

        "due_date":(datetime.now()+timedelta(days=np.random.randint(-10,20))).strftime("%Y-%m-%d"),

        "trust_score":np.random.randint(400,850)

        })

    df=pd.DataFrame(rows)

    df.to_sql("ledger",conn,if_exists="replace",index=False)

    return df


def get_data():

    try:
        df=pd.read_sql("SELECT * FROM ledger",conn)
        return df
    except:
        return pd.DataFrame()


# ---------------------------
# LANDING PAGE
# ---------------------------

def landing():

    st.markdown("# Khatakhat AI")

    st.markdown(
        "<div class='tagline'>Turn Outstanding Credit Into Predictable Cashflow</div>",
        unsafe_allow_html=True
    )

    st.write("")

    st.write("""
Khatakhat AI is an intelligent receivables analytics platform designed to help businesses
track outstanding credit, predict payment risks, and accelerate collections using data-driven insights.

Instead of relying on manual follow-ups and spreadsheets, Khatakhat AI analyzes customer payment
behavior to recommend optimal recovery strategies and improve working capital efficiency.
""")

    st.write("")

    col1,col2,col3=st.columns(3)

    with col1:
        st.markdown("""
        <div class="feature-card">
        <h3>Credit Risk Intelligence</h3>
        Identify customers likely to delay payments using predictive analytics.
        </div>
        """,unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class="feature-card">
        <h3>Cashflow Forecasting</h3>
        Predict incoming payments and maintain better financial planning.
        </div>
        """,unsafe_allow_html=True)

    with col3:
        st.markdown("""
        <div class="feature-card">
        <h3>Smart Recovery Strategies</h3>
        AI suggests the best approach to recover pending payments.
        </div>
        """,unsafe_allow_html=True)

    st.write("")
    st.write("")

    if st.button("Enter Platform"):
        st.session_state.page="login"
        st.rerun()


# ---------------------------
# LOGIN
# ---------------------------

def login():

    st.title("Platform Access")

    username=st.text_input("Username")
    password=st.text_input("Password",type="password")

    if st.button("Login"):

        if username=="admin" and password=="admin":

            st.session_state.auth=True
            st.session_state.page="dashboard"
            st.rerun()

        else:
            st.error("Invalid credentials")


# ---------------------------
# DASHBOARD
# ---------------------------

def dashboard(df):

    st.title("Receivables Dashboard")

    pending=df[df["status"]=="Pending"]
    paid=df[df["status"]=="Paid"]

    col1,col2,col3=st.columns(3)

    col1.metric("Outstanding Amount",f"₹{pending['amount'].sum():,.0f}")

    col2.metric("Recovered Amount",f"₹{paid['amount'].sum():,.0f}")

    col3.metric("Average Trust Score",int(df["trust_score"].mean()))

    st.write("")

    fig=px.scatter(
        df,
        x="amount",
        y="trust_score",
        color="status",
        title="Customer Credit Distribution"
    )

    st.plotly_chart(fig,use_container_width=True)

    st.subheader("Ledger")

    st.dataframe(df,use_container_width=True)


# ---------------------------
# MAIN APP
# ---------------------------

def main():

    if "page" not in st.session_state:
        st.session_state.page="landing"

    if "auth" not in st.session_state:
        st.session_state.auth=False

    if st.session_state.page=="landing":
        landing()

    elif st.session_state.page=="login":
        login()

    elif st.session_state.page=="dashboard":

        df=get_data()

        if df.empty:
            df=generate_sample()

        dashboard(df)


main()
