import streamlit as st
import pandas as pd

st.set_page_config(page_title="PaisaPal", layout="wide")

# -------------------------
# SIDEBAR
# -------------------------
st.sidebar.title("Navigation")

page = st.sidebar.radio(
    "Go to",
    ["Overview", "Insights", "Ask PaisaPal"]
)

uploaded_file = st.sidebar.file_uploader("Upload Transaction CSV", type="csv")

st.title("PaisaPal 💰")
st.caption("Your business cash companion.")

# -------------------------
# LOAD DATA
# -------------------------
if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)

    df["Date"] = pd.to_datetime(df["Date"])
    df = df.sort_values("Date")
    df["Cumulative Cash"] = df["Amount"].cumsum()

    total_income = df[df["Amount"] > 0]["Amount"].sum()
    total_expense = df[df["Amount"] < 0]["Amount"].sum()
    net_cashflow = total_income + total_expense

    expense_ratio = 0
    if total_income != 0:
        expense_ratio = abs(total_expense) / total_income

    # -------------------------
    # OVERVIEW TAB
    # -------------------------
    if page == "Overview":

        st.subheader("Where You Stand")

        col1, col2, col3 = st.columns(3)

        col1.metric("Total Inflow", f"₹{total_income:,.0f}")
        col2.metric("Total Outflow", f"₹{abs(total_expense):,.0f}")
        col3.metric("Net Position", f"₹{net_cashflow:,.0f}")

        st.divider()

        st.subheader("Cash Trend")
        st.line_chart(df.set_index("Date")["Cumulative Cash"])

        st.divider()

        # -------------------------
        # BUSINESS HEALTH SCORE
        # -------------------------
        score = 50

        # Net cashflow impact
        if net_cashflow > 0:
            score += 20
        else:
            score -= 20

        # Expense ratio impact
        if expense_ratio < 0.5:
            score += 20
        elif expense_ratio < 0.8:
            score += 10
        else:
            score -= 10

        # Trend impact
        if df["Cumulative Cash"].iloc[-1] > df["Cumulative Cash"].iloc[0]:
            score += 10
        else:
            score -= 10

        score = max(0, min(score, 100))

        st.subheader("Business Health Score")

        if score >= 80:
            st.success(f"🟢 {score}/100 — Strong Business Position")
        elif score >= 50:
            st.warning(f"🟡 {score}/100 — Stable but Monitor Closely")
        else:
            st.error(f"🔴 {score}/100 — Needs Immediate Attention")

    # -------------------------
    # INSIGHTS TAB
    # -------------------------
    elif page == "Insights":

        st.subheader("Financial Insights")

        if net_cashflow < 0:
            st.error("⚠ Your business is currently running at a loss.")
        else:
            st.success("✅ Your business is cash positive.")

        if expense_ratio > 0.8:
            st.warning("Expenses are very high compared to income.")
        elif expense_ratio > 0.5:
            st.info("Expenses are moderate and should be monitored.")
        else:
            st.success("Expense levels are healthy.")

        # Top Expense
        expense_df = df[df["Amount"] < 0]
        if not expense_df.empty:
            expense_summary = expense_df.groupby("Description")["Amount"].sum()
            top_expense = expense_summary.idxmin()
            top_expense_value = abs(expense_summary.min())

            st.subheader("Top Expense Area")
            st.write(f"Highest spending on **{top_expense}** (₹{top_expense_value:,.0f})")

    # -------------------------
    # ASK PAISAPAL TAB
    # -------------------------
    elif page == "Ask PaisaPal":

        st.subheader("Ask PaisaPal")

        question = st.text_input("Ask something about your business:")

        if question:
            question = question.lower()

            if "profit" in question or "loss" in question:
                if net_cashflow > 0:
                    response = "Your business is currently profitable."
                else:
                    response = "Your business is currently running at a loss."

            elif "runway" in question:
                total_days = (df["Date"].max() - df["Date"].min()).days + 1
                avg_daily_cashflow = net_cashflow / total_days

                if avg_daily_cashflow < 0:
                    current_cash = df["Cumulative Cash"].iloc[-1]
                    runway_days = abs(current_cash / avg_daily_cashflow)
                    response = f"Estimated cash runway is approximately {int(runway_days)} days."
                else:
                    response = "You are not burning cash daily."

            elif "score" in question:
                response = f"Your Business Health Score is {score}/100."

            elif "trend" in question:
                if df["Cumulative Cash"].iloc[-1] > df["Cumulative Cash"].iloc[0]:
                    response = "Cash trend is improving over time."
                else:
                    response = "Cash trend is gradually declining."

            else:
                response = "Try asking about profit, runway, score, or trend."

            st.success(response)

else:
    st.info("Upload a transaction CSV file from the sidebar to begin.")