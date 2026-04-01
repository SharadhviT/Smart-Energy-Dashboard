import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Page setup
st.set_page_config(layout="wide", page_title="Smart Energy Dashboard")
st.title("💡 Smart Energy Awareness & Optimization Dashboard – 100 Households")

# Load data
data = pd.read_csv("energy_data_100.csv")

# ---------- Currency Conversion ----------
conversion_rate = 0.096  # 1 INR ≈ 0.096 HKD
data['Cost (HKD)'] = data['Cost (₹)'] * conversion_rate

# -------------------- SIDEBAR FILTERS --------------------
st.sidebar.header("🔎 Filter Households")
household_types = st.sidebar.multiselect(
    "Household Type", 
    options=data['Household Type'].unique(), 
    default=data['Household Type'].unique()
)
ac_filter = st.sidebar.multiselect(
    "AC Used", options=['Yes','No'], default=['Yes','No']
)
led_filter = st.sidebar.multiselect(
    "LED Used", options=['Yes','No'], default=['Yes','No']
)
renewable_filter = st.sidebar.multiselect(
    "Renewable", options=['Yes','No'], default=['Yes','No']
)

# Apply filters
filtered_data = data[
    (data['Household Type'].isin(household_types)) &
    (data['AC Used'].isin(ac_filter)) &
    (data['LED Used'].isin(led_filter)) &
    (data['Renewable'].isin(renewable_filter))
]

# -------------------- KEY METRICS --------------------
st.subheader("📊 Key Metrics (Filtered Data)")
col1, col2, col3, col4 = st.columns(4)
col1.metric("Avg Energy (kWh)", f"{filtered_data['Daily Energy (kWh)'].mean():.2f}")
col2.metric("Avg Cost (INR)", f"{filtered_data['Cost (₹)'].mean():.2f}")
col2.metric("Avg Cost (HKD)", f"{filtered_data['Cost (HKD)'].mean():.2f}")
col3.metric("% Implemented Tips", f"{(filtered_data['Implemented Tips?']=='Yes').mean()*100:.1f}%")
col4.metric("% Using Renewable", f"{(filtered_data['Renewable']=='Yes').mean()*100:.1f}%")

# -------------------- RAW DATA --------------------
st.subheader("🏠 Household Energy Data (Filtered)")
st.dataframe(filtered_data)

# -------------------- LINE CHART: Energy --------------------
st.subheader("📈 Daily Energy Usage (kWh)")
st.line_chart(filtered_data['Daily Energy (kWh)'])

# -------------------- BAR CHART: Cost --------------------
st.subheader("💰 Daily Cost per Household")
st.bar_chart(filtered_data.set_index('Household ID')['Cost (HKD)'])

# -------------------- PIE CHART: Tips Implemented --------------------
st.subheader("✅ Households Implementing Energy-Saving Tips")
tip_counts = filtered_data['Implemented Tips?'].value_counts()
fig1, ax1 = plt.subplots()
ax1.pie(tip_counts, labels=tip_counts.index, autopct='%1.1f%%', colors=['#66b3ff','#ff9999'])
st.pyplot(fig1)

# -------------------- PIE CHART: Renewable --------------------
st.subheader("🌞 Renewable Energy Adoption")
renewable_counts = filtered_data['Renewable'].value_counts()
fig2, ax2 = plt.subplots()
ax2.pie(renewable_counts, labels=renewable_counts.index, autopct='%1.1f%%', colors=['#99ff99','#ffcc99'])
st.pyplot(fig2)

# -------------------- BOX PLOT: AC Usage --------------------
st.subheader("❄️ AC Usage vs Daily Energy")
fig3, ax3 = plt.subplots(figsize=(8,4))
sns.boxplot(x='AC Used', y='Daily Energy (kWh)', data=filtered_data, ax=ax3)
st.pyplot(fig3)

# -------------------- SCATTER PLOT: Energy vs Occupants --------------------
st.subheader("👥 Energy vs Number of Occupants")
fig4, ax4 = plt.subplots()
sns.scatterplot(x='Occupants', y='Daily Energy (kWh)', hue='LED Used', data=filtered_data, palette="Set2", ax=ax4)
st.pyplot(fig4)

