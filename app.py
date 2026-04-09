import streamlit as st
import pandas as pd
import numpy as np
import sqlite3
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import time

from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LinearRegression

# ==========================================
# PAGE CONFIG
# ==========================================
st.set_page_config(page_title="Khatakhat AI", layout="wide")

# ==========================================
# INDUSTRIAL THEME
# ==========================================
st.markdown("""
<style>

.stApp{
background-color:#0B0E14;
color:white;
}

h1,h2,h3{
font-family:monospace;
}

.stButton>button{
border:1px solid #1DE9B6;
color:#1DE9B6;
background:transparent;
height:3em;
width:100%;
}

.stButton>button:hover{
background:#1DE9B6;
color:black;
}

</style>
""",unsafe_allow_html=True)

# ==========================================
# DATABASE
# ==========================================

conn = sqlite3.connect("khatakhat_ai.db",check_same_thread=False)

conn.execute("""
CREATE TABLE IF NOT EXISTS ledger(
customer TEXT,
amount REAL,
status TEXT,
due_date TEXT,
trust_score INTEGER
)
""")

# ==========================================
# DATA FUNCTIONS
# ==========================================

def get_data():

    try:
        df = pd.read_sql("SELECT * FROM ledger",conn)

        if not df.empty:
            df["due_date"]=pd.to_datetime(df["due_date"])

        return df

    except:
        return pd.DataFrame()


def persist_data(df):

    df.columns=[c.lower().replace(" ","_") for c in df.columns]

    mapping={
    "customer_name":"customer",
    "payment_status":"status"
    }

    df=df.rename(columns=mapping)

    df.to_sql("ledger",conn,if_exists="replace",index=False)

    return True


# ==========================================
# SAMPLE DATA GENERATOR
# ==========================================

def generate_sample():

    customers=[
    "Alpha Traders",
    "Matrix Retail",
    "Zenith Logistics",
    "Global Hardware",
    "Vision Electronics"
    ]

    rows=[]

    for i in range(150):

        status=np.random.choice(["Paid","Pending"],p=[0.65,0.35])

        rows.append({

        "customer":np.random.choice(customers),

        "amount":np.random.randint(2000,100000),

        "status":status,

        "due_date":(datetime.now()+timedelta(days=np.random.randint(-30,30))).strftime("%Y-%m-%d"),

        "trust_score":np.random.randint(300,900)

        })

    df=pd.DataFrame(rows)

    persist_data(df)

    return df


# ==========================================
# AI RISK MODEL
# ==========================================

def train_model(df):

    model_df=df.copy()

    model_df["status"]=model_df["status"].str.lower()

    model_df["target"]=model_df["status"].apply(lambda x:1 if x=="pending" else 0)

    X=model_df[["amount","trust_score"]]

    y=model_df["target"]

    X_train,X_test,y_train,y_test=train_test_split(X,y,test_size=0.2,random_state=42)

    model=RandomForestClassifier(n_estimators=100)

    model.fit(X_train,y_train)

    return model


# ==========================================
# CASHFLOW FORECAST
# ==========================================

def forecast_cashflow(df):

    df["due_date"]=pd.to_datetime(df["due_date"])

    pending=df[df["status"]=="Pending"]

    if pending.empty:
        return pd.DataFrame()

    grouped=pending.groupby("due_date")["amount"].sum().reset_index()

    grouped["days"]=(grouped["due_date"]-grouped["due_date"].min()).dt.days

    model=LinearRegression()

    model.fit(grouped[["days"]],grouped["amount"])

    future=np.arange(grouped["days"].max()+1,grouped["days"].max()+15)

    preds=model.predict(future.reshape(-1,1))

    forecast=pd.DataFrame({

    "days":future,

    "predicted_cashflow":preds

    })

    return forecast


# ==========================================
# API SIMULATION
# ==========================================

class RecoveryAPI:

    @staticmethod
    def send_nudge(customer,amount):

        time.sleep(0.5)

        return{

        "status":"SUCCESS",

        "trace_id":f"KK-{np.random.randint(1000,9999)}",

        "time":datetime.now().strftime("%H:%M:%S")

        }


# ==========================================
# DASHBOARD
# ==========================================

def dashboard(df):

    st.title("EXECUTIVE COMMAND CENTER")

    if df.empty:
        st.warning("NO DATA FOUND")
        return

    pending=df[df["status"]=="Pending"]

    paid=df[df["status"]=="Paid"]

    total_pending=pending["amount"].sum()

    total_paid=paid["amount"].sum()

    health=(total_paid/(total_paid+total_pending))*100 if (total_paid+total_pending)>0 else 0

    c1,c2,c3,c4=st.columns(4)

    c1.metric("TOTAL OUTSTANDING",f"₹{total_pending:,.0f}")

    c2.metric("CAPITAL HEALTH",f"{health:.1f}%")

    c3.metric("AVG TRUST SCORE",int(df["trust_score"].mean()))

    c4.metric("TOTAL CUSTOMERS",df["customer"].nunique())

    st.subheader("3D CREDIT TOPOGRAPHY")

    fig=px.scatter_3d(

    df,

    x="amount",

    y="trust_score",

    z="status",

    color="status",

    template="plotly_dark"

    )

    st.plotly_chart(fig,use_container_width=True)

    st.subheader("AI CASHFLOW FORECAST")

    forecast=forecast_cashflow(df)

    if not forecast.empty:

        fig2=px.line(

        forecast,

        x="days",

        y="predicted_cashflow",

        template="plotly_dark"

        )

        st.plotly_chart(fig2,use_container_width=True)


