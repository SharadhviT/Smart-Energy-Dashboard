import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import LabelEncoder

# ---------- Page Setup ----------
st.set_page_config(layout="wide", page_title="Smart Energy Dashboard")
st.title("💡 Smart Energy Awareness & Optimization Dashboard")

st.markdown("""
This dashboard provides insights into energy consumption across 100 households.  
It utilizes **statistical modeling and regression analysis** to identify inefficiencies.
""")

# ---------- Load Data ----------
data = pd.read_csv("energy_data_100.csv")

# ---------- Clean Data ----------
for col in ['AC Used','LED Used','Renewable','Implemented Tips?']:
    data[col] = data[col].str.title()

# ---------- Currency Conversion ----------
conversion_rate_hkd = 0.096
conversion_rate_usd = 0.012
data['Cost (HKD)'] = data['Cost (₹)'] * conversion_rate_hkd
data['Cost (USD)'] = data['Cost (₹)'] * conversion_rate_usd

# ---------- Currency Toggle ----------
currency = st.sidebar.radio("💱 Select Currency", ["INR", "HKD", "USD"])
cost_col = {
    "INR": "Cost (₹)",
    "HKD": "Cost (HKD)",
    "USD": "Cost (USD)"
}[currency]

currency_symbol = {
    "INR": "₹",
    "HKD": "HKD",
    "USD": "$"
}[currency]

# ---------- Filters ----------
st.sidebar.header("🔎 Filter Households")
household_types = st.sidebar.multiselect("Household Type", data['Household Type'].unique(), default=data['Household Type'].unique())
ac_filter = st.sidebar.multiselect("AC Used", ['Yes','No'], default=['Yes','No'])
led_filter = st.sidebar.multiselect("LED Used", ['Yes','No'], default=['Yes','No'])
renewable_filter = st.sidebar.multiselect("Renewable", ['Yes','No'], default=['Yes','No'])
tips_filter = st.sidebar.multiselect("Implemented Tips?", ['Yes','No'], default=['Yes','No'])

# ---------- Add Household ----------
st.sidebar.header("➕ Add New Household")
with st.sidebar.form("add_household"):
    hh_type = st.selectbox("Household Type", ["Apartment", "Villa", "Independent House"])
    occupants = st.number_input("Occupants", 1, 10, 3)
    daily_energy = st.number_input("Daily Energy (kWh)", 1, 200, 30)
    ac = st.selectbox("AC Used", ["Yes", "No"])
    led = st.selectbox("LED Used", ["Yes", "No"])
    renewable = st.selectbox("Renewable", ["Yes", "No"])
    tips = st.selectbox("Implemented Tips?", ["Yes", "No"])
    submitted = st.form_submit_button("Add Household")

    if submitted:
        new_id = data["Household ID"].max() + 1
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

# ---------- Delete ----------
st.sidebar.header("🗑️ Delete Household")
if not data.empty:
    del_id = st.sidebar.selectbox("Select Household ID", data['Household ID'])
    if st.sidebar.button("Delete"):
        data = data[data['Household ID'] != del_id]
        st.sidebar.success(f"Deleted {del_id}")

# ---------- Filter ----------
filtered_data = data[
    (data['Household Type'].isin(household_types)) &
    (data['AC Used'].isin(ac_filter)) &
    (data['LED Used'].isin(led_filter)) &
    (data['Renewable'].isin(renewable_filter)) &
    (data['Implemented Tips?'].isin(tips_filter))
]

display_data = filtered_data if not filtered_data.empty else data

# ---------- Safe Mean ----------
def safe_mean(series, fallback):
    return fallback if series.empty else series.mean()

# ---------- Metrics ----------
avg_energy = safe_mean(display_data['Daily Energy (kWh)'], data['Daily Energy (kWh)'].mean())
avg_cost = safe_mean(display_data[cost_col], data[cost_col].mean())
tips_percent = (display_data['Implemented Tips?'] == 'Yes').mean() * 100
renewable_percent = (display_data['Renewable'] == 'Yes').mean() * 100

st.subheader("📊 Key Metrics")
c1, c2, c3, c4 = st.columns(4)
c1.metric("Avg Energy", f"{avg_energy:.2f} kWh")
c2.metric("Avg Cost", f"{currency_symbol} {avg_cost:.2f}")
c3.metric("Tips Used", f"{tips_percent:.1f}%")
c4.metric("Renewable", f"{renewable_percent:.1f}%")

