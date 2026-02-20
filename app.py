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

    # Clean & Prepare Data
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

    # Layout KPIs
    st.markdown("## Financial Overview")

    col1, col2, col3 = st.columns(3)

    col1.metric("Total Inflow", f"₹{total_income:,.0f}")
    col2.metric("Total Outflow", f"₹{total_expense:,.0f}")
    col3.metric("Net Position", f"₹{net_cashflow:,.0f}")

    st.markdown("---")

    # Health Score Display
    st.markdown("## Business Health Score")

    if score >= 80:
        st.success(f"Health Score: {score}/100 — Strong Financial Position")
    elif score >= 50:
        st.warning(f"Health Score: {score}/100 — Stable but Monitor Closely")
    else:
        st.error(f"Health Score: {score}/100 — Needs Financial Attention")

    # Cash Trend Chart
    st.markdown("## Cash Trend")
    st.line_chart(df.set_index("Date")["Cash Balance"])

    # Risk Indicators
    st.markdown("## Risk Indicators")

    col1, col2, col3 = st.columns(3)

    # Expense Risk
    if expense_ratio > 0.8:
        col1.error("Expense Intensity: High")
    elif expense_ratio > 0.6:
        col1.warning("Expense Intensity: Moderate")
    else:
        col1.success("Expense Intensity: Healthy")

    # Revenue Concentration
    if concentration_risk == "High":
        col2.error(f"Revenue Concentration: High ({concentration_percent:.0f}%)")
    elif concentration_risk == "Moderate":
        col2.warning(f"Revenue Concentration: Moderate ({concentration_percent:.0f}%)")
    else:
        col2.success("Revenue Concentration: Diversified")

    # Cash Trend Direction
    if df["Cash Balance"].iloc[-1] > df["Cash Balance"].iloc[0]:
        col3.success("Cash Trend: Improving")
    else:
        col3.warning("Cash Trend: Declining")

    st.markdown("---")

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

    st.markdown("---")

    # AI Explanation (Founder Tone)
    st.markdown("## AI Financial Explanation")

    explanation = ""

    if net_cashflow < 0:
        explanation += "Cash flow requires attention. Reviewing cost structure may unlock stability. "
    else:
        explanation += "Operations are generating positive cash flow. Foundation appears stable. "

    if concentration_risk == "High":
        explanation += "Revenue concentration is high, which increases dependency risk. Consider diversifying income sources. "
    elif concentration_risk == "Moderate":
        explanation += "Moderate revenue concentration detected. Diversification could improve resilience. "

    if expense_ratio > 0.8:
        explanation += "Expense intensity is elevated. Strategic cost optimization may improve flexibility. "

    st.info(explanation)

    st.markdown("---")

    # Ask PaisaPal
    st.markdown("## Ask PaisaPal")

    question = st.text_input("Ask about your business performance")

    if question:

        q = question.lower()

        if "runway" in q:
            if avg_daily_cashflow < 0:
                response = f"Estimated runway is approximately {int(runway_days)} days at current burn rate."
            else:
                response = "Current operations are not burning cash daily."

        elif "risk" in q:
            response = f"Primary risks include {concentration_risk} revenue concentration and expense ratio of {expense_ratio:.2f}."

        elif "health" in q:
            response = f"Your Business Health Score is {score}/100."

        elif "trend" in q:
            if df["Cash Balance"].iloc[-1] > df["Cash Balance"].iloc[0]:
                response = "Cash balance trend is improving over time."
            else:
                response = "Cash balance trend is gradually declining."

        else:
            response = "Try asking about runway, risk, health score, or trend."

        st.success(response)

else:
    st.info("Upload a transaction CSV file from the sidebar to begin.")