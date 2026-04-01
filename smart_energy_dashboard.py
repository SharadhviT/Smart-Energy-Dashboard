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
# 📁 DATA HANDLING
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

        cost = energy * 9

        rows.append([
            i,
            np.random.choice(["Apartment","Villa","Independent House"]),
            occupants,
            round(energy,2),
            round(cost,2),
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
    if os.path.exists(DATA_FILE):
        return pd.read_csv(DATA_FILE)
    else:
        return generate_data()

def save_data(df):
    df.to_csv(DATA_FILE, index=False)

if "data" not in st.session_state:
    st.session_state.data = load_data()

data = st.session_state.data.copy()

# =========================================================
# 🧹 CLEANING
# =========================================================
data['Daily Energy (kWh)'] = pd.to_numeric(data['Daily Energy (kWh)'], errors='coerce')
data['Cost (₹)'] = pd.to_numeric(data['Cost (₹)'], errors='coerce')
data.dropna(inplace=True)

for col in ['AC Used','LED Used','Renewable','Implemented Tips?']:
    data[col] = data[col].astype(str).str.title()

# =========================================================
# 💱 CURRENCY
# =========================================================
data['Cost (HKD)'] = data['Cost (₹)'] * 0.096
data['Cost (USD)'] = data['Cost (₹)'] * 0.012

currency = st.sidebar.radio("💱 Currency", ["INR","HKD","USD"])

cost_col = {
    "INR": "Cost (₹)",
    "HKD": "Cost (HKD)",
    "USD": "Cost (USD)"
}[currency]

symbol = {"INR":"₹","HKD":"HKD","USD":"$"}[currency]

# =========================================================
# 🔎 FILTERS
# =========================================================
st.sidebar.header("🔎 Filters")

household_types = st.sidebar.multiselect(
    "Household Type",
    data['Household Type'].unique(),
    default=data['Household Type'].unique()
)

filtered = data[
    (data['Household Type'].isin(household_types))
]

display_data = filtered if not filtered.empty else data.copy()

# =========================================================
# ➕ ADD / DELETE
# =========================================================
st.sidebar.header("⚙️ Manage")

with st.sidebar.form("add"):
    hh = st.selectbox("Type", ["Apartment","Villa","Independent House"])
    occ = st.number_input("Occupants",1,10,3)
    energy = st.number_input("Energy",1,200,30)
    ac = st.selectbox("AC",["Yes","No"])
    led = st.selectbox("LED",["Yes","No"])
    ren = st.selectbox("Renewable",["Yes","No"])
    tips = st.selectbox("Tips",["Yes","No"])

    if st.form_submit_button("Add"):
        new_id = int(data['Household ID'].max()) + 1
        new = pd.DataFrame([[new_id,hh,occ,energy,energy*9,ac,led,ren,tips]],
        columns=data.columns)

        updated = pd.concat([data,new], ignore_index=True)
        save_data(updated)
        st.session_state.data = updated
        st.rerun()

if not data.empty:
    del_id = st.sidebar.selectbox("Delete ID", data['Household ID'])
    if st.sidebar.button("Delete"):
        updated = data[data['Household ID'] != del_id]
        save_data(updated)
        st.session_state.data = updated
        st.rerun()

# =========================================================
# 📊 METRICS
# =========================================================
st.title("💡 Smart Energy Optimization System")

avg_energy = display_data['Daily Energy (kWh)'].mean()
avg_cost = display_data[cost_col].mean()

c1,c2 = st.columns(2)
c1.metric("Avg Energy", f"{avg_energy:.2f} kWh")
c2.metric("Avg Cost", f"{symbol} {avg_cost:.2f}")

# =========================================================
# 📈 VISUALS
# =========================================================
def show(fig): st.pyplot(fig)

# Line
fig, ax = plt.subplots()
ax.plot(display_data['Household ID'], display_data['Daily Energy (kWh)'])
ax.set(title="Energy per Household")
show(fig)

# Histogram
fig, ax = plt.subplots()
ax.hist(display_data['Daily Energy (kWh)'], bins=10)
show(fig)

# Scatter
fig, ax = plt.subplots()
sns.regplot(x='Daily Energy (kWh)', y=cost_col, data=display_data, ax=ax)
show(fig)

# =========================================================
# 🤖 REGRESSION
# =========================================================
st.subheader("📊 Regression Model")

reg = display_data.copy()

for col in ['AC Used','LED Used','Renewable']:
    reg[col] = LabelEncoder().fit_transform(reg[col])

X = reg[['Occupants','AC Used','LED Used','Renewable']]
y = reg['Daily Energy (kWh)']

model = LinearRegression().fit(X,y)
st.write(f"Model Accuracy (R²): {model.score(X,y):.3f}")

# =========================================================
# 🔍 CORRELATION (FIXED)
# =========================================================
st.subheader("📊 Correlation Matrix")

numeric = reg[['Daily Energy (kWh)','Occupants','AC Used','LED Used','Renewable']]

fig, ax = plt.subplots()
sns.heatmap(numeric.corr(), annot=True, cmap='coolwarm', ax=ax)
show(fig)

# =========================================================
# 🔮 SIMULATION
# =========================================================
st.subheader("🔮 Simulation")

impact = st.slider("LED Efficiency %",5,30,15)/100

sim = display_data.copy()
sim.loc[sim['LED Used']=="No",'Daily Energy (kWh)'] *= (1-impact)
sim['Cost (₹)'] = sim['Daily Energy (kWh)']*9

st.write(f"New Avg Cost: {symbol} {sim[cost_col].mean():.2f}")

# =========================================================
# 🧠 AI RECOMMENDATIONS (FIXED)
# =========================================================
st.subheader("🧠 AI Recommendations")

avg_ac = display_data[display_data['AC Used']=="Yes"]['Daily Energy (kWh)'].mean()
avg_no_ac = display_data[display_data['AC Used']=="No"]['Daily Energy (kWh)'].mean()

avg_led = display_data[display_data['LED Used']=="Yes"][cost_col].mean()
avg_no_led = display_data[display_data['LED Used']=="No"][cost_col].mean()

avg_ren = display_data[display_data['Renewable']=="Yes"]['Daily Energy (kWh)'].mean()
avg_no_ren = display_data[display_data['Renewable']=="No"]['Daily Energy (kWh)'].mean()

if avg_no_led > avg_led:
    st.success("💡 Switching to LED reduces cost significantly.")

if avg_ac > avg_no_ac:
    st.warning("❄️ AC usage increases energy consumption.")

if avg_ren < avg_no_ren:
    st.success("🌞 Renewable energy reduces consumption.")

# =========================================================
# 🏆 OPTIMIZATION
# =========================================================
st.subheader("🏆 Best Setup")

base_occ = int(display_data['Occupants'].mean())

configs = []
for ac in [0,1]:
    for led in [0,1]:
        for ren in [0,1]:
            pred = model.predict([[base_occ,ac,led,ren]])[0]
            configs.append([ac,led,ren,pred,pred*9])

opt = pd.DataFrame(configs, columns=["AC","LED","REN","Energy","Cost"])

best = opt.loc[opt['Cost'].idxmin()]
st.success(f"Best Cost: ₹ {best['Cost']:.2f}")

# =========================================================
# DOWNLOAD
# =========================================================
st.download_button("Download CSV", display_data.to_csv(index=False), "energy.csv")
