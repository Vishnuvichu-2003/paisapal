import streamlit as st
import pandas as pd

st.set_page_config(page_title="PaisaPal", layout="wide")

st.title("PaisaPal 💰")
st.caption("Know Your Business Health in Seconds.")

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
        top_customer_value = revenue_summary.max()
        concentration_percent = (top_customer_value / total_income) * 100

        if concentration_percent > 70:
            concentration_risk = "High"
        elif concentration_percent > 40:
            concentration_risk = "Moderate"

    # Health Score
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

    # Financial Overview
    st.markdown("## Financial Overview")
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Inflow", f"₹{total_income:,.0f}")
    col2.metric("Total Outflow", f"₹{total_expense:,.0f}")
    col3.metric("Net Position", f"₹{net_cashflow:,.0f}")

    st.divider()

    # Big Health Score
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
        st.warning("Opportunity to Improve Financial Structure")

    st.divider()

    # Cash Trend
    st.markdown("## Cash Trend")
    st.line_chart(df.set_index("Date")["Cash Balance"])

    st.divider()

    # Risk Indicators
    st.markdown("## Risk Indicators")
    col1, col2, col3 = st.columns(3)

    if expense_ratio > 0.8:
        col1.warning("Expense Intensity: High")
    elif expense_ratio > 0.6:
        col1.info("Expense Intensity: Moderate")
    else:
        col1.success("Expense Intensity: Healthy")

    if concentration_risk == "High":
        col2.warning(f"Revenue Concentration: High ({concentration_percent:.0f}%)")
    elif concentration_risk == "Moderate":
        col2.info(f"Revenue Concentration: Moderate ({concentration_percent:.0f}%)")
    else:
        col2.success("Revenue Concentration: Diversified")

    if df["Cash Balance"].iloc[-1] > df["Cash Balance"].iloc[0]:
        col3.success("Cash Trend: Improving")
    else:
        col3.info("Cash Trend: Slightly Declining")

    st.divider()

    # Cash Runway
    st.markdown("## Cash Runway Estimate")
    total_days = (df["Date"].max() - df["Date"].min()).days + 1

    if total_days > 0:
        avg_daily_cashflow = net_cashflow / total_days

        if avg_daily_cashflow < 0:
            current_cash = df["Cash Balance"].iloc[-1]
            runway_days = abs(current_cash / avg_daily_cashflow)
            st.info(f"At current performance levels, cash buffer may sustain approximately {int(runway_days)} days.")
        else:
            st.success("Current operations are not consuming daily cash reserves.")

    st.divider()

    # Executive Financial Brief
    st.markdown("## 🧠 Executive Financial Brief")

    if net_cashflow > 0:
        position_text = "Operations are generating positive cash flow."
    else:
        position_text = "Current spending is higher than inflows."

    if concentration_risk == "High":
        risk_text = "Revenue dependency on a single source is elevated."
    elif expense_ratio > 0.8:
        risk_text = "Expense structure is putting pressure on margins."
    elif df["Cash Balance"].iloc[-1] < df["Cash Balance"].iloc[0]:
        risk_text = "Cash trend indicates slight downward movement."
    else:
        risk_text = "No major structural risk detected."

    if score >= 80:
        outlook_text = "Financial structure appears stable and resilient."
    elif score >= 50:
        outlook_text = "Business remains stable but requires monitoring."
    else:
        outlook_text = "Focused improvements may enhance stability."

    st.write(f"**Current Position:** {position_text}")
    st.write(f"**Primary Risk Area:** {risk_text}")
    st.write(f"**Stability Outlook:** {outlook_text}")

    st.divider()

    # Ask PaisaPal - Structured Intent Engine
    st.markdown("## Ask PaisaPal")
    question = st.text_input("Ask about your business performance")

    if question:
        q = question.lower()

        runway_keywords = ["runway", "cash left", "how long", "survive", "sustain"]
        health_keywords = ["health", "score", "status", "condition", "stable", "safe"]
        risk_keywords = ["risk", "danger", "issue", "problem", "concern"]
        revenue_keywords = ["revenue", "dependency", "customer", "concentration"]
        expense_keywords = ["expense", "spending", "cost", "burn"]

        response = ""

        if any(word in q for word in runway_keywords):
            if avg_daily_cashflow < 0:
                response = f"At current burn levels, your cash runway is approximately {int(runway_days)} days."
            else:
                response = "Your operations are not currently burning cash daily."

        elif any(word in q for word in health_keywords):
            if score >= 80:
                response = "Your business is financially strong with stable structural indicators."
            elif score >= 50:
                response = "Your business is stable but requires monitoring."
            else:
                response = "There are structural pressures affecting financial stability."

        elif any(word in q for word in risk_keywords):
            risk_list = []
            if concentration_risk == "High":
                risk_list.append("high revenue concentration")
            if expense_ratio > 0.8:
                risk_list.append("elevated expense intensity")
            if df["Cash Balance"].iloc[-1] < df["Cash Balance"].iloc[0]:
                risk_list.append("declining cash trend")

            if risk_list:
                response = "Key structural risks include " + ", ".join(risk_list) + "."
            else:
                response = "No major structural risks are currently detected."

        elif any(word in q for word in revenue_keywords):
            if concentration_risk == "High":
                response = f"Approximately {int(concentration_percent)}% of revenue comes from a single source."
            elif concentration_risk == "Moderate":
                response = f"Revenue concentration is moderate at {int(concentration_percent)}%."
            else:
                response = "Revenue streams appear diversified."

        elif any(word in q for word in expense_keywords):
            if expense_ratio > 0.8:
                response = "Expenses are consuming a large portion of revenue."
            elif expense_ratio > 0.6:
                response = "Expenses are moderate and should be monitored."
            else:
                response = "Expense structure appears healthy."

        else:
            response = "You can ask about runway, health score, risks, revenue dependency, or expenses."

        st.success(response)

else:
    st.info("Upload a transaction CSV file from the sidebar to begin.")