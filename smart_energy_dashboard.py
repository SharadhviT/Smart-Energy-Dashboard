import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# ---------- Page Setup ----------
st.set_page_config(layout="wide", page_title="Smart Energy Dashboard")
st.title("💡 Smart Energy Awareness & Optimization Dashboard – 100 Households")

# ---------- Load Data ----------
data = pd.read_csv("energy_data_100.csv")

# ---------- Standardize categorical columns ----------
for col in ['AC Used','LED Used','Renewable','Implemented Tips?']:
    data[col] = data[col].str.title()

# ---------- Currency Conversion ----------
conversion_rate = 0.096  # 1 INR ≈ 0.096 HKD
data['Cost (HKD)'] = data['Cost (₹)'] * conversion_rate

# ---------- SIDEBAR FILTERS ----------
st.sidebar.header("🔎 Filter Households")
household_types = st.sidebar.multiselect("Household Type", options=data['Household Type'].unique(), default=data['Household Type'].unique())
ac_filter = st.sidebar.multiselect("AC Used", options=['Yes','No'], default=['Yes','No'])
led_filter = st.sidebar.multiselect("LED Used", options=['Yes','No'], default=['Yes','No'])
renewable_filter = st.sidebar.multiselect("Renewable", options=['Yes','No'], default=['Yes','No'])

# ---------- Apply Filters ----------
filtered_data = data[
    (data['Household Type'].isin(household_types)) &
    (data['AC Used'].isin(ac_filter)) &
    (data['LED Used'].isin(led_filter)) &
    (data['Renewable'].isin(renewable_filter))
]

# ---------- Fallback function ----------
def safe_mean(series, fallback=None):
    if series.empty:
        return fallback if fallback is not None else 0
    else:
        return series.mean()

# ---------- Metrics ----------
avg_energy = safe_mean(filtered_data['Daily Energy (kWh)'], fallback=data['Daily Energy (kWh)'].mean())
avg_cost_inr = safe_mean(filtered_data['Cost (₹)'], fallback=data['Cost (₹)'].mean())
avg_cost_hkd = safe_mean(filtered_data['Cost (HKD)'], fallback=data['Cost (HKD)'].mean())
tips_percent = safe_mean((filtered_data['Implemented Tips?']=='Yes')*100, fallback=(data['Implemented Tips?']=='Yes').mean()*100)
renewable_percent = safe_mean((filtered_data['Renewable']=='Yes')*100, fallback=(data['Renewable']=='Yes').mean()*100)

st.subheader("📊 Key Metrics (Filtered Data)")
col1, col2, col3, col4 = st.columns(4)
col1.metric("Avg Energy (kWh)", f"{avg_energy:.2f}")
col2.metric("Avg Cost (INR)", f"{avg_cost_inr:.2f}")
col2.metric("Avg Cost (HKD)", f"{avg_cost_hkd:.2f}")
col3.metric("% Implemented Tips", f"{tips_percent:.1f}%")
col4.metric("% Using Renewable", f"{renewable_percent:.1f}%")

# ---------- Display filtered data ----------
st.subheader("🏠 Household Energy Data (Filtered)")
if filtered_data.empty:
    st.info("⚠️ No households match your filter. Showing overall dataset as fallback.")
    display_data = data
else:
    display_data = filtered_data
st.dataframe(display_data)

# ---------- Line Chart: Daily Energy ----------
st.subheader("📈 Daily Energy Usage (kWh)")
st.line_chart(display_data['Daily Energy (kWh)'])

# ---------- Bar Chart: Cost HKD ----------
st.subheader("💰 Daily Cost per Household (HKD)")
st.bar_chart(display_data.set_index('Household ID')['Cost (HKD)'])

# ---------- Pie Charts ----------
st.subheader("✅ Households Implementing Energy-Saving Tips")
tip_counts = display_data['Implemented Tips?'].value_counts()
fig1, ax1 = plt.subplots()
ax1.pie(tip_counts, labels=tip_counts.index, autopct='%1.1f%%', colors=['#66b3ff','#ff9999'])
st.pyplot(fig1)

st.subheader("🌞 Renewable Energy Adoption")
renewable_counts = display_data['Renewable'].value_counts()
fig2, ax2 = plt.subplots()
ax2.pie(renewable_counts, labels=renewable_counts.index, autopct='%1.1f%%', colors=['#99ff99','#ffcc99'])
st.pyplot(fig2)

# ---------- Boxplot: AC Usage ----------
st.subheader("❄️ AC Usage vs Daily Energy")
fig3, ax3 = plt.subplots(figsize=(8,4))
sns.boxplot(x='AC Used', y='Daily Energy (kWh)', data=display_data, ax=ax3)
st.pyplot(fig3)

