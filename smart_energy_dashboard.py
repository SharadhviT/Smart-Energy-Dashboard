import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="Smart Energy Dashboard", layout="wide")

st.title("🏠 Smart Energy Awareness & Optimization Dashboard (Daily Cost ₹)")

# ---------- Load Data ----------
df = pd.read_csv("energy_data_100.csv")  # CSV can have more than 100 rows

# ---------- Add New Household ----------
st.sidebar.header("Add New Household")
with st.sidebar.form("add_household"):
    hh_type = st.selectbox("Household Type", ["Apartment", "Villa", "Independent House"])
    occupants = st.number_input("Occupants", min_value=1, max_value=10, value=3)
    daily_energy = st.number_input("Daily Energy (kWh)", min_value=1, max_value=200, value=30)
    ac = st.selectbox("AC Used", ["Yes", "No"])
    led = st.selectbox("LED Used", ["Yes", "No"])
    renewable = st.selectbox("Renewable", ["Yes", "No"])
    tips = st.selectbox("Implemented Tips?", ["Yes", "No"])
    submitted = st.form_submit_button("Add Household")
    if submitted:
        new_id = df["Household ID"].max() + 1
        new_row = {
            "Household ID": new_id,
            "Household Type": hh_type,
            "Occupants": occupants,
            "Daily Energy (kWh)": daily_energy,
            "Cost (₹)": daily_energy * 9,  # Daily cost
            "AC Used": ac,
            "LED Used": led,
            "Renewable": renewable,
            "Implemented Tips?": tips
        }
        df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
        st.success(f"✅ Household {new_id} added!")

# ---------- Filters ----------
st.sidebar.header("Filters")
ac_filter = st.sidebar.multiselect("AC Used", options=["Yes", "No"], default=["Yes", "No"])
led_filter = st.sidebar.multiselect("LED Used", options=["Yes", "No"], default=["Yes", "No"])
renewable_filter = st.sidebar.multiselect("Renewable", options=["Yes", "No"], default=["Yes", "No"])
tips_filter = st.sidebar.multiselect("Implemented Tips?", options=["Yes", "No"], default=["Yes", "No"])

filtered_df = df[
    df["AC Used"].isin(ac_filter) &
    df["LED Used"].isin(led_filter) &
    df["Renewable"].isin(renewable_filter) &
    df["Implemented Tips?"].isin(tips_filter)
]

st.subheader("📊 Household Data Table (Daily Cost ₹)")
st.dataframe(filtered_df)

# ---------- Line Chart: Daily Energy ----------
st.subheader("📈 Daily Energy (kWh) Trend")
st.line_chart(filtered_df.set_index("Household ID")["Daily Energy (kWh)"])

# ---------- Bar Chart: Daily Cost ----------
st.subheader("💰 Daily Cost per Household (₹)")
st.bar_chart(filtered_df.set_index("Household ID")["Cost (₹)"])

# ---------- Pie Chart: Tips Adoption ----------
st.subheader("🥇 % Households Implementing Energy-Saving Tips")
tips_counts = filtered_df["Implemented Tips?"].value_counts()
fig1, ax1 = plt.subplots(figsize=(4,4))  # Smaller pie chart
ax1.pie(tips_counts, labels=tips_counts.index, autopct='%1.1f%%', startangle=90, colors=["#66b3ff","#ff9999"])
ax1.axis('equal')
st.pyplot(fig1)

# ---------- Top 3 Energy-Saving Tips ----------
st.subheader("💡 Top 3 Energy-Saving Tips")
top_tips = [
    "1. Switch to LED bulbs",
    "2. Use AC only when necessary",
    "3. Install renewable energy sources (solar panels, etc.)"
]
for tip in top_tips:
    st.markdown(f"- {tip}")

# ---------- Summary Metrics ----------
st.subheader("📌 Summary Metrics")
col1, col2, col3 = st.columns(3)
col1.metric("Total Households", len(filtered_df))
col2.metric("Average Daily Energy (kWh)", round(filtered_df["Daily Energy (kWh)"].mean(),2))
col3.metric("Average Daily Cost (₹)", round(filtered_df["Cost (₹)"].mean(),2))
