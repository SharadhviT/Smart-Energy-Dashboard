import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import LabelEncoder

plt.style.use('ggplot')

# ---------- PAGE ----------
st.set_page_config(layout="wide", page_title="Smart Energy Optimization System")
st.title("💡 Smart Energy Optimization & Policy Simulation System")

st.markdown("""
A data-driven analytical platform to model household energy consumption,  
evaluate efficiency strategies, and simulate real-world policy interventions.
""")

# ---------- LOAD ----------
data = pd.read_csv("energy_data_100.csv")
data['Daily Energy (kWh)'] = data['Daily Energy (kWh)'].astype(float)

for col in ['AC Used','LED Used','Renewable','Implemented Tips?']:
    data[col] = data[col].str.title()

# ---------- CURRENCY ----------
conversion_rate_hkd = 0.096
conversion_rate_usd = 0.012

data['Cost (HKD)'] = data['Cost (₹)'] * conversion_rate_hkd
data['Cost (USD)'] = data['Cost (₹)'] * conversion_rate_usd

currency = st.sidebar.radio("💱 Currency", ["INR","HKD","USD"])
cost_col = {"INR":"Cost (₹)","HKD":"Cost (HKD)","USD":"Cost (USD)"}[currency]
symbol = {"INR":"₹","HKD":"HKD","USD":"$"}[currency]

# ---------- FILTER ----------
st.sidebar.header("🔎 Filters")
filtered = data.copy()

display_data = filtered

# ---------- METRICS ----------
def safe_mean(series, fallback):
    return fallback if series.empty else series.mean()

avg_energy = safe_mean(display_data['Daily Energy (kWh)'], data['Daily Energy (kWh)'].mean())
avg_cost = safe_mean(display_data[cost_col], data[cost_col].mean())

c1,c2 = st.columns(2)
c1.metric("Avg Energy", f"{avg_energy:.2f} kWh")
c2.metric("Avg Cost", f"{symbol} {avg_cost:.2f}")

# =========================================================
# 📊 VISUAL ANALYTICS
# =========================================================

# 1 Line
fig, ax = plt.subplots()
ax.plot(display_data['Household ID'], display_data['Daily Energy (kWh)'])
ax.set(title="Energy per Household", xlabel="Household ID", ylabel="kWh")
st.pyplot(fig)

# 2 Cost
fig, ax = plt.subplots()
ax.bar(display_data['Household ID'], display_data[cost_col])
ax.set(title="Cost per Household", xlabel="Household ID", ylabel=symbol)
st.pyplot(fig)

# 3 Histogram
fig, ax = plt.subplots()
ax.hist(display_data['Daily Energy (kWh)'], bins=10)
ax.set(title="Energy Distribution", xlabel="kWh", ylabel="Count")
st.pyplot(fig)

# 4 Scatter + regression
fig, ax = plt.subplots()
sns.regplot(x='Daily Energy (kWh)', y=cost_col, data=display_data, ax=ax)
ax.set(title="Energy vs Cost", xlabel="Energy", ylabel="Cost")
st.pyplot(fig)

# 5 Box
fig, ax = plt.subplots()
sns.boxplot(x='AC Used', y='Daily Energy (kWh)', data=display_data, ax=ax)
ax.set(title="AC Impact", xlabel="AC Usage", ylabel="Energy")
st.pyplot(fig)

# 6 Grouped
group = display_data.groupby(['AC Used','LED Used'])['Daily Energy (kWh)'].mean().unstack()
fig, ax = plt.subplots()
group.plot(kind='bar', ax=ax)
ax.set(title="AC + LED Interaction", xlabel="AC Used", ylabel="Energy")
st.pyplot(fig)

# =========================================================
# 📊 REGRESSION MODEL
# =========================================================

st.subheader("📊 Predictive Modeling")

reg = display_data.copy()
for col in ['AC Used','LED Used','Renewable']:
    reg[col] = LabelEncoder().fit_transform(reg[col])

X = reg[['Occupants','AC Used','LED Used','Renewable']]
y = reg['Daily Energy (kWh)']

model = LinearRegression().fit(X,y)
r2 = model.score(X,y)

coeffs = pd.DataFrame({'Feature':X.columns,'Impact':model.coef_})

st.dataframe(coeffs)
st.write(f"Model Accuracy (R²): {r2:.3f}")

fig, ax = plt.subplots()
ax.bar(coeffs['Feature'], coeffs['Impact'])
ax.set(title="Feature Impact", xlabel="Feature", ylabel="Impact")
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
# 🔮 POLICY SIMULATION
# =========================================================

st.subheader("🔮 Policy Simulation")

scenario = st.selectbox("Scenario",
["LED Adoption","Reduce AC Usage","Solar Adoption"])

sim = display_data.copy()
sim['Daily Energy (kWh)'] = sim['Daily Energy (kWh)'].astype(float)

impact = st.slider("Impact %",5,30,15)/100

if scenario == "LED Adoption":
    sim.loc[sim['LED Used']=='No','Daily Energy (kWh)'] *= (1-impact)

elif scenario == "Reduce AC Usage":
    sim.loc[sim['AC Used']=='Yes','Daily Energy (kWh)'] *= (1-impact)

elif scenario == "Solar Adoption":
    sim.loc[sim['Renewable']=='No','Daily Energy (kWh)'] *= (1-impact)

sim['Cost (₹)'] = sim['Daily Energy (kWh)']*9
sim['Cost (HKD)'] = sim['Cost (₹)']*conversion_rate_hkd
sim['Cost (USD)'] = sim['Cost (₹)']*conversion_rate_usd

new_cost = safe_mean(sim[cost_col], avg_cost)
savings = (avg_cost - new_cost)*len(sim)

st.write(f"💡 New Avg Cost: {symbol} {new_cost:.2f}")
st.write(f"💰 Total Savings: {symbol} {savings:.2f}/day")

# =========================================================
# 🎯 PERSONALIZED INSIGHTS
# =========================================================

st.subheader("🎯 Personalized Insights")

for _, row in display_data.head(5).iterrows():
    msg = f"House {row['Household ID']}: "
    if row['LED Used']=="No": msg+="Use LED. "
    if row['AC Used']=="Yes": msg+="Reduce AC. "
    if row['Renewable']=="No": msg+="Adopt solar. "
    st.write(msg)

# =========================================================
# 🧠 SUMMARY
# =========================================================

st.subheader("🧠 Key Insights")

st.write(f"""
- Avg energy: {avg_energy:.2f} kWh  
- AC significantly increases consumption  
- LED reduces cost  
- Model explains {r2*100:.1f}% variation  
- Policy simulation shows measurable savings  
""")

# =========================================================
# DOWNLOAD
# =========================================================

@st.cache_data
def convert(df):
    return df.to_csv(index=False).encode('utf-8')

st.download_button("Download Data", convert(display_data), "energy.csv")
