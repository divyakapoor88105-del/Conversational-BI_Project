import streamlit as st
import pandas as pd
import plotly.express as px

def generate_insights(data):
    insights = []

    # Top Product
    top_product = data.groupby("Product")["Revenue"].sum().idxmax()
    insights.append(f"🏆 {top_product} is the top performing product.")

    # Best Region
    top_region = data.groupby("Region")["Revenue"].sum().idxmax()
    insights.append(f"🌍 {top_region} is the best performing region.")

    # Profit Check
    total_profit = data["Profit"].sum()
    if total_profit > 0:
        insights.append("📈 Business is overall profitable.")
    else:
        insights.append("⚠️ Business is running in loss.")

    # Trend
    if "Date" in data.columns:
        insights.append("📊 Revenue trend shows business performance over time.")

    return insights
# Page configuration
st.set_page_config(
    page_title="Conversational AI Business Intelligence",
    page_icon="📊",
    layout="wide"
)

# Dark UI styling
st.markdown("""
<style>

body {
    background-color:#0E1117;
}

.big-title {
    font-size:40px;
    font-weight:bold;
}

.small-text {
    font-size:15px;
}

button[kind="secondary"] {
    background-color:#1f77b4;
    color:white;
    border-radius:8px;
}

</style>
""", unsafe_allow_html=True)

# Title
st.markdown("""
<h1 style='text-align:center;
font-size:60px;
font-weight:800;
color:#00E5FF;'>
📊 Conversational AI for Instant Business Intelligence
</h1>
""", unsafe_allow_html=True)

st.markdown(
"<p style='text-align:center;font-size:18px;color:gray;'>Ask business questions and instantly generate AI-powered insights</p>",
unsafe_allow_html=True
)


# Upload Dataset
st.header("📂 Upload Dataset")

uploaded_file = st.file_uploader("Upload CSV Dataset", type=["csv"])

if uploaded_file:
    data = pd.read_csv(uploaded_file)
else:
    data = pd.read_csv("dataset.csv")

# Dataset Preview
with st.expander("Preview Dataset"):
    st.dataframe(data.head())

# Key Metrics
st.header("📊 Key Business Insights")

total_revenue = data["Revenue"].sum()
top_product = data.groupby("Product")["Revenue"].sum().idxmax()
top_region = data.groupby("Region")["Revenue"].sum().idxmax()
total_profit = data["Profit"].sum()


c1, c2, c3, c4 = st.columns(4)

c1.markdown("<p style='font-size:20px;'><b>💰 Total Revenue</b></p>", unsafe_allow_html=True)
c1.markdown(f"<p style='font-size:18px;'>{total_revenue}</p>", unsafe_allow_html=True)

c2.markdown("<p style='font-size:20px;'><b>🏆 Top Product</b></p>", unsafe_allow_html=True)
c2.markdown(f"<p style='font-size:18px;'>{top_product}</p>", unsafe_allow_html=True)

c3.markdown("<p style='font-size:20px;'><b>🌍 Best Region</b></p>", unsafe_allow_html=True)
c3.markdown(f"<p style='font-size:18px;'>{top_region}</p>", unsafe_allow_html=True)

c4.markdown("<p style='font-size:20px;'><b>📈 Total Profit</b></p>", unsafe_allow_html=True)
c4.markdown(f"<p style='font-size:18px;'>{total_profit}</p>", unsafe_allow_html=True)

# Session state
if "question" not in st.session_state:
    st.session_state.question=""

if "chat_history" not in st.session_state:
    st.session_state.chat_history=[]

if "charts" not in st.session_state:
    st.session_state.charts=[]

if "insights" not in st.session_state:
    st.session_state.insights = []

# Suggested Questions
st.header("💡 Suggested Questions")

b1,b2 = st.columns(2)

with b1:

    if st.button("📊 Generate Sales Dashboard", use_container_width=True):
        st.session_state.question="sales dashboard"

    if st.button("🏆 Best Selling Product", use_container_width=True):
        st.session_state.question="best product"

with b2:

    if st.button("🌍 Revenue by Region", use_container_width=True):
        st.session_state.question="revenue by region"

    if st.button("💰 Total Profit", use_container_width=True):
        st.session_state.question="profit"

