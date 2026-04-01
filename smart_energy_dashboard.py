import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Page settings
st.set_page_config(layout="wide", page_title="Smart Energy Dashboard")
st.title("💡 Smart Energy Awareness & Optimization Dashboard – 100 Households")

# Load preloaded 100 households CSV
data = pd.read_csv("energy_data_100.csv")

# ---------- KEY METRICS ----------
st.subheader("📊 Dashboard Key Metrics")
col1, col2, col3, col4 = st.columns(4)
col1.metric("Avg Energy (kWh)", f"{data['Daily Energy (kWh)'].mean():.2f}")
col2.metric("Avg Cost (₹)", f"{data['Cost (₹)'].mean():.2f}")
col3.metric("% Implemented Tips", f"{(data['Implemented Tips?']=='Yes').mean()*100:.1f}%")
col4.metric("% Using Renewable", f"{(data['Renewable']=='Yes').mean()*100:.1f}%")

# ---------- RAW DATA ----------
st.subheader("🏠 Household Energy Data")
st.dataframe(data)

# ---------- LINE CHART: Daily Energy ----------
st.subheader("📈 Daily Energy Usage (kWh)")
st.line_chart(data['Daily Energy (kWh)'])

# ---------- BAR CHART: Cost ----------
st.subheader("💰 Daily Cost (₹) per Household")
st.bar_chart(data.set_index('Household ID')['Cost (₹)'])

# ---------- PIE CHART: Tips Implemented ----------
st.subheader("✅ Households Implementing Energy-Saving Tips")
tip_counts = data['Implemented Tips?'].value_counts()
fig1, ax1 = plt.subplots()
ax1.pie(tip_counts, labels=tip_counts.index, autopct='%1.1f%%', colors=['#66b3ff','#ff9999'])
st.pyplot(fig1)

# ---------- ENERGY PER OCCUPANT ----------
st.subheader("⚡ Energy Usage per Occupant")
data['Energy per Occupant'] = data['Daily Energy (kWh)'] / data['Occupants']
st.bar_chart(data.set_index('Household ID')['Energy per Occupant'])

# ---------- ENERGY BY HOUSEHOLD TYPE ----------
st.subheader("🏘️ Average Energy Usage by Household Type")
avg_energy_type = data.groupby('Household Type')['Daily Energy (kWh)'].mean()
st.bar_chart(avg_energy_type)

# ---------- RENEWABLE ADOPTION PIE CHART ----------
st.subheader("🌞 Renewable Energy Adoption")
renewable_counts = data['Renewable'].value_counts()
fig2, ax2 = plt.subplots()
ax2.pie(renewable_counts, labels=renewable_counts.index, autopct='%1.1f%%', colors=['#99ff99','#ffcc99'])
st.pyplot(fig2)

# ---------- AC USAGE BOX PLOT ----------
st.subheader("❄️ AC Usage vs Daily Energy")
fig3, ax3 = plt.subplots(figsize=(8,4))
sns.boxplot(x='AC Used', y='Daily Energy (kWh)', data=data, ax=ax3)
st.pyplot(fig3)

# ---------- SCATTER PLOT: Energy vs Occupants ----------
st.subheader("👥 Energy vs Number of Occupants")
fig4, ax4 = plt.subplots()
sns.scatterplot(x='Occupants', y='Daily Energy (kWh)', hue='LED Used', data=data, palette="Set2", ax=ax4)
st.pyplot(fig4)

# ---------- LED vs Non-LED Analysis ----------
st.subheader("💡 LED vs Non-LED Cost Analysis")
avg_cost_led = data[data['LED Used']=='Yes']['Cost (₹)'].mean()
avg_cost_non_led = data[data['LED Used']=='No']['Cost (₹)'].mean()
st.write(f"- Average cost with LED bulbs: ₹{avg_cost_led:.2f}")
st.write(f"- Average cost without LED bulbs: ₹{avg_cost_non_led:.2f}")
st.write(f"- LED households save ~₹{avg_cost_non_led-avg_cost_led:.2f} per day")

# ---------- AC vs Non-AC Analysis ----------
st.subheader("❄️ AC vs Non-AC Energy Analysis")
avg_ac = data[data['AC Used']=='Yes']['Daily Energy (kWh)'].mean()
avg_no_ac = data[data['AC Used']=='No']['Daily Energy (kWh)'].mean()
st.write(f"- Average AC Household Energy: {avg_ac:.2f} kWh")
st.write(f"- Average Non-AC Household Energy: {avg_no_ac:.2f} kWh")
st.write(f"- AC households consume {((avg_ac-avg_no_ac)/avg_no_ac*100):.1f}% more energy on average")

# ---------- TOP 5 ENERGY CONSUMERS ----------
st.subheader("🏆 Top 5 Energy-Consuming Households")
top5 = data.sort_values(by='Daily Energy (kWh)', ascending=False).head(5)
st.table(top5[['Household ID','Daily Energy (kWh)','Cost (₹)','AC Used','LED Used']])

# ---------- RENEWABLE ENERGY IMPACT ----------
st.subheader("🌞 Renewable Energy Impact")
renewable_avg = data[data['Renewable']=='Yes']['Daily Energy (kWh)'].mean()
non_renewable_avg = data[data['Renewable']=='No']['Daily Energy (kWh)'].mean()
st.write(f"- Average energy with renewable: {renewable_avg:.2f} kWh")
st.write(f"- Average energy without renewable: {non_renewable_avg:.2f} kWh")

# ---------- DYNAMIC RECOMMENDATIONS ----------
st.subheader("📝 Data-Driven Recommendations")
if avg_cost_led > avg_cost_non_led:
    st.write("- Encourage households to switch to LED bulbs to save cost.")
if avg_ac > avg_no_ac:
    st.write("- Reduce AC usage or optimize temperature settings to save energy.")
if renewable_avg > non_renewable_avg:
    st.write("- Promote renewable energy adoption for higher efficiency.")

# ---------- TOP 5 ENERGY-SAVING TIPS ----------
st.subheader("💡 Top 5 Energy-Saving Tips")
st.write("""
1. Turn off unused appliances.  
2. Use LED bulbs instead of CFL/Incandescent.  
3. Reduce AC usage or set optimal temperature.  
4. Install solar panels if possible.  
5. Optimize washing machine usage and laundry loads.
""")
