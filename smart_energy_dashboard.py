import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import LabelEncoder
import numpy as np
import os

plt.style.use('ggplot')

# =========================================================
# 📁 DATA
# =========================================================
DATA_FILE = "energy_data_100.csv"

def generate_data():
    np.random.seed(42)
    rows = []
    for i in range(1, 101):
        occupants = np.random.randint(1, 7)
        ac = np.random.choice(["Yes","No"])
        led = np.random.choice(["Yes","No"])
        renewable = np.random.choice(["Yes","No"])

        energy = np.random.uniform(10, 60)
        if ac == "Yes": energy += 15
        if led == "Yes": energy -= 5
        if renewable == "Yes": energy -= 3

        rows.append([
            i,
            np.random.choice(["Apartment","Villa","Independent House"]),
            occupants,
            round(energy,2),
            round(energy*9,2),
            ac, led, renewable,
            np.random.choice(["Yes","No"])
        ])

    df = pd.DataFrame(rows, columns=[
        "Household ID","Household Type","Occupants",
        "Daily Energy (kWh)","Cost (₹)",
        "AC Used","LED Used","Renewable","Implemented Tips?"
    ])

    df.to_csv(DATA_FILE, index=False)
    return df

def load_data():
    return pd.read_csv(DATA_FILE) if os.path.exists(DATA_FILE) else generate_data()

def save_data(df):
    df.to_csv(DATA_FILE, index=False)

if "data" not in st.session_state:
    st.session_state.data = load_data()

data = st.session_state.data.copy()

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
# 🔎 FILTER
# =========================================================
display_data = data.copy()

# =========================================================
# 📊 METRICS
# =========================================================
st.title("💡 Smart Energy Optimization System")

st.metric("Avg Energy", f"{display_data['Daily Energy (kWh)'].mean():.2f} kWh")
st.metric("Avg Cost", f"{symbol} {display_data[cost_col].mean():.2f}")

# =========================================================
# 📈 VISUALS
# =========================================================
fig, ax = plt.subplots()
ax.plot(display_data['Household ID'], display_data['Daily Energy (kWh)'])
st.pyplot(fig)

# =========================================================
# 🤖 MODEL
# =========================================================
reg = display_data.copy()

for col in ['AC Used','LED Used','Renewable']:
    reg[col] = LabelEncoder().fit_transform(reg[col])

X = reg[['Occupants','AC Used','LED Used','Renewable']]
y = reg['Daily Energy (kWh)']

model = LinearRegression().fit(X,y)

st.write(f"Model R²: {model.score(X,y):.3f}")

# =========================================================
# 🔍 CORRELATION
# =========================================================
fig, ax = plt.subplots()
sns.heatmap(reg[['Daily Energy (kWh)','Occupants','AC Used','LED Used','Renewable']].corr(),
            annot=True, ax=ax)
st.pyplot(fig)

# =========================================================
# 🔮 SIMULATION (FINAL FIX)
# =========================================================
st.subheader("Simulation")

impact = st.slider("LED Efficiency %", 5, 30, 15) / 100

sim = display_data.copy()

# ✅ FULL SAFE PIPELINE
sim_energy = pd.to_numeric(sim['Daily Energy (kWh)'], errors='coerce')

sim_energy = np.where(
    sim['LED Used'] == "No",
    sim_energy * (1 - impact),
    sim_energy
)

# ✅ Assign back cleanly (NO .loc)
sim = sim.assign(**{"Daily Energy (kWh)": sim_energy})

# Recalculate cost
sim['Cost (₹)'] = sim['Daily Energy (kWh)'] * 9
sim['Cost (HKD)'] = sim['Cost (₹)'] * 0.096
sim['Cost (USD)'] = sim['Cost (₹)'] * 0.012

st.write(f"New Avg Cost: {symbol} {sim[cost_col].mean():.2f}")

# =========================================================
# 🧠 AI RECOMMENDATIONS (FIXED)
# =========================================================
st.subheader("AI Recommendations")

avg_ac = display_data[display_data['AC Used']=="Yes"]['Daily Energy (kWh)'].mean()
avg_no_ac = display_data[display_data['AC Used']=="No"]['Daily Energy (kWh)'].mean()

avg_led = display_data[display_data['LED Used']=="Yes"][cost_col].mean()
avg_no_led = display_data[display_data['LED Used']=="No"][cost_col].mean()

avg_ren = display_data[display_data['Renewable']=="Yes"]['Daily Energy (kWh)'].mean()
avg_no_ren = display_data[display_data['Renewable']=="No"]['Daily Energy (kWh)'].mean()

if avg_no_led > avg_led:
    st.success("Switch to LED to reduce cost")

if avg_ac > avg_no_ac:
    st.warning("Reduce AC usage")

if avg_ren < avg_no_ren:
    st.success("Use renewable energy")

# =========================================================
# DOWNLOAD
# =========================================================
st.download_button("Download CSV", display_data.to_csv(index=False), "energy.csv")
