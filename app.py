import streamlit as st
import pandas as pd
import google.generativeai as genai

st.set_page_config(page_title="PaisaPal", layout="wide")

genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
model = genai.GenerativeModel("gemini-2.0-flash")

st.title("PaisaPal 💰")
st.caption("Know Your Business Health in Seconds.")

st.sidebar.header("Upload Transaction CSV")
uploaded_file = st.sidebar.file_uploader("Upload CSV", type="csv")

with open("transactions_sample.csv", "rb") as f:
    st.sidebar.download_button(
        label="📥 Download Sample CSV",
        data=f,
        file_name="transactions_sample.csv",
        mime="text/csv"
    )

if uploaded_file:

    df = pd.read_csv(uploaded_file)

    df["Date"] = pd.to_datetime(df["Date"])
    df = df.sort_values("Date")
    df["Cash Balance"] = df["Amount"].cumsum()

    total_income   = df[df["Amount"] > 0]["Amount"].sum()
    total_expense  = abs(df[df["Amount"] < 0]["Amount"].sum())
    net_cashflow   = total_income - total_expense
    expense_ratio  = total_expense / total_income if total_income != 0 else 0

    income_df = df[df["Amount"] > 0]
    concentration_risk    = "Low"
    concentration_percent = 0

    if not income_df.empty:
        revenue_summary       = income_df.groupby("Description")["Amount"].sum()
        top_customer_value    = revenue_summary.max()
        concentration_percent = (top_customer_value / total_income) * 100
        if concentration_percent > 70:
            concentration_risk = "High"
        elif concentration_percent > 40:
            concentration_risk = "Moderate"

    total_days = (df["Date"].max() - df["Date"].min()).days + 1
    avg_daily_cashflow = net_cashflow / total_days if total_days > 0 else 0
    runway_days = 0
    if avg_daily_cashflow < 0:
        current_cash = df["Cash Balance"].iloc[-1]
        runway_days  = abs(current_cash / avg_daily_cashflow)

    score = 100
    if net_cashflow < 0:                   score -= 30
    if expense_ratio > 0.8:                score -= 25
    elif expense_ratio > 0.6:              score -= 15
    if concentration_risk == "High":       score -= 20
    elif concentration_risk == "Moderate": score -= 10
    score = max(score, 0)

    st.markdown("## Financial Overview")
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Inflow",  f"₹{total_income:,.0f}")
    col2.metric("Total Outflow", f"₹{total_expense:,.0f}")
    col3.metric("Net Position",  f"₹{net_cashflow:,.0f}")

    st.divider()

    st.markdown("## Business Health Score")
    st.markdown(
        f"""
        <div style='text-align:center; padding:40px 0;'>
            <h1 style='font-size:90px; margin-bottom:10px;'>{score}/100</h1>
        </div>
        """,
        unsafe_allow_html=True
    )

    if score >= 80:
        st.success("Strong Financial Position")
    elif score >= 50:
        st.warning("Stable — Monitor Key Areas")
    else:
        st.error("Opportunity to Improve Financial Structure")

    st.divider()

    st.markdown("## Cash Trend")
    st.line_chart(df.set_index("Date")["Cash Balance"])

    st.divider()

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

    st.markdown("## Cash Runway Estimate")
    if avg_daily_cashflow < 0:
        st.info(f"At current performance levels, cash buffer may sustain approximately **{int(runway_days)} days**.")
    else:
        st.success("Current operations are not consuming daily cash reserves.")

    st.divider()

    st.markdown("## 🧠 Executive Financial Brief")

    business_context = f"""
    You are PaisaPal, a friendly AI financial copilot for Indian small businesses (MSMEs).

    Here is the business financial data:
    - Total Income: ₹{total_income:,.0f}
    - Total Expenses: ₹{total_expense:,.0f}
    - Net Cash Flow: ₹{net_cashflow:,.0f}
    - Expense Ratio: {expense_ratio:.0%}
    - Revenue Concentration Risk: {concentration_risk} ({concentration_percent:.0f}% from top source)
    - Cash Trend: {'Improving' if df['Cash Balance'].iloc[-1] > df['Cash Balance'].iloc[0] else 'Declining'}
    - Cash Runway: {int(runway_days) if runway_days > 0 else 'N/A (positive cash flow)'} days
    - Health Score: {score}/100
    - Date Range: {df['Date'].min().strftime('%b %Y')} to {df['Date'].max().strftime('%b %Y')}
    """

    if "brief_generated" not in st.session_state:
        st.session_state.brief_generated = False

    if not st.session_state.brief_generated:
        with st.spinner("Generating your financial brief..."):
            brief_prompt = business_context + """
            Write a short Executive Financial Brief (3-4 sentences max) for this business owner.
            Be direct, friendly, and actionable. Mention the most important insight and one clear
            recommendation. Write in simple English, no jargon. Do not use bullet points.
            """
            response = model.generate_content(brief_prompt)
            st.session_state.brief = response.text
            st.session_state.brief_generated = True

    st.write(st.session_state.brief)

    st.divider()

    st.markdown("## 💬 Ask PaisaPal")
    st.caption("Ask anything in English or Hindi about your business finances.")

    if "messages" not in st.session_state:
        st.session_state.messages = []

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

    user_question = st.chat_input("e.g. Mera paisa kahan ja raha hai? / What is my biggest risk?")

    if user_question:
        with st.chat_message("user"):
            st.write(user_question)
        st.session_state.messages.append({"role": "user", "content": user_question})

        full_prompt = business_context + f"""
        Previous conversation:
        {chr(10).join([f"{m['role'].title()}: {m['content']}" for m in st.session_state.messages[:-1]])}

        The business owner asks: {user_question}

        Answer helpfully and concisely. If they write in Hindi, respond in Hindi.
        If in English, respond in English. Keep it under 4 sentences. Be specific with numbers.
        """

        with st.chat_message("assistant"):
            with st.spinner("PaisaPal is thinking..."):
                ai_response = model.generate_content(full_prompt)
                st.write(ai_response.text)

        st.session_state.messages.append({"role": "assistant", "content": ai_response.text})

else:
    st.info("Upload a transaction CSV file from the sidebar to begin.")
    st.markdown("👆 Don't have a CSV? Download the **sample file** from the sidebar to try PaisaPal instantly.")
