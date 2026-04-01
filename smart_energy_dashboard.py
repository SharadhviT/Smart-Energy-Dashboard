import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import LabelEncoder
import os
# ---------- Load Data ----------
data = pd.read_csv("energy_data_100.csv")

plt.style.use('ggplot')

# =========================================================
# 📁 DATA HANDLING
# =========================================================
DATA_FILE = "energy_data_100.csv"

def load_data():
    if os.path.exists(DATA_FILE):
        return pd.read_csv(DATA_FILE)
    else:
        return pd.DataFrame(columns=[
            "Household ID","Household Type","Occupants",
            "Daily Energy (kWh)","Cost (₹)",
            "AC Used","LED Used","Renewable","Implemented Tips?"
        ])

def save_data(df):
    df.to_csv(DATA_FILE, index=False)

if "data" not in st.session_state:
    st.session_state.data = load_data()

data = st.session_state.data.copy()

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
    "Household Type", data['Household Type'].unique(),
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
# ⚙️ SIDEBAR - ADD / DELETE
# =========================================================
st.sidebar.header("⚙️ Manage Households")

with st.sidebar.form("add_form"):
    st.subheader("➕ Add Household")
    hh_type = st.selectbox("Household Type", ["Apartment","Villa","Independent House"])
    occupants = st.number_input("Occupants",1,10,3)
    energy = st.number_input("Daily Energy (kWh)",1,200,30)
    ac = st.selectbox("AC Used",["Yes","No"])
    led = st.selectbox("LED Used",["Yes","No"])
    renewable = st.selectbox("Renewable",["Yes","No"])
    tips = st.selectbox("Implemented Tips?",["Yes","No"])

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
# 📊 METRICS
# =========================================================
st.title("💡 Smart Energy Optimization System")

avg_energy = display_data['Daily Energy (kWh)'].mean()
avg_cost = display_data[cost_col].mean()

c1,c2 = st.columns(2)
c1.metric("Avg Energy", f"{avg_energy:.2f} kWh")
c2.metric("Avg Cost", f"{symbol} {avg_cost:.2f}")

# =========================================================
# 📊 GRAPHS
# =========================================================

def show_plot(fig):
    st.pyplot(fig)

# Line
fig, ax = plt.subplots()
ax.plot(display_data['Household ID'], display_data['Daily Energy (kWh)'])
ax.set(title="Energy per Household", xlabel="Household ID", ylabel="kWh")
show_plot(fig)

# Bar
fig, ax = plt.subplots()
ax.bar(display_data['Household ID'], display_data[cost_col])
ax.set(title="Cost per Household", xlabel="Household ID", ylabel=symbol)
show_plot(fig)

# Histogram
fig, ax = plt.subplots()
ax.hist(display_data['Daily Energy (kWh)'], bins=10)
ax.set(title="Energy Distribution", xlabel="kWh", ylabel="Count")
show_plot(fig)

# Scatter
fig, ax = plt.subplots()
sns.regplot(x='Daily Energy (kWh)', y=cost_col, data=display_data, ax=ax)
ax.set(title="Energy vs Cost", xlabel="Energy", ylabel="Cost")
show_plot(fig)

# Box
fig, ax = plt.subplots()
sns.boxplot(x='AC Used', y='Daily Energy (kWh)', data=display_data, ax=ax)
ax.set(title="AC Impact", xlabel="AC", ylabel="Energy")
show_plot(fig)

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
# 🔍 CORRELATION
# =========================================================
numeric = reg[['Daily Energy (kWh)','Occupants','AC Used','LED Used','Renewable']]

fig, ax = plt.subplots()
sns.heatmap(numeric.corr(), annot=True, cmap='coolwarm', ax=ax)
ax.set_title("Correlation Matrix")
show_plot(fig)

# =========================================================
# 🔮 SIMULATION
# =========================================================
st.subheader("🔮 Simulation")

sim = display_data.copy()
sim['Daily Energy (kWh)'] = sim['Daily Energy (kWh)'].astype(float)

impact = st.slider("LED Efficiency %",5,30,15)/100
sim.loc[sim['LED Used']=="No",'Daily Energy (kWh)'] *= (1-impact)

sim['Cost (₹)'] = sim['Daily Energy (kWh)']*9

new_cost = sim[cost_col].mean()
st.write(f"New Avg Cost: {symbol} {new_cost:.2f}")

# =========================================================
# 📊 OPTIMIZATION ENGINE
# =========================================================
st.subheader("📊 Best Cost Optimization")

base_occ = int(display_data['Occupants'].mean())

options = [
("Yes","Yes","Yes"),("Yes","Yes","No"),("Yes","No","Yes"),
("Yes","No","No"),("No","Yes","Yes"),("No","Yes","No"),
("No","No","Yes"),("No","No","No")
]

results = []

for ac,led,ren in options:
    temp = pd.DataFrame({
        "Occupants":[base_occ],
        "AC Used":[1 if ac=="Yes" else 0],
        "LED Used":[1 if led=="Yes" else 0],
        "Renewable":[1 if ren=="Yes" else 0]
    })

    energy = model.predict(temp)[0]
    cost = energy * 9

    results.append([ac,led,ren,round(energy,2),round(cost,2)])

opt_df = pd.DataFrame(results, columns=[
    "AC","LED","Renewable","Energy","Cost"
])

st.dataframe(opt_df)

best = opt_df.loc[opt_df['Cost'].idxmin()]

st.success(f"""
Best Setup:
AC: {best['AC']}
LED: {best['LED']}
Renewable: {best['Renewable']}

Cost: ₹ {best['Cost']}
""")

fig, ax = plt.subplots()
ax.bar(range(len(opt_df)), opt_df['Cost'])
ax.set(title="Cost Across Scenarios", xlabel="Scenario", ylabel="₹")
show_plot(fig)

# =========================================================
# DOWNLOAD
# =========================================================
@st.cache_data
def convert(df):
    return df.to_csv(index=False).encode('utf-8')

st.download_button("Download Data", convert(display_data), "energy.csv")
