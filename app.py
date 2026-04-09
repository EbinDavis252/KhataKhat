import streamlit as st
import pandas as pd
import numpy as np
import sqlite3
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split

# ==========================================
# CONFIGURATION & SETUP
# ==========================================
st.set_page_config(page_title="Khatakhat | Recovery Engine", layout="wide", page_icon="💸")

# Database setup
conn = sqlite3.connect('khatakhat.db', check_same_thread=False)

# ==========================================
# HELPER FUNCTIONS & ML MODELS
# ==========================================
def generate_sample_data():
    """Generates a realistic mock dataset for micro-merchants."""
    np.random.seed(42)
    n = 200
    
    customers = [f"Customer {i}" for i in range(1, 51)]
    statuses = ["Paid", "Pending"]
    
    data = {
        "customer_id": np.random.randint(100, 150, n),
        "customer_name": np.random.choice(customers, n),
        "phone_number": [f"98765{np.random.randint(10000, 99999)}" for _ in range(n)],
        "purchase_date": [datetime.now() - timedelta(days=np.random.randint(1, 90)) for _ in range(n)],
        "amount": np.random.randint(500, 10000, n),
        "payment_status": np.random.choice(statuses, n, p=[0.6, 0.4]),
        "payment_method": np.random.choice(["UPI", "Cash", "Bank Transfer", "None"], n),
        "total_transactions": np.random.randint(1, 20, n),
    }
    
    df = pd.DataFrame(data)
    df['due_date'] = df['purchase_date'] + timedelta(days=15)
    
    # Feature Engineering: Derive missing fields
    current_date = datetime.now()
    df['payment_date'] = df.apply(lambda row: row['due_date'] + timedelta(days=np.random.randint(-5, 30)) if row['payment_status'] == 'Paid' else pd.NaT, axis=1)
    
    def calculate_delay(row):
        if row['payment_status'] == 'Paid':
            return max(0, (row['payment_date'] - row['due_date']).days)
        else:
            return max(0, (current_date - row['due_date']).days)
            
    df['days_delayed'] = df.apply(calculate_delay, axis=1)
    
    # Calculate customer-level avg delay
    avg_delay_map = df.groupby('customer_id')['days_delayed'].mean().to_dict()
    df['avg_payment_delay'] = df['customer_id'].map(avg_delay_map)
    
    return df

def train_risk_model(df):
    """Trains a Random Forest model to predict payment probability within 7 days."""
    # Simplify feature set for MVP
    features = ['amount', 'days_delayed', 'total_transactions', 'avg_payment_delay']
    
    # Target: 1 if delayed < 7 days and Paid, 0 otherwise
    df['target_paid_on_time'] = np.where((df['payment_status'] == 'Paid') & (df['days_delayed'] <= 7), 1, 0)
    
    X = df[features].fillna(0)
    y = df['target_paid_on_time']
    
    # In a real scenario, handle class imbalance and scale features.
    model = RandomForestClassifier(n_estimators=50, random_state=42)
    model.fit(X, y)
    
    return model, features

def get_data():
    """Fetches data from SQLite, or generates it if empty."""
    try:
        df = pd.read_sql("SELECT * FROM ledger", conn)
        df['purchase_date'] = pd.to_datetime(df['purchase_date'])
        df['due_date'] = pd.to_datetime(df['due_date'])
        if df.empty: raise ValueError
    except:
        df = generate_sample_data()
        df.to_sql("ledger", conn, if_exists="replace", index=False)
    return df

# Initialize Data & Models
df = get_data()
model, feature_cols = train_risk_model(df.copy())

# ==========================================
# UI MODULES
# ==========================================

def module_1_dashboard():
    st.header("📊 Merchant Dashboard")
    
    pending_df = df[df['payment_status'] == 'Pending']
    total_outstanding = pending_df['amount'].sum()
    total_customers = df['customer_id'].nunique()
    recovered_this_month = df[(df['payment_status'] == 'Paid') & (df['payment_date'] >= pd.Timestamp(datetime.now() - timedelta(days=30)))]['amount'].sum()
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Outstanding Credit (₹)", f"₹{total_outstanding:,.2f}")
    col2.metric("Total Customers", total_customers)
    col3.metric("Recovered This Month", f"₹{recovered_this_month:,.2f}")
    col4.metric("High Risk Customers", len(df[df['avg_payment_delay'] > 20]['customer_id'].unique()))
    
    st.markdown("---")
    c1, c2 = st.columns(2)
    with c1:
        status_counts = df['payment_status'].value_counts().reset_index()
        fig1 = px.pie(status_counts, names='payment_status', values='count', title="Overall Payment Success Rate", hole=0.4, color_discrete_sequence=['#00CC96', '#EF553B'])
        st.plotly_chart(fig1, use_container_width=True)
    with c2:
        trend = df.groupby(df['purchase_date'].dt.date)['amount'].sum().reset_index()
        fig2 = px.line(trend, x='purchase_date', y='amount', title="Credit Issuance Trend")
        st.plotly_chart(fig2, use_container_width=True)

