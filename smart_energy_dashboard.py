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
# 📁 DEFAULT DATA (100 HOUSEHOLDS)
# =========================================================
def generate_sample_data(n=100):
    np.random.seed(42)
    return pd.DataFrame({
        "Household ID": range(1, n+1),
        "Household Type": np.random.choice(["Apartment","Villa","Independent House"], n),
        "Occupants": np.random.randint(1, 7, n),
        "Daily Energy (kWh)": np.random.randint(10, 80, n),
        "AC Used": np.random.choice(["Yes","No"], n),
        "LED Used": np.random.choice(["Yes","No"], n),
        "Renewable": np.random.choice(["Yes","No"], n),
        "Implemented Tips?": np.random.choice(["Yes","No"], n)
    })

DATA_FILE = "energy_data_100.csv"

def load_data():
    if os.path.exists(DATA_FILE):
        return pd.read_csv(DATA_FILE)
    else:
        df = generate_sample_data()
        df["Cost (₹)"] = df["Daily Energy (kWh)"] * 9
        return df

def save_data(df):
    df.to_csv(DATA_FILE, index=False)

# Session state
if "data" not in st.session_state:
    st.session_state.data = load_data()

data = st.session_state.data.copy()

# =========================================================
# 📤 FILE UPLOAD OPTION
# =========================================================
st.sidebar.header("📤 Upload Dataset")
uploaded_file = st.sidebar.file_uploader("Upload CSV", type=["csv"])

if uploaded_file:
    data = pd.read_csv(uploaded_file)
    st.session_state.data = data
    st.sidebar.success("Dataset uploaded!")

# =========================================================
# 🧹 CLEAN DATA
# =========================================================
data['Daily Energy (kWh)'] = pd.to_numeric(data['Daily Energy (kWh)'], errors='coerce')
data['Cost (₹)'] = pd.to_numeric(data['Cost (₹)'], errors='coerce')
data.dropna(inplace=True)

for col in ['AC Used','LED Used','Renewable','Implemented Tips?']:
    data[col] = data[col].astype(str).str.title()

# =========================================================
# 💱 CURRENCY
# =========================================================
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

# =========================================================
# 🔎 FILTERS
# =========================================================
st.sidebar.header("🔎 Filters")

household_types = st.sidebar.multiselect(
    "Household Type",
    data['Household Type'].unique(),
    default=data['Household Type'].unique()
)

ac_filter = st.sidebar.multiselect("AC Used",["Yes","No"],["Yes","No"])
led_filter = st.sidebar.multiselect("LED Used",["Yes","No"],["Yes","No"])
renewable_filter = st.sidebar.multiselect("Renewable",["Yes","No"],["Yes","No"])
tips_filter = st.sidebar.multiselect("Implemented Tips?",["Yes","No"],["Yes","No"])

filtered = data[
    (data['Household Type'].isin(household_types)) &
    (data['AC Used'].isin(ac_filter)) &
    (data['LED Used'].isin(led_filter)) &
    (data['Renewable'].isin(renewable_filter)) &
    (data['Implemented Tips?'].isin(tips_filter))
]

display_data = filtered if not filtered.empty else data.copy()

# =========================================================
# ⚙️ ADD / DELETE
# =========================================================
st.sidebar.header("⚙️ Manage Households")

with st.sidebar.form("add_form"):
    st.subheader("➕ Add Household")
    hh_type = st.selectbox("Type", ["Apartment","Villa","Independent House"])
    occupants = st.number_input("Occupants",1,10,3)
    energy = st.number_input("Daily Energy",1,200,30)
    ac = st.selectbox("AC",["Yes","No"])
    led = st.selectbox("LED",["Yes","No"])
    renewable = st.selectbox("Renewable",["Yes","No"])
    tips = st.selectbox("Tips",["Yes","No"])

    if st.form_submit_button("Add"):
        new_id = int(data['Household ID'].max()) + 1 if not data.empty else 1
        new_row = {
            "Household ID": new_id,
            "Household Type": hh_type,
            "Occupants": occupants,
            "Daily Energy (kWh)": float(energy),
            "Cost (₹)": float(energy)*9,
            "AC Used": ac,
            "LED Used": led,
            "Renewable": renewable,
            "Implemented Tips?": tips
        }
        updated = pd.concat([data, pd.DataFrame([new_row])], ignore_index=True)
        save_data(updated)
        st.session_state.data = updated
        st.success(f"Added Household {new_id}")
        st.rerun()

st.sidebar.subheader("🗑️ Delete Household")
if not data.empty:
    del_id = st.sidebar.selectbox("Select ID", sorted(data['Household ID'].unique()))
    if st.sidebar.button("Delete"):
        updated = data[data['Household ID'] != del_id]
        save_data(updated)
        st.session_state.data = updated
        st.success(f"Deleted Household {del_id}")
        st.rerun()

# =========================================================
# 📊 TITLE + REPORT LINE (YOUR STATEMENT)
# =========================================================
st.title("💡 Smart Energy Awareness & Optimization Dashboard")

st.info("""
I have uploaded a technical report on my Smart Energy Awareness and Optimization Dashboard. 
This project utilizes regression and statistical modeling to identify energy inefficiencies— 
a direct application of the analytical skills that earned me a 100/100 in Statistics.
""")

# =========================================================
# 📊 METRICS
# =========================================================
avg_energy = display_data['Daily Energy (kWh)'].mean()
avg_cost = display_data[cost_col].mean()

c1,c2 = st.columns(2)
c1.metric("Avg Energy", f"{avg_energy:.2f} kWh")
c2.metric("Avg Cost", f"{symbol} {avg_cost:.2f}")

# =========================================================
# 📊 VISUALS
# =========================================================
fig, ax = plt.subplots()
ax.plot(display_data['Household ID'], display_data['Daily Energy (kWh)'])
ax.set(title="Energy per Household")
st.pyplot(fig)

fig, ax = plt.subplots()
ax.bar(display_data['Household ID'], display_data[cost_col])
ax.set(title="Cost per Household")
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

model = LinearRegression().fit(X,y)
r2 = model.score(X,y)

st.write(f"Model R²: {r2:.3f}")

# =========================================================
# 📊 CORRELATION
# =========================================================
fig, ax = plt.subplots()
sns.heatmap(reg.corr(), annot=True, cmap='coolwarm', ax=ax)
st.pyplot(fig)

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
# 📊 RECOMMENDATIONS (FIXED)
# =========================================================
st.subheader("📊 Data-Driven Recommendations")

avg_led = display_data[display_data['LED Used']=="Yes"]['Daily Energy (kWh)'].mean()
avg_non_led = display_data[display_data['LED Used']=="No"]['Daily Energy (kWh)'].mean()

avg_ac = display_data[display_data['AC Used']=="Yes"]['Daily Energy (kWh)'].mean()
avg_no_ac = display_data[display_data['AC Used']=="No"]['Daily Energy (kWh)'].mean()

if avg_led < avg_non_led:
    st.write("✔ LED usage significantly reduces energy consumption")

if avg_ac > avg_no_ac:
    st.write("✔ AC usage is a major contributor to high energy consumption")

# =========================================================
# 📥 DOWNLOAD
# =========================================================
st.download_button("Download Data", display_data.to_csv(index=False), "energy.csv")
