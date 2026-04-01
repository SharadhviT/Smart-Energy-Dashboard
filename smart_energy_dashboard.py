import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import LabelEncoder

plt.style.use('ggplot')

# ---------- PAGE ----------
st.set_page_config(layout="wide", page_title="Smart Energy Dashboard")
st.title("💡 Smart Energy Optimization Dashboard")

# ---------- LOAD DATA ----------
data = pd.read_csv("energy_data_100.csv")

# Fix datatypes
data['Daily Energy (kWh)'] = pd.to_numeric(data['Daily Energy (kWh)'], errors='coerce')
data['Cost (₹)'] = pd.to_numeric(data['Cost (₹)'], errors='coerce')
data.dropna(inplace=True)

# Clean categories
for col in ['AC Used','LED Used','Renewable','Implemented Tips?']:
    data[col] = data[col].astype(str).str.title()

# ---------- CURRENCY ----------
conversion_rate_hkd = 0.096
conversion_rate_usd = 0.012

data['Cost (HKD)'] = data['Cost (₹)'] * conversion_rate_hkd
data['Cost (USD)'] = data['Cost (₹)'] * conversion_rate_usd

currency = st.sidebar.radio("💱 Currency", ["INR","HKD","USD"])

cost_col = {
    "INR": "Cost (₹)",
    "HKD": "Cost (HKD)",
    "USD": "Cost (USD)"
}[currency]

symbol = {
    "INR": "₹",
    "HKD": "HKD",
    "USD": "$"
}[currency]

# ---------- SIDEBAR FILTERS ----------
st.sidebar.header("🔎 Filter Households")

household_types = st.sidebar.multiselect(
    "Household Type",
    data['Household Type'].unique(),
    default=data['Household Type'].unique()
)

ac_filter = st.sidebar.multiselect(
    "AC Used",
    ['Yes','No'],
    default=['Yes','No']
)

led_filter = st.sidebar.multiselect(
    "LED Used",
    ['Yes','No'],
    default=['Yes','No']
)

renewable_filter = st.sidebar.multiselect(
    "Renewable",
    ['Yes','No'],
    default=['Yes','No']
)

tips_filter = st.sidebar.multiselect(
    "Implemented Tips?",
    ['Yes','No'],
    default=['Yes','No']
)

# ---------- APPLY FILTER ----------
filtered_data = data[
    (data['Household Type'].isin(household_types)) &
    (data['AC Used'].isin(ac_filter)) &
    (data['LED Used'].isin(led_filter)) &
    (data['Renewable'].isin(renewable_filter)) &
    (data['Implemented Tips?'].isin(tips_filter))
]

if filtered_data.empty:
    st.warning("⚠️ No matching data — showing full dataset")
    display_data = data.copy()
else:
    display_data = filtered_data.copy()

st.sidebar.markdown(f"### 📊 Showing {len(display_data)} households")

# ---------- METRICS ----------
avg_energy = display_data['Daily Energy (kWh)'].mean()
avg_cost = display_data[cost_col].mean()

c1, c2 = st.columns(2)
c1.metric("Avg Energy", f"{avg_energy:.2f} kWh")
c2.metric("Avg Cost", f"{symbol} {avg_cost:.2f}")

# =========================================================
# 📊 GRAPHS
# =========================================================

# 1 Energy line
fig, ax = plt.subplots()
ax.plot(display_data['Household ID'], display_data['Daily Energy (kWh)'])
ax.set_title("Daily Energy per Household")
ax.set_xlabel("Household ID")
ax.set_ylabel("Energy (kWh)")
st.pyplot(fig)

# 2 Cost bar
fig, ax = plt.subplots()
ax.bar(display_data['Household ID'], display_data[cost_col])
ax.set_title("Cost per Household")
ax.set_xlabel("Household ID")
ax.set_ylabel(f"Cost ({symbol})")
st.pyplot(fig)