def module_2_upload():
    st.header("📂 Upload Ledger Dataset")
    uploaded_file = st.file_uploader("Upload your Khatabook/Ledger (CSV or Excel)", type=['csv', 'xlsx'])
    
    if uploaded_file:
        try:
            if uploaded_file.name.endswith('.csv'):
                new_data = pd.read_csv(uploaded_file)
            else:
                new_data = pd.read_excel(uploaded_file)
            st.success("Dataset loaded successfully!")
            st.dataframe(new_data.head())
            
            if st.button("Clean & Save to Database"):
                new_data.to_sql("ledger", conn, if_exists="replace", index=False)
                st.success("Data securely saved to SQLite Database.")
                st.rerun()
        except Exception as e:
            st.error(f"Error processing file: {e}")

def module_3_ledger():
    st.header("📓 Customer Credit Ledger")
    
    col1, col2 = st.columns([1, 3])
    with col1:
        status_filter = st.selectbox("Filter by Status", ["All", "Pending", "Paid"])
        search_query = st.text_input("Search Customer Name")
    
    filtered_df = df.copy()
    if status_filter != "All":
        filtered_df = filtered_df[filtered_df['payment_status'] == status_filter]
    if search_query:
        filtered_df = filtered_df[filtered_df['customer_name'].str.contains(search_query, case=False)]
        
    st.dataframe(filtered_df[['customer_name', 'phone_number', 'amount', 'due_date', 'payment_status', 'days_delayed']], use_container_width=True)

def module_4_ai_prediction():
    st.header("🤖 AI Payment Prediction")
    st.write("Predicts the likelihood of a pending payment being cleared within the next 7 days.")
    
    pending_df = df[df['payment_status'] == 'Pending'].copy()
    
    if pending_df.empty:
        st.info("No pending payments to predict.")
        return
        
    # Generate predictions
    X_pred = pending_df[feature_cols].fillna(0)
    probabilities = model.predict_proba(X_pred)[:, 1] # Probability of class 1 (Paid on time)
    pending_df['Payment_Probability'] = probabilities * 100
    
    customer = st.selectbox("Select Customer to View AI Prediction", pending_df['customer_name'].unique())
    cust_data = pending_df[pending_df['customer_name'] == customer].iloc[0]
    
    prob_score = cust_data['Payment_Probability']
    
    fig = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = prob_score,
        title = {'text': f"Payment Likelihood for {customer} (%)"},
        gauge = {'axis': {'range': [None, 100]},
                 'bar': {'color': "darkblue"},
                 'steps' : [
                     {'range': [0, 40], 'color': "lightcoral"},
                     {'range': [40, 70], 'color': "khaki"},
                     {'range': [70, 100], 'color': "lightgreen"}],
                 }
    ))
    st.plotly_chart(fig)

def module_5_behavioral_engine():
    st.header("🧠 Behavioral Recovery Engine")
    st.write("AI-generated psychological nudges to improve recovery rates.")
    
    pending_df = df[df['payment_status'] == 'Pending']
    if pending_df.empty:
        st.info("No pending payments.")
        return
        
    customer = st.selectbox("Select Customer for Nudge", pending_df['customer_name'].unique())
    cust_data = pending_df[pending_df['customer_name'] == customer].iloc[0]
    amount = cust_data['amount']
    
    st.subheader("Select Nudge Strategy:")
    
    c1, c2, c3 = st.columns(3)
    with c1:
        st.info("**1. Social Proof**")
        msg1 = f"You are a trusted customer. Clearing ₹{amount} today will help maintain your Gold customer status with us."
        st.code(msg1, language="text")
        
    with c2:
        st.warning("**2. Loss Aversion**")
        msg2 = f"Alert: Your shop credit limit will be paused tomorrow unless the pending ₹{amount} is cleared today."
        st.code(msg2, language="text")
        
    with c3:
        st.success("**3. Reciprocity**")
        msg3 = f"We have valued your loyalty for a long time. Kindly settle your outstanding ₹{amount} today so we can continue serving you."
        st.code(msg3, language="text")
        
    st.markdown("---")
    st.button("📲 Simulate Send via WhatsApp API", type="primary")

def module_6_risk_detection():
    st.header("⚠️ Defaulter Risk Detection")
    
    # Categorize risk based on average payment delay
    customer_risk = df.groupby(['customer_id', 'customer_name'])['days_delayed'].mean().reset_index()
    
    def assign_risk(delay):
        if delay < 5: return "Low Risk"
        elif delay < 15: return "Medium Risk"
        else: return "High Risk"
        
    customer_risk['Risk_Level'] = customer_risk['days_delayed'].apply(assign_risk)
    
    col1, col2 = st.columns(2)
    with col1:
        fig = px.pie(customer_risk, names='Risk_Level', title="Customer Risk Distribution", color='Risk_Level',
                     color_discrete_map={"Low Risk": "green", "Medium Risk": "orange", "High Risk": "red"})
        st.plotly_chart(fig, use_container_width=True)
        
    with col2:
        st.subheader("Top High-Risk Customers")
        high_risk = customer_risk[customer_risk['Risk_Level'] == 'High Risk'].sort_values(by='days_delayed', ascending=False)
        st.dataframe(high_risk[['customer_name', 'days_delayed']].head(10), use_container_width=True)

