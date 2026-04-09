import streamlit as st
import pandas as pd
import numpy as np
import sqlite3
import plotly.express as px
from datetime import datetime, timedelta

# ==========================================
# 0. UI SETUP (STABLE SLATE THEME)
# ==========================================
st.set_page_config(page_title="KhataKhat | Phase 3", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #0F172A; color: #F1F5F9; }
    .action-card {
        background: #1E293B;
        border-top: 4px solid #F59E0B; /* Amber for Action */
        padding: 20px;
        border-radius: 10px;
        margin-bottom: 20px;
    }
    .stDateInput div[data-baseweb="input"] { background-color: #1E293B; color: white; }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 1. SCHEDULING LOGIC (The Brain)
# ==========================================
def calculate_optimal_date(due_date, trust_score):
    """
    Logic: 
    - Low Trust (<400): Reminder 2 days BEFORE due date.
    - Mid Trust (400-700): Reminder ON due date.
    - High Trust (>700): Reminder 3 days AFTER due date (Grace Period).
    """
    if trust_score < 400:
        return due_date - timedelta(days=2)
    elif trust_score > 700:
        return due_date + timedelta(days=3)
    else:
        return due_date

# ==========================================
# 2. MODULE 7: SMART CALENDAR & SCHEDULER
# ==========================================
def mod_scheduler(df, L):
    st.title("📅 Recovery Calendar")
    
    # Filter only pending for scheduling
    pending = df[df['status'] == 'Pending'].copy()
    pending['due_date'] = pd.to_datetime(pending['due_date'])
    
    # Apply Logic
    pending['scheduled_date'] = pending.apply(lambda x: calculate_optimal_date(x['due_date'], x['trust_score']), axis=1)
    
    st.markdown("""
    <div class="action-card">
        <h4 style="margin:0; color:#F59E0B;">🤖 Munim's Schedule Optimizer</h4>
        <p>I have analyzed customer behavior. High-trust clients get a grace period, while high-risk clients are flagged for early nudges.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Visualizing the Schedule
    schedule_viz = pending.groupby('scheduled_date')['amount'].sum().reset_index()
    fig = px.bar(schedule_viz, x='scheduled_date', y='amount', 
                 title="Planned Recovery Volume by Date",
                 color_discrete_sequence=['#F59E0B'], template="plotly_dark")
    st.plotly_chart(fig, use_container_width=True)
    
    # Daily Task List
    st.subheader("📝 Today's Recovery Tasks")
    today = datetime.now().date()
    todays_tasks = pending[pending['scheduled_date'].dt.date == today]
    
    if not todays_tasks.empty:
        st.dataframe(todays_tasks[['customer', 'amount', 'trust_score', 'status']], use_container_width=True)
        if st.button("Bulk Nudge All Today 📲"):
            st.success(f"WhatsApp API triggered for {len(todays_tasks)} clients.")
    else:
        st.info("No urgent tasks for today. Your capital flow is currently optimized.")

# ==========================================
# 3. MODULE 10: AUTOMATION SETTINGS
# ==========================================
def mod_automation_settings(L):
    st.title("⚙️ Workflow Automation")
    
    with st.expander("Smart Reminder Rules"):
        st.write("Current Logic Formula:")
        st.latex(r"Date_{opt} = Date_{due} + \delta(Trust)")
        
        st.checkbox("Enable Auto-WhatsApp on Due Date", value=True)
        st.checkbox("Send SMS if WhatsApp fails", value=False)
        st.slider("Grace Period for Star Payers (Days)", 1, 7, 3)

# ==========================================
# 4. DATA & ROUTING
# ==========================================
conn = sqlite3.connect('khatakhat_logic.db', check_same_thread=False)

def main():
    if "auth" not in st.session_state: st.session_state.auth = True # Skipping login for speed
    
    df = pd.read_sql("SELECT * FROM ledger", conn)
    
    with st.sidebar:
        st.title("KhataKhat AI")
        choice = st.radio("Phase 3 Navigation", ["Recovery Calendar", "Automation Settings", "Back to Dashboard"])

    if choice == "Recovery Calendar":
        mod_scheduler(df, "English")
    elif choice == "Automation Settings":
        mod_automation_settings("English")
    else:
        st.write("Returning to main engine...")

if __name__ == "__main__":
    main()