# ---------- Scatter: Energy vs Occupants ----------
st.subheader("👥 Energy vs Number of Occupants")
fig4, ax4 = plt.subplots()
sns.scatterplot(x='Occupants', y='Daily Energy (kWh)', hue='LED Used', data=display_data, palette="Set2", ax=ax4)
st.pyplot(fig4)

# ---------- Energy per Occupant ----------
st.subheader("⚡ Energy Usage per Occupant")
display_data['Energy per Occupant'] = display_data['Daily Energy (kWh)'] / display_data['Occupants']
st.bar_chart(display_data.set_index('Household ID')['Energy per Occupant'])

# ---------- Avg Energy by Household Type ----------
st.subheader("🏘️ Avg Energy Usage by Household Type")
avg_energy_type = display_data.groupby('Household Type')['Daily Energy (kWh)'].mean()
st.bar_chart(avg_energy_type)

# ---------- LED vs Non-LED Cost Analysis ----------
st.subheader("💡 LED vs Non-LED Cost Analysis")
avg_cost_led = safe_mean(display_data[display_data['LED Used']=='Yes']['Cost (HKD)'], fallback=avg_cost_hkd)
avg_cost_non_led = safe_mean(display_data[display_data['LED Used']=='No']['Cost (HKD)'], fallback=avg_cost_hkd)
st.write(f"- Avg cost with LED bulbs: HKD {avg_cost_led:.2f}")
st.write(f"- Avg cost without LED bulbs: HKD {avg_cost_non_led:.2f}")
st.write(f"- LED households save ~HKD {avg_cost_non_led-avg_cost_led:.2f} per day")

# ---------- AC vs Non-AC Energy ----------
st.subheader("❄️ AC vs Non-AC Energy Analysis")
avg_ac = safe_mean(display_data[display_data['AC Used']=='Yes']['Daily Energy (kWh)'], fallback=avg_energy)
avg_no_ac = safe_mean(display_data[display_data['AC Used']=='No']['Daily Energy (kWh)'], fallback=avg_energy)
st.write(f"- Avg AC Household Energy: {avg_ac:.2f} kWh")
st.write(f"- Avg Non-AC Household Energy: {avg_no_ac:.2f} kWh")
st.write(f"- AC households consume {((avg_ac-avg_no_ac)/avg_no_ac*100):.1f}% more energy" if avg_no_ac != 0 else "-")

# ---------- Top 5 Energy Consumers ----------
st.subheader("🏆 Top 5 Energy-Consuming Households")
top5 = display_data.sort_values(by='Daily Energy (kWh)', ascending=False).head(5)
st.table(top5[['Household ID','Daily Energy (kWh)','Cost (₹)','Cost (HKD)','AC Used','LED Used']])

# ---------- Renewable Impact ----------
st.subheader("🌞 Renewable Energy Impact")
renewable_avg = safe_mean(display_data[display_data['Renewable']=='Yes']['Daily Energy (kWh)'], fallback=avg_energy)
non_renewable_avg = safe_mean(display_data[display_data['Renewable']=='No']['Daily Energy (kWh)'], fallback=avg_energy)
st.write(f"- Avg energy with renewable: {renewable_avg:.2f} kWh")
st.write(f"- Avg energy without renewable: {non_renewable_avg:.2f} kWh")

# ---------- Dynamic Recommendations ----------
st.subheader("📝 Data-Driven Recommendations")
if avg_cost_led > avg_cost_non_led:
    st.write("- Encourage households to switch to LED bulbs to save cost.")
if avg_ac > avg_no_ac:
    st.write("- Reduce AC usage or optimize temperature settings to save energy.")
if renewable_avg > non_renewable_avg:
    st.write("- Promote renewable energy adoption for higher efficiency.")

# ---------- Top 5 Energy-Saving Tips ----------
st.subheader("💡 Top 5 Energy-Saving Tips")
st.write("""
1. Turn off unused appliances.  
2. Use LED bulbs instead of CFL/Incandescent.  
3. Reduce AC usage or set optimal temperature.  
4. Install solar panels if possible.  
5. Optimize washing machine usage and laundry loads.
""")

# ---------- Download Filtered Data ----------
st.subheader("💾 Download Filtered Data")
@st.cache_data
def convert_df(df):
    return df.to_csv(index=False).encode('utf-8')

csv = convert_df(display_data)
st.download_button(
    label="Download Filtered Data as CSV",
    data=csv,
    file_name='filtered_energy_data.csv',
    mime='text/csv'
)