# ---------- Charts ----------
st.line_chart(display_data['Daily Energy (kWh)'])
st.bar_chart(display_data.set_index('Household ID')[cost_col])

# Pie Charts (fixed)
counts = display_data['Implemented Tips?'].value_counts()
fig1, ax1 = plt.subplots()
ax1.pie(counts, labels=counts.index, autopct='%1.1f%%')
st.pyplot(fig1)

counts2 = display_data['Renewable'].value_counts()
fig2, ax2 = plt.subplots()
ax2.pie(counts2, labels=counts2.index, autopct='%1.1f%%')
st.pyplot(fig2)

# ---------- Derived Metrics ----------
display_data = display_data.copy()
display_data['Energy per Occupant'] = display_data['Daily Energy (kWh)'] / display_data['Occupants']
st.bar_chart(display_data.set_index('Household ID')['Energy per Occupant'])

# ---------- Analysis ----------
avg_cost_led = safe_mean(display_data[display_data['LED Used']=='Yes'][cost_col], avg_cost)
avg_cost_non_led = safe_mean(display_data[display_data['LED Used']=='No'][cost_col], avg_cost)

avg_ac = safe_mean(display_data[display_data['AC Used']=='Yes']['Daily Energy (kWh)'], avg_energy)
avg_no_ac = safe_mean(display_data[display_data['AC Used']=='No']['Daily Energy (kWh)'], avg_energy)

renewable_avg = safe_mean(display_data[display_data['Renewable']=='Yes']['Daily Energy (kWh)'], avg_energy)
non_renewable_avg = safe_mean(display_data[display_data['Renewable']=='No']['Daily Energy (kWh)'], avg_energy)

# ---------- Regression ----------
st.subheader("📊 Regression Analysis")
reg_data = display_data.copy()

for col in ['AC Used','LED Used','Renewable']:
    reg_data[col] = LabelEncoder().fit_transform(reg_data[col])

X = reg_data[['Occupants','AC Used','LED Used','Renewable']]
y = reg_data['Daily Energy (kWh)']

model = LinearRegression().fit(X, y)
coeffs = pd.DataFrame({'Feature': X.columns, 'Impact': model.coef_})

st.dataframe(coeffs)

# R2 Score
r2 = model.score(X, y)
st.write(f"📊 Model Accuracy (R²): {r2:.3f}")

st.bar_chart(coeffs.set_index('Feature'))

# ---------- Recommendations ----------
st.subheader("📝 Data-Driven Recommendations")
recs = []

if avg_cost_led < avg_cost_non_led:
    recs.append(f"💡 LED saves {currency_symbol} {avg_cost_non_led - avg_cost_led:.2f}/day")

if avg_ac > avg_no_ac and avg_no_ac != 0:
    recs.append(f"❄️ AC increases energy by {((avg_ac-avg_no_ac)/avg_no_ac*100):.1f}%")

if renewable_avg < non_renewable_avg:
    recs.append("🌞 Promote renewable energy")

if tips_percent < 50:
    recs.append("📉 Increase awareness campaigns")

if not recs:
    recs.append("✅ Efficient usage patterns")

for r in recs:
    st.write(r)

# ---------- What-if ----------
st.subheader("🔮 What-If Scenario")

all_led = display_data.copy()
all_led['LED Used'] = 'Yes'
new_cost = safe_mean(all_led[cost_col], avg_cost)

total_savings = (avg_cost - new_cost) * len(display_data)

st.write(f"If all use LED → Save {currency_symbol} {total_savings:.2f}/day")

# ---------- Personalized ----------
st.subheader("🎯 Household Insights")

for _, row in display_data.head(5).iterrows():
    msg = f"House {row['Household ID']}: "
    if row['LED Used'] == 'No':
        msg += "Use LED. "
    if row['AC Used'] == 'Yes':
        msg += "Reduce AC. "
    if row['Renewable'] == 'No':
        msg += "Go solar. "
    st.write(msg)

# ---------- Download ----------
@st.cache_data
def convert(df):
    return df.to_csv(index=False).encode('utf-8')

st.download_button("Download CSV", convert(display_data), "data.csv")
