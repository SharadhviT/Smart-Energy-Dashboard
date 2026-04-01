import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import LabelEncoder

plt.style.use('ggplot')

# ---------- Page Setup ----------
st.set_page_config(layout="wide", page_title="Smart Energy Dashboard")
st.title("💡 Smart Energy Awareness & Optimization Dashboard")

# ---------- Load Data ----------
data = pd.read_csv("energy_data_100.csv")

# Ensure float for calculations
data['Daily Energy (kWh)'] = data['Daily Energy (kWh)'].astype(float)

# ---------- Clean Data ----------
for col in ['AC Used','LED Used','Renewable','Implemented Tips?']:
    data[col] = data[col].str.title()

# ---------- Currency ----------
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

currency_symbol = {
    "INR": "₹",
    "HKD": "HKD",
    "USD": "$"
}[currency]

# ---------- Filters ----------
household_types = st.sidebar.multiselect("Household Type", data['Household Type'].unique(), default=data['Household Type'].unique())
ac_filter = st.sidebar.multiselect("AC Used", ['Yes','No'], default=['Yes','No'])
led_filter = st.sidebar.multiselect("LED Used", ['Yes','No'], default=['Yes','No'])
renewable_filter = st.sidebar.multiselect("Renewable", ['Yes','No'], default=['Yes','No'])
tips_filter = st.sidebar.multiselect("Tips Used", ['Yes','No'], default=['Yes','No'])

filtered_data = data[
    (data['Household Type'].isin(household_types)) &
    (data['AC Used'].isin(ac_filter)) &
    (data['LED Used'].isin(led_filter)) &
    (data['Renewable'].isin(renewable_filter)) &
    (data['Implemented Tips?'].isin(tips_filter))
]

display_data = filtered_data if not filtered_data.empty else data

# ---------- Metrics ----------
def safe_mean(series, fallback):
    return fallback if series.empty else series.mean()

avg_energy = safe_mean(display_data['Daily Energy (kWh)'], data['Daily Energy (kWh)'].mean())
avg_cost = safe_mean(display_data[cost_col], data[cost_col].mean())

st.subheader("📊 Key Metrics")
c1,c2 = st.columns(2)
c1.metric("Avg Energy", f"{avg_energy:.2f} kWh")
c2.metric("Avg Cost", f"{currency_symbol} {avg_cost:.2f}")

# ---------- GRAPH 1: Energy Line ----------
fig, ax = plt.subplots()
ax.plot(display_data['Household ID'], display_data['Daily Energy (kWh)'])
ax.set_title("Daily Energy Usage per Household")
ax.set_xlabel("Household ID")
ax.set_ylabel("Energy (kWh)")
st.pyplot(fig)

# ---------- GRAPH 2: Cost Bar ----------
fig, ax = plt.subplots()
ax.bar(display_data['Household ID'], display_data[cost_col])
ax.set_title(f"Cost per Household ({currency_symbol})")
ax.set_xlabel("Household ID")
ax.set_ylabel(f"Cost ({currency_symbol})")
st.pyplot(fig)

# ---------- GRAPH 3: Pie Tips ----------
counts = display_data['Implemented Tips?'].value_counts()
fig, ax = plt.subplots()
ax.pie(counts, labels=counts.index, autopct='%1.1f%%')
ax.set_title("Energy Saving Tips Adoption")
st.pyplot(fig)

# ---------- GRAPH 4: Pie Renewable ----------
counts2 = display_data['Renewable'].value_counts()
fig, ax = plt.subplots()
ax.pie(counts2, labels=counts2.index, autopct='%1.1f%%')
ax.set_title("Renewable Energy Adoption")
st.pyplot(fig)

# ---------- GRAPH 5: Boxplot ----------
fig, ax = plt.subplots()
sns.boxplot(x='AC Used', y='Daily Energy (kWh)', data=display_data, ax=ax)
ax.set_title("AC Usage vs Energy Consumption")
ax.set_xlabel("AC Usage")
ax.set_ylabel("Energy (kWh)")
st.pyplot(fig)

