import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="Smart Budget Analyzer", page_icon="💰", layout="wide")

# --- STYLING ---
st.markdown("""
    <style>
    .main {
        background-color: #f5f5f5;
    }
    .stMetric {
        background-color: #ffffff;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.1);
    }
    </style>
    """, unsafe_allow_html=True)

# --- HEADER ---
st.title("💰 Smart Financial Goal Analyzer")
st.markdown("Analyze your spending habits and create a custom plan to achieve your financial goals.")

# --- SIDEBAR: INPUTS ---
st.sidebar.header("1. Your Financial Profile")

income = st.sidebar.number_input("Monthly Net Income ($)", min_value=0, value=5000, step=100)
savings_goal = st.sidebar.number_input("Monthly Savings Goal ($)", min_value=0, value=500, step=50)

st.sidebar.header("2. Add Recent Transactions")
# Create a simple form to add expenses
with st.sidebar.form("expense_form"):
    date = st.date_input("Date")
    category = st.selectbox("Category", ["Housing", "Food", "Transportation", "Utilities", "Entertainment", "Shopping", "Health", "Debt", "Other"])
    amount = st.number_input("Amount ($)", min_value=0.0, value=0.0, step=10.0)
    submitted = st.form_submit_button("Add Transaction")

# --- STATE MANAGEMENT (To keep data while app refreshes) ---
if 'transactions' not in st.session_state:
    # Pre-populating with some dummy data for demonstration
    st.session_state['transactions'] = [
        {"Date": "2023-10-01", "Category": "Housing", "Amount": 1500},
        {"Date": "2023-10-03", "Category": "Food", "Amount": 400},
        {"Date": "2023-10-05", "Category": "Transportation", "Amount": 150},
        {"Date": "2023-10-10", "Category": "Entertainment", "Amount": 100},
        {"Date": "2023-10-12", "Category": "Shopping", "Amount": 250},
    ]

# Add new transaction if submitted
if submitted:
    new_trans = {"Date": str(date), "Category": category, "Amount": amount}
    st.session_state['transactions'].append(new_trans)

# Convert to DataFrame
df = pd.DataFrame(st.session_state['transactions'])
total_spent = df['Amount'].sum() if not df.empty else 0

# --- MAIN DASHBOARD ---

# 1. TOP METRICS
col1, col2, col3, col4 = st.columns(4)
col1.metric("Monthly Income", f"${income:,.2f}")
col2.metric("Total Spent", f"${total_spent:,.2f}")
col3.metric("Remaining", f"${income - total_spent:,.2f}")
col4.metric("Savings Goal", f"${savings_goal:,.2f}", delta_color="normal")

st.divider()

# 2. ANALYSIS & VISUALIZATION
c1, c2 = st.columns([2, 1])

with c1:
    st.subheader("📊 Spending Breakdown")
    if not df.empty:
        # Group by Category
        category_df = df.groupby('Category')['Amount'].sum().reset_index()
        
        # Create Pie Chart
        fig, ax = plt.subplots()
        colors = ['#FF4B4B', '#FF9F36', '#FFD700', '#4BC0C0', '#9966FF', '#FF89bd']
        ax.pie(category_df['Amount'], labels=category_df['Category'], autopct='%1.1f%%', colors=colors, startangle=140)
        ax.axis('equal')
        st.pyplot(fig)
    else:
        st.info("No transactions added yet.")

with c2:
    st.subheader("📝 Transaction History")
    st.dataframe(df, hide_index=True)

# --- 3. CUSTOM BUDGETING PLAN (50/30/20 RULE) ---
st.divider()
st.subheader("🎯 Custom Budgeting Plan")

# Calculate Limits
needs_limit = income * 0.50
wants_limit = income * 0.30
savings_limit = income * 0.20

# Categorize current spending
current_needs = df[df['Category'].isin(['Housing', 'Utilities', 'Transportation', 'Food'])]['Amount'].sum()
current_wants = df[df['Category'].isin(['Entertainment', 'Shopping', 'Other'])]['Amount'].sum()
current_savings = savings_goal # Assuming goal is met if we track it

# Display Plan
plan_col1, plan_col2, plan_col3 = st.columns(3)

with plan_col1:
    st.info(f"**Needs (50%)**\nTarget: ${needs_limit:,.2f}\n\nCurrent: ${current_needs:,.2f}")
    if current_needs > needs_limit:
        st.error(f"⚠️ You are over budget by ${current_needs - needs_limit:,.2f}")
    else:
        st.success("✅ You are within the safe zone.")

with plan_col2:
    st.warning(f"**Wants (30%)**\nTarget: ${wants_limit:,.2f}\n\nCurrent: ${current_wants:,.2f}")
    if current_wants > wants_limit:
        st.error(f"⚠️ You are over budget by ${current_wants - wants_limit:,.2f}")
    else:
        st.success("✅ Great discipline!")

with plan_col3:
    st.success(f"**Savings (20%)**\nTarget: ${savings_limit:,.2f}\n\nGoal: ${savings_goal:,.2f}")
    if savings_goal >= savings_limit:
        st.balloons()
        st.write("🚀 You are hitting your savings target! Keep it up.")
    else:
        st.error(f"⚠️ You need to save ${savings_limit - savings_goal:,.2f} more to hit the 20% mark.")

# --- 4. RECOMMENDATIONS ---
st.subheader("💡 AI Recommendations")
if total_spent > income:
    st.error("CRITICAL ALERT: You are spending more than you earn! Immediate cuts are required in your 'Wants' categories.")
else:
    remaining = income - total_spent
    if remaining < savings_goal:
        diff = savings_goal - remaining
        st.warning(f"To meet your savings goal, you need to save an extra ${diff:,.2f}. Try reducing 'Entertainment' or 'Shopping' spending.")
    else:
        st.success("You have a healthy surplus! Consider investing your remaining funds or allocating them to your next big goal.")

# Reset Button
if st.button("Clear All Data"):
    st.session_state['transactions'] = []
    st.rerun()
