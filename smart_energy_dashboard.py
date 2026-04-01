import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import LabelEncoder
import os

plt.style.use('ggplot')

# =========================================================
# 📁 DATA
# =========================================================
DATA_FILE = "energy_data_100.csv"

def generate_data():
    np.random.seed(42)
    data = []

    for i in range(1, 101):
        occupants = np.random.randint(1, 7)
        ac = np.random.choice(["Yes","No"])
        led = np.random.choice(["Yes","No"])
        ren = np.random.choice(["Yes","No"])

        energy = np.random.uniform(10, 60)
        if ac == "Yes": energy += 15
        if led == "Yes": energy -= 5
        if ren == "Yes": energy -= 3

        data.append([
            i,
            np.random.choice(["Apartment","Villa","Independent House"]),
            occupants,
            round(energy,2),
            round(energy*9,2),
            ac, led, ren,
            np.random.choice(["Yes","No"])
        ])

    df = pd.DataFrame(data, columns=[
        "Household ID","Household Type","Occupants",
        "Daily Energy (kWh)","Cost (₹)",
        "AC Used","LED Used","Renewable","Implemented Tips?"
    ])

    df.to_csv(DATA_FILE, index=False)
    return df

def load_data():
    if os.path.exists(DATA_FILE):
        return pd.read_csv(DATA_FILE)
    return generate_data()

data = load_data()

# =========================================================
# 🧹 CLEAN
# =========================================================
data['Daily Energy (kWh)'] = pd.to_numeric(data['Daily Energy (kWh)'], errors='coerce')
data['Cost (₹)'] = pd.to_numeric(data['Cost (₹)'], errors='coerce')
data = data.dropna()

for col in ['AC Used','LED Used','Renewable','Implemented Tips?']:
    data[col] = data[col].astype(str).str.title()

# =========================================================
# 💱 CURRENCY
# =========================================================
data['Cost (HKD)'] = data['Cost (₹)'] * 0.096
data['Cost (USD)'] = data['Cost (₹)'] * 0.012

currency = st.sidebar.radio("Currency", ["INR","HKD","USD"])

cost_col = {
    "INR": "Cost (₹)",
    "HKD": "Cost (HKD)",
    "USD": "Cost (USD)"
}[currency]

symbol = {"INR":"₹","HKD":"HKD","USD":"$"}[currency]

# =========================================================
# 📊 TITLE
# =========================================================
st.title("💡 Smart Energy Optimization Dashboard")

# =========================================================
# 📊 METRICS
# =========================================================
st.metric("Avg Energy", f"{data['Daily Energy (kWh)'].mean():.2f} kWh")
st.metric("Avg Cost", f"{symbol} {data[cost_col].mean():.2f}")

# =========================================================
# 📈 PLOTS
# =========================================================
fig, ax = plt.subplots()
ax.plot(data['Household ID'], data['Daily Energy (kWh)'])
ax.set_title("Energy per Household")
st.pyplot(fig)

# =========================================================
# 🤖 REGRESSION
# =========================================================
reg = data.copy()

for col in ['AC Used','LED Used','Renewable']:
    reg[col] = LabelEncoder().fit_transform(reg[col])

X = reg[['Occupants','AC Used','LED Used','Renewable']]
y = reg['Daily Energy (kWh)']

model = LinearRegression().fit(X, y)
st.write(f"Model R²: {model.score(X,y):.3f}")

# =========================================================
# 🔍 CORRELATION
# =========================================================
fig, ax = plt.subplots()
sns.heatmap(reg[['Daily Energy (kWh)','Occupants','AC Used','LED Used','Renewable']].corr(),
            annot=True, ax=ax)
st.pyplot(fig)

# =========================================================
# 🔮 SIMULATION (100% SAFE)
# =========================================================
st.subheader("🔮 LED Impact Simulation")

impact = st.slider("LED Efficiency %", 5, 30, 15) / 100

sim = data.copy()

# ✅ SAFE NUMPY OPERATION (NO LOC, NO ERROR)
energy_array = sim['Daily Energy (kWh)'].astype(float).values

mask = (sim['LED Used'] == "No").values

energy_array = np.where(mask, energy_array * (1 - impact), energy_array)

sim['Daily Energy (kWh)'] = energy_array

# Recalculate cost
sim['Cost (₹)'] = sim['Daily Energy (kWh)'] * 9
sim['Cost (HKD)'] = sim['Cost (₹)'] * 0.096
sim['Cost (USD)'] = sim['Cost (₹)'] * 0.012

st.write(f"New Avg Cost: {symbol} {sim[cost_col].mean():.2f}")

# =========================================================
# 🧠 AI RECOMMENDATIONS
# =========================================================
st.subheader("🧠 AI Recommendations")

avg_ac = data[data['AC Used']=="Yes"]['Daily Energy (kWh)'].mean()
avg_no_ac = data[data['AC Used']=="No"]['Daily Energy (kWh)'].mean()

avg_led = data[data['LED Used']=="Yes"][cost_col].mean()
avg_no_led = data[data['LED Used']=="No"][cost_col].mean()

avg_ren = data[data['Renewable']=="Yes"]['Daily Energy (kWh)'].mean()
avg_no_ren = data[data['Renewable']=="No"]['Daily Energy (kWh)'].mean()

if avg_no_led > avg_led:
    st.success("💡 LED reduces cost")

if avg_ac > avg_no_ac:
    st.warning("❄️ AC increases energy usage")

if avg_ren < avg_no_ren:
    st.success("🌞 Renewable reduces energy")

# =========================================================
# 📥 DOWNLOAD
# =========================================================
st.download_button("Download CSV", data.to_csv(index=False), "energy.csv")