# 3 Histogram
fig, ax = plt.subplots()
ax.hist(display_data['Daily Energy (kWh)'], bins=10)
ax.set_title("Energy Distribution")
ax.set_xlabel("Energy (kWh)")
ax.set_ylabel("Households")
st.pyplot(fig)

# 4 Scatter
fig, ax = plt.subplots()
sns.regplot(x='Daily Energy (kWh)', y=cost_col, data=display_data, ax=ax)
ax.set_title("Energy vs Cost")
ax.set_xlabel("Energy (kWh)")
ax.set_ylabel(f"Cost ({symbol})")
st.pyplot(fig)

# 5 Boxplot
fig, ax = plt.subplots()
sns.boxplot(x='AC Used', y='Daily Energy (kWh)', data=display_data, ax=ax)
ax.set_title("AC Usage vs Energy")
ax.set_xlabel("AC Used")
ax.set_ylabel("Energy (kWh)")
st.pyplot(fig)

# 6 Grouped
group = display_data.groupby(['AC Used','LED Used'])['Daily Energy (kWh)'].mean().unstack()

fig, ax = plt.subplots()
group.plot(kind='bar', ax=ax)
ax.set_title("AC vs LED Energy Comparison")
ax.set_xlabel("AC Used")
ax.set_ylabel("Avg Energy (kWh)")
st.pyplot(fig)

# =========================================================
# 📊 REGRESSION
# =========================================================

st.subheader("📊 Regression Analysis")

reg = display_data.copy()

for col in ['AC Used','LED Used','Renewable']:
    reg[col] = LabelEncoder().fit_transform(reg[col])

X = reg[['Occupants','AC Used','LED Used','Renewable']]
y = reg['Daily Energy (kWh)']

model = LinearRegression().fit(X, y)

coeffs = pd.DataFrame({
    "Feature": X.columns,
    "Impact": model.coef_
})

st.dataframe(coeffs)

r2 = model.score(X, y)
st.write(f"Model Accuracy (R²): {r2:.3f}")

# Feature chart
fig, ax = plt.subplots()
ax.bar(coeffs['Feature'], coeffs['Impact'])
ax.set_title("Feature Impact on Energy")
ax.set_xlabel("Feature")
ax.set_ylabel("Impact")
st.pyplot(fig)

# =========================================================
# 🔍 CORRELATION
# =========================================================

numeric = reg[['Daily Energy (kWh)','Occupants','AC Used','LED Used','Renewable']]

fig, ax = plt.subplots()
sns.heatmap(numeric.corr(), annot=True, cmap='coolwarm', ax=ax)
ax.set_title("Correlation Matrix")
st.pyplot(fig)

# =========================================================
# 🔮 SIMULATION
# =========================================================

st.subheader("🔮 What-If Simulation")

sim = display_data.copy()
sim['Daily Energy (kWh)'] = sim['Daily Energy (kWh)'].astype(float)

impact = st.slider("LED Efficiency Improvement (%)", 5, 30, 15) / 100

sim.loc[sim['LED Used'] == 'No', 'Daily Energy (kWh)'] *= (1 - impact)

sim['Cost (₹)'] = sim['Daily Energy (kWh)'] * 9
sim['Cost (HKD)'] = sim['Cost (₹)'] * conversion_rate_hkd
sim['Cost (USD)'] = sim['Cost (₹)'] * conversion_rate_usd

new_cost = sim[cost_col].mean()
savings = (avg_cost - new_cost) * len(sim)

st.write(f"New Avg Cost: {symbol} {new_cost:.2f}")
st.write(f"Total Savings: {symbol} {savings:.2f} per day")

# =========================================================
# 🎯 RECOMMENDATIONS
# =========================================================

st.subheader("🎯 Recommendations")

if savings > 0:
    st.write("💡 Switching to LED significantly reduces cost")

if r2 > 0.5:
    st.write("📊 Strong predictive relationship in data")

# =========================================================
# DOWNLOAD
# =========================================================

@st.cache_data
def convert(df):
    return df.to_csv(index=False).encode('utf-8')

st.download_button("Download Data", convert(display_data), "energy_data.csv")