# Question Input
st.header("💬 Ask Question")

question = st.text_input("Type business question", value=st.session_state.question)

def smart_query(q, data):

    import plotly.express as px

    q = q.lower()

    num_cols = data.select_dtypes(include="number").columns.tolist()
    cat_cols = data.select_dtypes(include="object").columns.tolist()

    # -------- TOTAL --------
    if "total" in q:
        for col in num_cols:
            if col.lower() in q:
                return f"Total {col} is {data[col].sum()}"

    # -------- AVERAGE --------
    if "average" in q or "mean" in q:
        for col in num_cols:
            if col.lower() in q:
                return f"Average {col} is {data[col].mean()}"

    # -------- TOP --------
    if "top" in q or "best" in q:
        if cat_cols and num_cols:
            df = data.groupby(cat_cols[0])[num_cols[0]].sum().reset_index()
            top = df.sort_values(num_cols[0], ascending=False).iloc[0]
            return f"Top {cat_cols[0]} is {top[cat_cols[0]]} with {top[num_cols[0]]}"

    # -------- GROUP BY --------
    if "by" in q:
        for cat in cat_cols:
            if cat.lower() in q:
                for num in num_cols:
                    if num.lower() in q:

                        df = data.groupby(cat)[num].sum().reset_index()

                        fig = px.bar(df, x=cat, y=num, title=f"{num} by {cat}")

                        return f"Showing {num} by {cat}", fig

    # -------- SPECIFIC VALUE --------
    for col in cat_cols:
        unique_vals = data[col].dropna().astype(str).str.lower().unique()

        for val in unique_vals:
            if val in q:
                for num in num_cols:
                    if num.lower() in q:
                        filtered = data[data[col].astype(str).str.lower() == val]
                        return f"Total {num} for {val.title()} is {filtered[num].sum()}"

    # -------- TREND --------
    if "trend" in q or "over time" in q:
        if "Date" in data.columns and num_cols:
            df = data.groupby("Date")[num_cols[0]].sum().reset_index()
            fig = px.line(df, x="Date", y=num_cols[0], title="Trend Over Time")
            return "Showing trend over time", fig

    return "I analyzed your data but couldn't find a clear answer. Try rephrasing."

# AI Logic

# =========================
# NEW AI LOGIC (FINAL FIX)
# =========================
if question:

    q = question.lower().strip()
    response = ""

    # =========================
    # DASHBOARD (FORCED LOGIC)
    # =========================
    if "dashboard" in q or "sales dashboard" in q:

        prod = data.groupby("Product")["Revenue"].sum().reset_index()
        fig1 = px.bar(prod, x="Product", y="Revenue", title="Revenue by Product")

        reg = data.groupby("Region")["Revenue"].sum().reset_index()
        fig2 = px.pie(reg, names="Region", values="Revenue", title="Revenue by Region")

        if "Date" in data.columns:
            trend = data.groupby("Date")["Revenue"].sum().reset_index()
            fig3 = px.line(trend, x="Date", y="Revenue", title="Revenue Trend")

            st.session_state.charts.append(fig3)

        st.session_state.charts.append(fig1)
        st.session_state.charts.append(fig2)

        response = "📊 Full Sales Dashboard Generated"

        insights = generate_insights(data)
        st.session_state.insights = insights

    # =========================
    # SMART AI (FOR EVERYTHING ELSE)
    # =========================
    else:

        result = smart_query(q, data)

        if isinstance(result, tuple):
            response, fig = result
            st.session_state.charts.append(fig)
        else:
            response = result

    # SAVE CHAT
    st.session_state.chat_history.append(("You", question))
    st.session_state.chat_history.append(("AI", response))



# Chat UI
st.header("💬 Conversation")

for sender,message in st.session_state.chat_history:

    if sender=="You":
        st.markdown(f"🧑 **You:** {message}")
    else:
        st.markdown(f"🤖 **AI:** {message}")

# Charts

if "charts" in st.session_state:
    for i, c in enumerate(st.session_state.charts):
        st.plotly_chart(c, use_container_width=True, key="chart_" + str(i))


st.header("🧠 AI Insights")

if "insights" in st.session_state:
    for i, ins in enumerate(st.session_state.insights):
        st.success(ins)