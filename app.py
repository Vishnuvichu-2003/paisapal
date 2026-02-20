import streamlit as st
import pandas as pd

st.set_page_config(page_title="PaisaPal", layout="wide")

# ---------- HEADER ----------
st.title("PaisaPal 💰")
st.caption("Your business cash companion.")

uploaded_file = st.sidebar.file_uploader("Upload Transaction CSV", type="csv")

if uploaded_file is not None:

    # ---------- DATA ----------
    df = pd.read_csv(uploaded_file)
    df["Date"] = pd.to_datetime(df["Date"])
    df = df.sort_values("Date")
    df["Cash Balance"] = df["Amount"].cumsum()

    total_income = df[df["Amount"] > 0]["Amount"].sum()
    total_expense = df[df["Amount"] < 0]["Amount"].sum()
    net_cashflow = total_income + total_expense

    expense_ratio = abs(total_expense) / total_income if total_income != 0 else 0

    total_days = (df["Date"].max() - df["Date"].min()).days + 1
    avg_daily_cashflow = net_cashflow / total_days if total_days > 0 else 0

    # ---------- HEALTH SCORE ----------
    score = 50

    if net_cashflow > 0:
        score += 20
    else:
        score -= 20

    if expense_ratio < 0.5:
        score += 15
    elif expense_ratio < 0.8:
        score += 5
    else:
        score -= 15

    if df["Cash Balance"].iloc[-1] > df["Cash Balance"].iloc[0]:
        score += 10
    else:
        score -= 10

    score = max(0, min(100, score))

    if score >= 80:
        health_label = "Strong"
    elif score >= 60:
        health_label = "Stable"
    elif score >= 40:
        health_label = "Monitor"
    else:
        health_label = "Needs Attention"

    # ---------- TABS ----------
    tab1, tab2, tab3 = st.tabs(["Overview", "Insights", "Ask PaisaPal"])

    # ================= OVERVIEW =================
    with tab1:

        st.subheader("Where You Stand")

        col1, col2, col3 = st.columns(3)

        col1.metric("Total Inflow", f"₹{total_income:,.0f}")
        col2.metric("Total Outflow", f"₹{abs(total_expense):,.0f}")
        col3.metric("Net Position", f"₹{net_cashflow:,.0f}")

        st.markdown("---")

        st.subheader("Cash Trend")
        st.line_chart(df.set_index("Date")["Cash Balance"])

        st.markdown("---")

        st.subheader("Business Health")
        st.metric("Health Score", f"{score}/100")
        st.write(f"Status: **{health_label}**")

    # ================= INSIGHTS =================
    with tab2:

        st.subheader("What This Means")

        if net_cashflow >= 0:
            st.write("• Income is currently covering expenses.")
        else:
            st.write("• Spending is currently higher than inflows.")

        if expense_ratio < 0.5:
            st.write("• Expense levels are comfortably aligned with income.")
        elif expense_ratio < 0.8:
            st.write("• Expenses are moderate relative to income.")
        else:
            st.write("• Expenses are consuming a large share of income.")

        if df["Cash Balance"].iloc[-1] > df["Cash Balance"].iloc[0]:
            st.write("• Cash position is gradually improving.")
        else:
            st.write("• Cash position is trending downward.")

        st.markdown("---")

        st.subheader("Suggested Focus")

        if expense_ratio > 0.8:
            st.write("Consider reviewing major expense categories to improve margin stability.")
        elif net_cashflow < 0:
            st.write("Improving inflow consistency could strengthen overall stability.")
        else:
            st.write("Current position is stable. Maintain spending discipline and monitor trends.")

    # ================= ASK PAISAPAL =================
    with tab3:

        st.subheader("Ask PaisaPal")

        user_question = st.text_input("Ask about profit, runway, score, or trend")

        if user_question:

            question = user_question.lower()
            response = ""

            if "profit" in question or "cash" in question:
                if net_cashflow >= 0:
                    response = "Your business is currently operating with positive cash flow."
                else:
                    response = "Spending is currently exceeding inflows."

            elif "runway" in question:
                if avg_daily_cashflow < 0:
                    current_cash = df["Cash Balance"].iloc[-1]
                    runway_days = abs(current_cash / avg_daily_cashflow)
                    response = f"Estimated runway is approximately {int(runway_days)} days."
                else:
                    response = "Runway risk is currently low."

            elif "score" in question:
                response = f"Your Business Health Score is {score}/100."

            elif "trend" in question:
                if df["Cash Balance"].iloc[-1] > df["Cash Balance"].iloc[0]:
                    response = "Cash trend is improving over time."
                else:
                    response = "Cash trend is gradually declining."

            else:
                response = "Try asking about profit, runway, score, or trend."

            st.success(response)

else:
    st.info("Upload a transaction CSV file from the sidebar to begin.")