def module_7_cash_flow():
    st.header("💸 Cash Flow Forecast")
    
    pending_df = df[df['payment_status'] == 'Pending'].copy()
    pending_df['predicted_payment_date'] = pending_df['due_date'] + pd.to_timedelta(pending_df['avg_payment_delay'], unit='D')
    
    forecast_dates = pending_df.groupby(pending_df['predicted_payment_date'].dt.date)['amount'].sum().reset_index()
    forecast_dates.columns = ['Date', 'Expected Inflow']
    forecast_dates = forecast_dates.sort_values('Date')
    
    fig = px.bar(forecast_dates, x='Date', y='Expected Inflow', title="Expected Cash Inflow (Next 30 Days)", text_auto='.2s')
    fig.update_traces(textfont_size=12, textangle=0, textposition="outside", cliponaxis=False)
    st.plotly_chart(fig, use_container_width=True)

def module_8_credit_score():
    st.header("🏅 Customer Credit Score")
    st.write("A proprietary score evaluating merchant trust.")
    
    # Behavioral Credit Score Formula Implementation
    scores = []
    for cust_id, group in df.groupby('customer_id'):
        avg_delay = group['days_delayed'].mean()
        total_txns = len(group)
        
        # Credit score mathematical model representation
        # Base: 900. Penalty for delays, reward for frequency.
        score = 900 - (avg_delay * 8) + (total_txns * 3)
        score = max(300, min(900, score)) # Bound between 300 and 900
        
        scores.append({
            'Customer Name': group['customer_name'].iloc[0],
            'Total Transactions': total_txns,
            'Average Delay (Days)': round(avg_delay, 1),
            'Credit Score': int(score)
        })
        
    score_df = pd.DataFrame(scores).sort_values(by='Credit Score', ascending=False)
    
    # Visualize score distribution
    fig = px.histogram(score_df, x="Credit Score", nbins=20, title="Credit Score Distribution")
    st.plotly_chart(fig, use_container_width=True)
    st.dataframe(score_df, use_container_width=True)

def module_9_insights():
    st.header("📈 Recovery Insights")
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Most Reliable Customers")
        reliable = df[df['payment_status'] == 'Paid'].groupby('customer_name')['days_delayed'].mean().sort_values().head(5)
        st.table(reliable)
        
    with col2:
        st.subheader("Total Stuck Working Capital")
        stuck_capital = df[(df['payment_status'] == 'Pending') & (df['days_delayed'] > 30)]['amount'].sum()
        st.metric("Capital Stuck (>30 Days)", f"₹{stuck_capital:,.2f}", delta="-Critical", delta_color="inverse")

def module_10_settings():
    st.header("⚙️ Admin / Settings")
    st.write("Configure your payment gateways and application preferences.")
    
    upi_id = st.text_input("Enter Merchant UPI ID", "merchant@upi")
    merchant_name = st.text_input("Merchant Name", "Gupta Traders")
    
    st.subheader("Generate Custom Payment Link")
    amount = st.number_input("Amount to request (₹)", min_value=1)
    
    if st.button("Generate Link"):
        upi_link = f"upi://pay?pa={upi_id}&pn={merchant_name.replace(' ', '%20')}&am={amount}"
        st.code(upi_link, language="text")
        st.success("Link generated! You can copy this and share it with the customer.")

# ==========================================
# SIDEBAR NAVIGATION
# ==========================================
st.sidebar.title("Khatakhat 🚀")
st.sidebar.caption("Behavioral Cash Flow Engine")

modules = {
    "1️⃣ Merchant Dashboard": module_1_dashboard,
    "2️⃣ Upload Ledger Dataset": module_2_upload,
    "3️⃣ Customer Credit Ledger": module_3_ledger,
    "4️⃣ AI Payment Prediction": module_4_ai_prediction,
    "5️⃣ Behavioral Recovery Engine": module_5_behavioral_engine,
    "6️⃣ Defaulter Risk Detection": module_6_risk_detection,
    "7️⃣ Cash Flow Forecast": module_7_cash_flow,
    "8️⃣ Customer Credit Score": module_8_credit_score,
    "9️⃣ Recovery Insights": module_9_insights,
    "🔟 Admin / Settings": module_10_settings
}

selection = st.sidebar.radio("Navigation", list(modules.keys()))

# Execute the selected module
modules[selection]()
