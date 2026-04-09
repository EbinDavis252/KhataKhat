import streamlit as st
import pandas as pd
import numpy as np
import sqlite3
from sklearn.ensemble import RandomForestClassifier
import plotly.express as px

st.set_page_config(page_title="Khatakhat AI", layout="wide")

# -----------------------------
# STYLE
# -----------------------------

st.markdown("""
<style>

.stApp{
background-color:#f6f8fb;
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
# FUNCTIONS
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

    X = df[["amount", "days_due", "trust_score"]]
    y = df["late"]

    model = RandomForestClassifier(n_estimators=100)

    model.fit(X, y)

    return model


# -----------------------------
# RECOVERY MESSAGE
# -----------------------------

def generate_message(risk):

    if risk > 0.7:
        return "High Risk → Send urgent reminder and restrict further credit"

    elif risk > 0.4:
        return "Medium Risk → Send polite reminder"

    else:
        return "Low Risk → Customer reliable"


# -----------------------------
# LANDING PAGE
# -----------------------------

def landing():

    st.markdown('<div class="hero-title">Khatakhat AI</div>', unsafe_allow_html=True)

    st.markdown('<div class="hero-sub">Turn Outstanding Credit Into Predictable Cashflow</div>', unsafe_allow_html=True)

    st.write("")

    st.markdown("""
    <div class="hero-desc">
    Khatakhat AI is a receivables intelligence platform for businesses.
    Instead of simply recording credit transactions, it analyzes customer payment
    behavior to predict delays, assess credit risk, and improve recovery strategies.
    </div>
    """, unsafe_allow_html=True)

    st.write("")
    st.write("")

    if st.button("Enter Platform"):
        st.session_state.page = "dashboard"
        st.rerun()

    st.write("")
    st.subheader("Why Khatakhat AI")

    col1,col2,col3 = st.columns(3)

    with col1:
        st.markdown("""
        <div class="card">
        <h4>Risk Prediction</h4>
        AI predicts which customers might delay payments.
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class="card">
        <h4>Cashflow Visibility</h4>
        Understand expected incoming payments.
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown("""
        <div class="card">
        <h4>Recovery Intelligence</h4>
        Get suggestions on how to recover dues.
        </div>
        """, unsafe_allow_html=True)

# -----------------------------
# DASHBOARD
# -----------------------------

def dashboard():

    st.title("Receivables Intelligence Dashboard")

    df = load_data()

    if df.empty:

        st.warning("No data available. Upload ledger or add records.")

        return

    model = train_model(df)

    X = df[["amount","days_due","trust_score"]]

    df["risk_probability"] = model.predict_proba(X)[:,1]

    df["recommendation"] = df["risk_probability"].apply(generate_message)

    # METRICS

    col1,col2,col3 = st.columns(3)

    outstanding = df[df.status=="Pending"]["amount"].sum()
    recovered = df[df.status=="Paid"]["amount"].sum()

    col1.metric("Outstanding Credit", f"₹{outstanding:,.0f}")
    col2.metric("Recovered Payments", f"₹{recovered:,.0f}")
    col3.metric("Average Trust Score", int(df.trust_score.mean()))

    st.write("")

    # RISK VISUALIZATION

    st.subheader("Customer Risk Distribution")

    fig = px.scatter(
        df,
        x="amount",
        y="trust_score",
        color="risk_probability",
        size="days_due",
        hover_name="customer"
    )

    st.plotly_chart(fig, use_container_width=True)

    st.write("")

    # CASHFLOW FORECAST

    st.subheader("Expected Cashflow")

    predicted_recovery = outstanding * 0.65

    st.info(f"Estimated recovery next 30 days: ₹{predicted_recovery:,.0f}")

    st.write("")

    # TABLE

    st.subheader("Customer Ledger Intelligence")

    st.dataframe(df, use_container_width=True)


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
            ["Dashboard","Upload Ledger","Manual Entry"]
        )

        if menu == "Dashboard":
            dashboard()

        elif menu == "Upload Ledger":
            upload_data()

        elif menu == "Manual Entry":
            manual_entry()


main()
