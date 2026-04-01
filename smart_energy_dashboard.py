import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import LabelEncoder

# ---------- Page Setup ----------
st.set_page_config(layout="wide", page_title="Smart Energy Dashboard")
st.title("💡 Smart Energy Awareness & Optimization Dashboard")

# ---------- Load Data ----------
data = pd.read_csv("energy_data_100.csv")

# ---------- Standardize categorical columns ----------
for col in ['AC Used', 'LED Used', 'Renewable', 'Implemented Tips?']:
    data[col] = data[col].str.title()

# ---------- Currency Conversion ----------
conversion_rate_hkd = 0.096  # 1 INR ≈ 0.096 HKD
conversion_rate_usd = 0.012  # 1 INR ≈ 0.012 USD
data['Cost (HKD)'] = data['Cost (₹)'] * conversion_rate_hkd
data['Cost (USD)'] = data['Cost (₹)'] * conversion_rate_usd

# ---------- Currency Toggle ----------
currency = st.sidebar.radio("💱 Select Currency", options=["INR", "HKD", "USD"])
currency_map = {
    "INR": ("Cost (₹)", "₹"),
    "HKD": ("Cost (HKD)", "HKD"),
    "USD": ("Cost (USD)", "$")
}
cost_col, currency_symbol = currency_map[currency]

# ---------- Sidebar Filters ----------
st.sidebar.header("🔎 Filter Households")
household_types = st.sidebar.multiselect(
    "Household Type", options=data['Household Type'].unique(), default=data['Household Type'].unique()
)
ac_filter = st.sidebar.multiselect("AC Used", options=['Yes', 'No'], default=['Yes', 'No'])
led_filter = st.sidebar.multiselect("LED Used", options=['Yes', 'No'], default=['Yes', 'No'])
renewable_filter = st.sidebar.multiselect("Renewable", options=['Yes', 'No'], default=['Yes', 'No'])
tips_filter = st.sidebar.multiselect("Implemented Tips?", options=['Yes', 'No'], default=['Yes', 'No'])

# ---------- Add New Household ----------
st.sidebar.header("➕ Add New Household")
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
        new_id = data["Household ID"].max() + 1 if not data.empty else 1
        new_row = {
            "Household ID": new_id,
            "Household Type": hh_type,
            "Occupants": occupants,
            "Daily Energy (kWh)": daily_energy,
            "Cost (₹)": daily_energy * 9,
            "AC Used": ac,
            "LED Used": led,
            "Renewable": renewable,
            "Implemented Tips?": tips,
            "Cost (HKD)": daily_energy * 9 * conversion_rate_hkd,
            "Cost (USD)": daily_energy * 9 * conversion_rate_usd
        }
        data = pd.concat([data, pd.DataFrame([new_row])], ignore_index=True)
        st.sidebar.success(f"✅ Household {new_id} added!")

# ---------- Delete Household ----------
st.sidebar.header("🗑️ Delete Household")
if not data.empty:
    del_id = st.sidebar.selectbox("Select Household ID to Delete", options=data['Household ID'].tolist())
    if st.sidebar.button("Delete Household"):
        data = data[data['Household ID'] != del_id].reset_index(drop=True)
        st.sidebar.success(f"✅ Household {del_id} deleted!")
else:
    st.sidebar.info("No households available to delete.")

# ---------- Apply Filters ----------
filtered_data = data[
    data['Household Type'].isin(household_types) &
    data['AC Used'].isin(ac_filter) &
    data['LED Used'].isin(led_filter) &
    data['Renewable'].isin(renewable_filter) &
    data['Implemented Tips?'].isin(tips_filter)
]

# ---------- Fallback function ----------
def safe_mean(series, fallback=None):
    return series.mean() if not series.empty else (fallback if fallback is not None else 0)

# ---------- Key Metrics ----------
avg_energy = safe_mean(filtered_data['Daily Energy (kWh)'], fallback=data['Daily Energy (kWh)'].mean())
avg_cost = safe_mean(filtered_data[cost_col], fallback=safe_mean(data[cost_col]))
tips_percent = safe_mean((filtered_data['Implemented Tips?'] == 'Yes') * 100,
                         fallback=(data['Implemented Tips?'] == 'Yes').mean() * 100)
renewable_percent = safe_mean((filtered_data['Renewable'] == 'Yes') * 100,
                              fallback=(data['Renewable'] == 'Yes').mean() * 100)

st.subheader("Key Metrics")
col1, col2, col3, col4 = st.columns(4)
col1.metric("Avg Energy (kWh)", f"{avg_energy:.2f}")
col2.metric(f"Avg Cost ({currency_symbol})", f"{avg_cost:.2f}")
col3.metric("% Implemented Tips", f"{tips_percent:.1f}%")
col4.metric("% Using Renewable", f"{renewable_percent:.1f}%")

# ---------- Display filtered data ----------
st.subheader("Household Energy Data")
display_data = filtered_data if not filtered_data.empty else data
if filtered_data.empty:
    st.info("⚠️ No households match your filter. Showing overall dataset as fallback.")
st.dataframe(display_data)

# ---------- Charts ----------
# Line chart
st.subheader("Daily Energy Usage (kWh)")
st.line_chart(display_data['Daily Energy (kWh)'])

# Bar chart
st.subheader(f"Daily Cost per Household ({currency_symbol})")
st.bar_chart(display_data.set_index('Household ID')[cost_col])

# Pie charts
st.subheader("Households Implementing Energy-Saving Tips")
tip_counts = display_data['Implemented Tips?'].value_counts()
fig1, ax1 = plt.subplots(figsize=(4,4))
ax1.pie(tip_counts, labels=tip_counts.index, autopct='%1.1f%%', colors=['#66b3ff','#ff9999'])
st.pyplot(fig1)

st.subheader("Renewable Energy Adoption")
renewable_counts = display_data['Renewable'].value_counts()
fig2, ax2 = plt.subplots(figsize=(4,4))
ax2.pie(renewable_counts, labels=renewable_counts.index, autopct='%1.1f%%', colors=['#99ff99','#ffcc99'])
st.pyplot(fig2)

# Boxplot
st.subheader("AC Usage vs Daily Energy")
fig3, ax3 = plt.subplots(figsize=(8,4))
sns.boxplot(x='AC Used', y='Daily Energy (kWh)', data=display_data, ax=ax3)
st.pyplot(fig3)

# Scatter
st.subheader("Energy vs Number of Occupants")
fig4, ax4 = plt.subplots()
sns.scatterplot(x='Occupants', y='Daily Energy (kWh)', hue='LED Used', data=display_data, palette="Set2", ax=ax4)
st.pyplot(fig4)

# Energy per occupant safely
st.subheader("Energy Usage per Occupant")
display_data = display_data.copy()
display_data['Energy per Occupant'] = display_data['Daily Energy (kWh)'] / display_data['Occupants']
st.bar_chart(display_data.set_index('Household ID')['Energy per Occupant'])

# Avg Energy by Household Type
st.subheader("Avg Energy Usage by Household Type")
avg_energy_type = display_data.groupby('Household Type')['Daily Energy (kWh)'].mean()
st.bar_chart(avg_energy_type)