# -------------------- ENERGY PER OCCUPANT --------------------
st.subheader("⚡ Energy Usage per Occupant")
filtered_data['Energy per Occupant'] = filtered_data['Daily Energy (kWh)'] / filtered_data['Occupants']
st.bar_chart(filtered_data.set_index('Household ID')['Energy per Occupant'])

# -------------------- Avg Energy by Household Type --------------------
st.subheader("🏘️ Avg Energy Usage by Household Type")
avg_energy_type = filtered_data.groupby('Household Type')['Daily Energy (kWh)'].mean()
st.bar_chart(avg_energy_type)

# -------------------- LED vs Non-LED Analysis --------------------
st.subheader("💡 LED vs Non-LED Cost Analysis")
avg_cost_led = filtered_data[filtered_data['LED Used']=='Yes']['Cost (HKD)'].mean()
avg_cost_non_led = filtered_data[filtered_data['LED Used']=='No']['Cost (HKD)'].mean()
st.write(f"- Avg cost with LED bulbs: HKD {avg_cost_led:.2f}")
st.write(f"- Avg cost without LED bulbs: HKD {avg_cost_non_led:.2f}")
st.write(f"- LED households save ~HKD {avg_cost_non_led-avg_cost_led:.2f} per day")

# -------------------- AC vs Non-AC Analysis --------------------
st.subheader("❄️ AC vs Non-AC Energy Analysis")
avg_ac = filtered_data[filtered_data['AC Used']=='Yes']['Daily Energy (kWh)'].mean()
avg_no_ac = filtered_data[filtered_data['AC Used']=='No']['Daily Energy (kWh)'].mean()
st.write(f"- Avg AC Household Energy: {avg_ac:.2f} kWh")
st.write(f"- Avg Non-AC Household Energy: {avg_no_ac:.2f} kWh")
if avg_no_ac != 0:
    st.write(f"- AC households consume {((avg_ac-avg_no_ac)/avg_no_ac*100):.1f}% more energy on average")

# -------------------- Top 5 Energy Consumers --------------------
st.subheader("🏆 Top 5 Energy-Consuming Households")
top5 = filtered_data.sort_values(by='Daily Energy (kWh)', ascending=False).head(5)
st.table(top5[['Household ID','Daily Energy (kWh)','Cost (₹)','Cost (HKD)','AC Used','LED Used']])

# -------------------- Renewable Impact --------------------
st.subheader("🌞 Renewable Energy Impact")
renewable_avg = filtered_data[filtered_data['Renewable']=='Yes']['Daily Energy (kWh)'].mean()
non_renewable_avg = filtered_data[filtered_data['Renewable']=='No']['Daily Energy (kWh)'].mean()
st.write(f"- Avg energy with renewable: {renewable_avg:.2f} kWh")
st.write(f"- Avg energy without renewable: {non_renewable_avg:.2f} kWh")

# -------------------- Dynamic Recommendations --------------------
st.subheader("📝 Data-Driven Recommendations")
if avg_cost_led > avg_cost_non_led:
    st.write("- Encourage households to switch to LED bulbs to save cost.")
if avg_ac > avg_no_ac:
    st.write("- Reduce AC usage or optimize temperature settings to save energy.")
if renewable_avg > non_renewable_avg:
    st.write("- Promote renewable energy adoption for higher efficiency.")

# -------------------- Top 5 Energy-Saving Tips --------------------
st.subheader("💡 Top 5 Energy-Saving Tips")
st.write("""
1. Turn off unused appliances.  
2. Use LED bulbs instead of CFL/Incandescent.  
3. Reduce AC usage or set optimal temperature.  
4. Install solar panels if possible.  
5. Optimize washing machine usage and laundry loads.
""")

# -------------------- DOWNLOAD FILTERED DATA --------------------
st.subheader("💾 Download Filtered Data")
@st.cache_data
def convert_df(df):
    return df.to_csv(index=False).encode('utf-8')

csv = convert_df(filtered_data)

st.download_button(
    label="Download Filtered Data as CSV",
    data=csv,
    file_name='filtered_energy_data.csv',
    mime='text/csv'
)
