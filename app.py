import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(page_title="PaisaPal", layout="wide")

st.title("PaisaPal 💰")
st.caption("Your AI Financial Co-Pilot for Growing Businesses")

# Sidebar Upload
st.sidebar.header("Upload Transaction CSV")
uploaded_file = st.sidebar.file_uploader("Upload CSV", type="csv")

if uploaded_file:

    df = pd.read_csv(uploaded_file)

    # Prepare Data
    df["Date"] = pd.to_datetime(df["Date"])
    df = df.sort_values("Date")
    df["Cash Balance"] = df["Amount"].cumsum()

    total_income = df[df["Amount"] > 0]["Amount"].sum()
    total_expense = abs(df[df["Amount"] < 0]["Amount"].sum())
    net_cashflow = total_income - total_expense

    expense_ratio = total_expense / total_income if total_income != 0 else 0

    # Revenue Concentration
    income_df = df[df["Amount"] > 0]
    concentration_risk = "Low"
    concentration_percent = 0

    if not income_df.empty:
        revenue_summary = income_df.groupby("Description")["Amount"].sum()
        top_customer = revenue_summary.idxmax()
        top_customer_value = revenue_summary.max()
        concentration_percent = (top_customer_value / total_income) * 100

        if concentration_percent > 70:
            concentration_risk = "High"
        elif concentration_percent > 40:
            concentration_risk = "Moderate"

    # Business Health Score
    score = 100

    if net_cashflow < 0:
        score -= 30

    if expense_ratio > 0.8:
        score -= 25
    elif expense_ratio > 0.6:
        score -= 15

    if concentration_risk == "High":
        score -= 20
    elif concentration_risk == "Moderate":
        score -= 10

    score = max(score, 0)

    # KPI Overview
    st.markdown("## Financial Overview")

    col1, col2, col3 = st.columns(3)

    col1.metric("Total Inflow", f"₹{total_income:,.0f}")
    col2.metric("Total Outflow", f"₹{total_expense:,.0f}")
    col3.metric("Net Position", f"₹{net_cashflow:,.0f}")

    st.divider()

    # BIG PREMIUM SCORE DISPLAY
    st.markdown("## Business Health Score")

    st.markdown(
        f"""
        <div style='text-align: center; padding: 40px 0;'>
            <h1 style='font-size: 90px; margin-bottom: 10px;'>{score}/100</h1>
        </div>
        """,
        unsafe_allow_html=True
    )

    if score >= 80:
        st.success("Strong Financial Position")
    elif score >= 50:
        st.warning("Stable — Monitor Key Areas")
    else:
        st.error("Attention Needed — Review Cash Structure")

    st.divider()

    # Cash Trend
    st.markdown("## Cash Trend")
    st.line_chart(df.set_index("Date")["Cash Balance"])

    st.divider()

    # Risk Indicators
    st.markdown("## Risk Indicators")

    col1, col2, col3 = st.columns(3)

    if expense_ratio > 0.8:
        col1.error("Expense Intensity: High")
    elif expense_ratio > 0.6:
        col1.warning("Expense Intensity: Moderate")
    else:
        col1.success("Expense Intensity: Healthy")

    if concentration_risk == "High":
        col2.error(f"Revenue Concentration: High ({concentration_percent:.0f}%)")
    elif concentration_risk == "Moderate":
        col2.warning(f"Revenue Concentration: Moderate ({concentration_percent:.0f}%)")
    else:
        col2.success("Revenue Concentration: Diversified")

    if df["Cash Balance"].iloc[-1] > df["Cash Balance"].iloc[0]:
        col3.success("Cash Trend: Improving")
    else:
        col3.warning("Cash Trend: Declining")

    st.divider()

    # Cash Runway
    st.markdown("## Cash Runway Estimate")

    total_days = (df["Date"].max() - df["Date"].min()).days + 1

    if total_days > 0:
        avg_daily_cashflow = net_cashflow / total_days

        if avg_daily_cashflow < 0:
            current_cash = df["Cash Balance"].iloc[-1]
            runway_days = abs(current_cash / avg_daily_cashflow)
            st.warning(
                f"At current performance levels, cash buffer may sustain approximately {int(runway_days)} days."
            )
        else:
            st.success("Current operations are not consuming daily cash reserves.")

    st.divider()

    # Ask PaisaPal
    st.markdown("## Ask PaisaPal")

    question = st.text_input("Ask about your business performance")

    if question:

        q = question.lower()

        if "runway" in q:
            if avg_daily_cashflow < 0:
                response = f"Estimated runway is approximately {int(runway_days)} days."
            else:
                response = "Current operations are not burning cash daily."

        elif "risk" in q:
            response = f"Primary risks include {concentration_risk} revenue concentration and expense ratio of {expense_ratio:.2f}."

        elif "health" in q:
            response = f"Your Business Health Score is {score}/100."

        elif "trend" in q:
            if df["Cash Balance"].iloc[-1] > df["Cash Balance"].iloc[0]:
                response = "Cash balance trend is improving."
            else:
                response = "Cash balance trend is declining."

        else:
            response = "Try asking about runway, risk, health score, or trend."

        st.success(response)

else:
    st.info("Upload a transaction CSV file from the sidebar to begin.")