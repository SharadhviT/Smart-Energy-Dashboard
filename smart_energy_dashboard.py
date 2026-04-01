 import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

st.set_page_config(layout="wide")
st.title("Smart Energy Awareness & Optimization Dashboard – 100 Households")

# Load preloaded data
data = pd.read_csv("energy_data_100.csv")

# Display raw data
st.subheader("Household Energy Data")
st.dataframe(data)

# ---------- Line chart: Daily Energy ----------
st.subheader("Daily Energy Usage (kWh) - Line Chart")
st.line_chart(data['Daily Energy (kWh)'])

# ---------- Bar chart: Cost per Household ----------
st.subheader("Daily Cost (₹) per Household")
st.bar_chart(data.set_index('Household ID')['Cost (₹)'])

# ---------- Pie chart: Tips implemented ----------
st.subheader("Households Implementing Energy-Saving Tips")
tip_counts = data['Implemented Tips?'].value_counts()
fig1, ax1 = plt.subplots()
ax1.pie(tip_counts, labels=tip_counts.index, autopct='%1.1f%%', colors=['#66b3ff','#ff9999'])
st.pyplot(fig1)

# ---------- Additional Graphs ----------
# 1. Energy per Occupant
st.subheader("Energy Usage per Occupant")
data['Energy per Occupant'] = data['Daily Energy (kWh)'] / data['Occupants']
st.bar_chart(data.set_index('Household ID')['Energy per Occupant'])

# 2. Energy by Household Type
st.subheader("Average Energy Usage by Household Type")
avg_energy_type = data.groupby('Household Type')['Daily Energy (kWh)'].mean()
st.bar_chart(avg_energy_type)

# 3. Renewable Energy Adoption
st.subheader("Renewable Energy Adoption (Solar Panels)")
renewable_counts = data['Renewable'].value_counts()
fig2, ax2 = plt.subplots()
ax2.pie(renewable_counts, labels=renewable_counts.index, autopct='%1.1f%%', colors=['#99ff99','#ffcc99'])
st.pyplot(fig2)

# 4. AC Usage Analysis
st.subheader("AC Usage vs Daily Energy")
fig3, ax3 = plt.subplots(figsize=(8,4))
sns.boxplot(x='AC Used', y='Daily Energy (kWh)', data=data, ax=ax3)
st.pyplot(fig3)

# ---------- Top 5 Energy-Saving Tips ----------
st.subheader("Top 5 Energy-Saving Tips")
st.write("""
1. Turn off unused appliances.  
2. Use LED bulbs instead of CFL/Incandescent.  
3. Reduce AC usage or set optimal temperature.  
4. Install solar panels if possible.  
5. Optimize washing machine usage and laundry loads.
""")

# ---------- Additional Insights ----------
st.subheader("Insights Summary")
st.write(f"- Average Energy per Household: {data['Daily Energy (kWh)'].mean():.2f} kWh")
st.write(f"- Average Energy per Occupant: {data['Energy per Occupant'].mean():.2f} kWh")
st.write(f"- Households using LED bulbs: {(data['LED Used']=="Yes").mean()*100:.1f}%")
st.write(f"- Households with renewable energy: {(data['Renewable']=="Yes").mean()*100:.1f}%")
st.write(f"- Households using AC: {(data['AC Used']=="Yes").mean()*100:.1f}%")
