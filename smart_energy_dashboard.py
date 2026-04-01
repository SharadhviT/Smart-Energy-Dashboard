import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression

st.set_page_config(page_title="AI Smart Energy Optimizer", layout="wide")
st.title("🌱 AI Smart Energy Optimizer")

# Upload or use sample data
data_file = st.file_uploader("Upload Energy Data CSV", type=["csv"])
if data_file:
    df = pd.read_csv(data_file)
else:
    # Sample data
    df = pd.DataFrame({
        'AC_Hours':[5,6,4,7,3],
        'Lights_Hours':[6,5,4,6,5],
        'Fridge_Usage(kWh)':[3,3.2,2.8,3.5,3],
        'Other_Usage(kWh)':[2,2.1,1.9,2.5,2]
    })
st.dataframe(df)

# Calculate total energy
df['Total_Energy(kWh)'] = df['AC_Hours']*1.5 + df['Lights_Hours']*0.5 + df['Fridge_Usage(kWh)'] + df['Other_Usage(kWh)']

# Train model
X = df[['AC_Hours','Lights_Hours','Fridge_Usage(kWh)','Other_Usage(kWh)']]
y = df['Total_Energy(kWh)']
model = LinearRegression()
model.fit(X, y)

st.subheader("Predict Daily Energy Usage")
ac = st.slider("AC Hours", 0, 24, 5)
lights = st.slider("Lights Hours", 0, 24, 5)
fridge = st.slider("Fridge Usage kWh", 0, 10, 3)
other = st.slider("Other Usage kWh", 0, 10, 2)

pred = model.predict([[ac, lights, fridge, other]])[0]
st.write(f"Predicted Daily Energy Consumption: **{pred:.2f} kWh**")

# Optimization suggestion
optimized_ac = max(ac - 2, 0)
optimized_lights = max(lights - 2, 0)
optimized_pred = model.predict([[optimized_ac, optimized_lights, fridge, other]])[0]
st.success(f"Suggested Reduction: AC → {optimized_ac}h, Lights → {optimized_lights}h")
st.info(f"Optimized Energy Consumption: **{optimized_pred:.2f} kWh**")

# CO2 calculation
co2 = pred * 0.82
st.write(f"Estimated CO₂ Emission: **{co2:.2f} kg**")

# Plot energy usage
fig, ax = plt.subplots()
df[['AC_Hours','Lights_Hours','Fridge_Usage(kWh)','Other_Usage(kWh)']].plot(kind='bar', ax=ax)
plt.title("Energy Usage Overview")
st.pyplot(fig)
requirements.txt

        st.write(f"**New Energy:** {new_energy:.2f} kWh")
        st.write(f"**New Cost:** {currency_symbol}{new_cost:.2f}")
        st.write(f"**Savings:** {currency_symbol}{row[cost_col]-new_cost:.2f}")