# ---------- GRAPH 6: Scatter ----------
fig, ax = plt.subplots()
sns.scatterplot(x='Occupants', y='Daily Energy (kWh)', hue='LED Used', data=display_data, ax=ax)
ax.set_title("Energy vs Occupants")
ax.set_xlabel("Number of Occupants")
ax.set_ylabel("Energy (kWh)")
st.pyplot(fig)

# ---------- GRAPH 7: Energy per Occupant ----------
display_data = display_data.copy()
display_data['Energy per Occupant'] = display_data['Daily Energy (kWh)'] / display_data['Occupants']

fig, ax = plt.subplots()
ax.bar(display_data['Household ID'], display_data['Energy per Occupant'])
ax.set_title("Energy per Occupant")
ax.set_xlabel("Household ID")
ax.set_ylabel("Energy per Person (kWh)")
st.pyplot(fig)

# ---------- GRAPH 8: Household Type ----------
grouped = display_data.groupby('Household Type')['Daily Energy (kWh)'].mean()

fig, ax = plt.subplots()
ax.bar(grouped.index, grouped.values)
ax.set_title("Avg Energy by Household Type")
ax.set_xlabel("Household Type")
ax.set_ylabel("Energy (kWh)")
st.pyplot(fig)

# ---------- Regression ----------
reg_data = display_data.copy()
for col in ['AC Used','LED Used','Renewable']:
    reg_data[col] = LabelEncoder().fit_transform(reg_data[col])

X = reg_data[['Occupants','AC Used','LED Used','Renewable']]
y = reg_data['Daily Energy (kWh)']

model = LinearRegression().fit(X,y)

coeffs = pd.DataFrame({'Feature':X.columns,'Impact':model.coef_})

st.subheader("📊 Regression Impact")
st.dataframe(coeffs)

# Graph 9: Feature importance
fig, ax = plt.subplots()
ax.bar(coeffs['Feature'], coeffs['Impact'])
ax.set_title("Feature Impact on Energy")
ax.set_xlabel("Features")
ax.set_ylabel("Impact")
st.pyplot(fig)

# R2
st.write(f"Model Accuracy (R²): {model.score(X,y):.3f}")

# ---------- Correlation ----------
fig, ax = plt.subplots()
sns.heatmap(reg_data.corr(), annot=True, cmap='coolwarm', ax=ax)
ax.set_title("Correlation Matrix")
st.pyplot(fig)

# ---------- WHAT IF ----------
st.subheader("🔮 What If Analysis")

all_led = display_data.copy()
all_led['Daily Energy (kWh)'] = all_led['Daily Energy (kWh)'].astype(float)

reduction = st.slider("LED Efficiency %", 5, 30, 15)/100

mask = all_led['LED Used'] == 'No'
all_led.loc[mask, 'Daily Energy (kWh)'] *= (1 - reduction)

all_led['Cost (₹)'] = all_led['Daily Energy (kWh)'] * 9
all_led['Cost (HKD)'] = all_led['Cost (₹)'] * conversion_rate_hkd
all_led['Cost (USD)'] = all_led['Cost (₹)'] * conversion_rate_usd

new_cost = safe_mean(all_led[cost_col], avg_cost)
savings = (avg_cost - new_cost) * len(display_data)

st.write(f"If all use LED → Save {currency_symbol} {savings:.2f}/day")

# ---------- Recommendations ----------
st.subheader("📝 Recommendations")

recs = []

if savings > 0:
    recs.append("Switch to LED bulbs")

if not recs:
    recs.append("Energy usage is already efficient")

for r in recs:
    st.write(r)

# ---------- Download ----------
@st.cache_data
def convert(df):
    return df.to_csv(index=False).encode('utf-8')

st.download_button("Download CSV", convert(display_data), "data.csv")
