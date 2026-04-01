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
This dashboard analyzes energy consumption across households using **statistical modeling and regression analysis**.
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
st.sidebar.header("🔎 Filters")
filtered_data = data.copy()

# ---------- Safe Mean ----------
def safe_mean(series, fallback):
    return fallback if series.empty else series.mean()

# ---------- Metrics ----------
avg_energy = safe_mean(filtered_data['Daily Energy (kWh)'], data['Daily Energy (kWh)'].mean())
avg_cost = safe_mean(filtered_data[cost_col], data[cost_col].mean())
tips_percent = (filtered_data['Implemented Tips?'] == 'Yes').mean() * 100
renewable_percent = (filtered_data['Renewable'] == 'Yes').mean() * 100

st.subheader("📊 Key Metrics")
col1, col2, col3, col4 = st.columns(4)
col1.metric("Avg Energy (kWh)", f"{avg_energy:.2f}")
col2.metric(f"Avg Cost ({currency_symbol})", f"{avg_cost:.2f}")
col3.metric("% Tips Used", f"{tips_percent:.1f}%")
col4.metric("% Renewable", f"{renewable_percent:.1f}%")

# ---------- Charts ----------
st.subheader("📈 Energy Trend")
st.line_chart(filtered_data['Daily Energy (kWh)'])

st.subheader("💰 Cost per Household")
st.bar_chart(filtered_data.set_index('Household ID')[cost_col])

# ---------- Analysis ----------
display_data = filtered_data.copy()

avg_cost_led = safe_mean(display_data[display_data['LED Used']=='Yes'][cost_col], avg_cost)
avg_cost_non_led = safe_mean(display_data[display_data['LED Used']=='No'][cost_col], avg_cost)

avg_ac = safe_mean(display_data[display_data['AC Used']=='Yes']['Daily Energy (kWh)'], avg_energy)
avg_no_ac = safe_mean(display_data[display_data['AC Used']=='No']['Daily Energy (kWh)'], avg_energy)

renewable_avg = safe_mean(display_data[display_data['Renewable']=='Yes']['Daily Energy (kWh)'], avg_energy)
non_renewable_avg = safe_mean(display_data[display_data['Renewable']=='No']['Daily Energy (kWh)'], avg_energy)

# ---------- ✅ FIXED RECOMMENDATIONS ----------
st.subheader("📝 Data-Driven Recommendations")

recommendations = []

# LED
if avg_cost_led < avg_cost_non_led:
    savings = avg_cost_non_led - avg_cost_led
    recommendations.append(f"💡 LED bulbs save ~{currency_symbol} {savings:.2f} per day per household.")

# AC
if avg_ac > avg_no_ac:
    increase = ((avg_ac - avg_no_ac) / avg_no_ac * 100) if avg_no_ac != 0 else 0
    recommendations.append(f"❄️ AC usage increases energy by ~{increase:.1f}% — optimize usage.")

# Renewable
if renewable_avg < non_renewable_avg:
    recommendations.append("🌞 Renewable energy users consume less energy — promote solar adoption.")

# Awareness
if tips_percent < 50:
    recommendations.append("📉 Less than 50% households follow energy-saving tips — awareness needed.")

# Strong threshold (advanced logic)
if abs(avg_cost_non_led - avg_cost_led) < 1:
    recommendations.append("⚖️ LED vs non-LED difference is minimal — investigate further data.")

# Fallback
if not recommendations:
    recommendations.append("✅ Energy usage patterns are already efficient.")

for rec in recommendations:
    st.write(rec)

# ---------- Regression ----------
st.subheader("📊 Regression Analysis")

reg_data = display_data.copy()
for col in ['AC Used','LED Used','Renewable']:
    reg_data[col] = LabelEncoder().fit_transform(reg_data[col])

X = reg_data[['Occupants','AC Used','LED Used','Renewable']]
y = reg_data['Daily Energy (kWh)']

model = LinearRegression().fit(X, y)

coeffs = pd.DataFrame({
    'Feature': X.columns,
    'Impact': model.coef_
})

st.write("### Feature Impact")
st.dataframe(coeffs)

# ---------- Correlation ----------
st.subheader("🔍 Correlation Matrix")

fig, ax = plt.subplots()
sns.heatmap(reg_data.corr(), annot=True, cmap='coolwarm', ax=ax)
st.pyplot(fig)

# ---------- Download ----------
st.subheader("💾 Download Data")

@st.cache_data
def convert(df):
    return df.to_csv(index=False).encode('utf-8')

csv = convert(display_data)

st.download_button(
    "Download CSV",
    csv,
    "energy_data.csv",
    "text/csv"
)