# ==========================================
# LEDGER UPLOAD
# ==========================================

def upload_module():

    st.title("UPLOAD LEDGER DATA")

    file=st.file_uploader("Upload CSV or Excel",type=["csv","xlsx"])

    if file:

        if file.name.endswith("csv"):

            df=pd.read_csv(file)

        else:

            df=pd.read_excel(file)

        st.dataframe(df)

        if st.button("SAVE TO DATABASE"):

            persist_data(df)

            st.success("DATA SAVED")


# ==========================================
# RISK PREDICTOR
# ==========================================

def risk_predictor(df):

    st.title("AI RISK INTELLIGENCE")

    model=train_model(df)

    probs=model.predict_proba(df[["amount","trust_score"]])

    df["default_probability"]=probs[:,1]*100

    fig=px.scatter(

    df,

    x="amount",

    y="default_probability",

    size="amount",

    color="default_probability",

    color_continuous_scale="Reds",

    template="plotly_dark"

    )

    st.plotly_chart(fig,use_container_width=True)


# ==========================================
# RECOVERY ENGINE
# ==========================================

def recovery_module(df):

    st.title("RECOVERY ENGINE")

    pending=df[df["status"]=="Pending"]

    if pending.empty:

        st.success("NO PENDING PAYMENTS")

        return

    customer=st.selectbox("Select Customer",pending["customer"].unique())

    client=pending[pending["customer"]==customer].iloc[0]

    st.write("Outstanding:",f"₹{client['amount']:,.0f}")

    messages={

    "Social Proof":

    f"You are a trusted client. Please clear ₹{client['amount']} today to maintain priority status.",

    "Loss Aversion":

    f"Your credit privileges may pause tomorrow unless ₹{client['amount']} is cleared.",

    "Reciprocity":

    f"Thank you for being a valued partner. Kindly settle ₹{client['amount']} today."

    }

    choice=st.selectbox("Behavioral Nudge",list(messages.keys()))

    st.code(messages[choice])

    upi="merchant@upi"

    payment_link=f"upi://pay?pa={upi}&pn=Merchant&am={client['amount']}"

    st.code(payment_link)

    if st.button("SEND RECOVERY NUDGE"):

        response=RecoveryAPI.send_nudge(customer,client["amount"])

        st.success(f"Message Sent | Trace ID: {response['trace_id']}")


# ==========================================
# LEDGER VIEW
# ==========================================

def ledger_view(df):

    st.title("SMART LEDGER")

    st.dataframe(df,use_container_width=True)


# ==========================================
# AUDIT EXPORT
# ==========================================

def audit_module(df):

    st.title("AUDIT & RECONCILIATION")

    st.download_button(

    "EXPORT LEDGER",

    df.to_csv(index=False),

    "ledger_export.csv"

    )


# ==========================================
# LOGIN SYSTEM
# ==========================================

def login():

    st.title("KHATAKHAT AI ACCESS")

    u=st.text_input("Username",value="merchant")

    p=st.text_input("Password",type="password",value="admin123")

    if st.button("LOGIN"):

        if u=="merchant" and p=="admin123":

            st.session_state.auth=True

            st.rerun()

        else:

            st.error("ACCESS DENIED")


# ==========================================
# MAIN
# ==========================================

def main():

    if "auth" not in st.session_state:

        st.session_state.auth=False

    if not st.session_state.auth:

        login()

        return

    df=get_data()

    if df.empty:

        df=generate_sample()

    with st.sidebar:

        st.title("KHATAKHAT AI")

        menu=[

        "Dashboard",

        "Upload Ledger",

        "Smart Ledger",

        "Risk Predictor",

        "Recovery Engine",

        "Audit"

        ]

        choice=st.radio("Navigation",menu)

        if st.button("Logout"):

            st.session_state.auth=False

            st.rerun()

    if choice=="Dashboard":

        dashboard(df)

    elif choice=="Upload Ledger":

        upload_module()

    elif choice=="Smart Ledger":

        ledger_view(df)

    elif choice=="Risk Predictor":

        risk_predictor(df)

    elif choice=="Recovery Engine":

        recovery_module(df)

    elif choice=="Audit":

        audit_module(df)


if __name__=="__main__":

    main()
