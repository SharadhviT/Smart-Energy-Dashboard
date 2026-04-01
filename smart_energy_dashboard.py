import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.title("Smart Energy Awareness & Optimization Dashboard")

# Number of households
num = st.number_input("Enter number of households", min_value=1, max_value=100, value=5, step=1)

household_data = []

for i in range(1, num+1):
    st.subheader(f"Household {i}")
    
    energy = st.number_input(
        f"Daily Energy (kWh) for Household {i}", 
        min_value=0, value=10, key=f"energy_{i}"
    )
    
    cost = st.number_input(
        f"Daily Cost (₹) for Household {i}", 
        min_value=0, value=150, key=f"cost_{i}"
    )
    
    tip = st.selectbox(
        f"Implemented Energy-Saving Tips?", 
        ["Yes", "No"], key=f"tip_{i}"
    )
    
    occupants = st.number_input(
        f"Number of Occupants", min_value=1, max_value=20, value=3, key=f"occupants_{i}"
    )
    
    house_type = st.selectbox(
        "Household Type", ["Apartment", "Independent House", "Villa"], key=f"type_{i}"
    )
    
    ac = st.selectbox(
        "Air Conditioning Used?", ["Yes", "No"], key=f"ac_{i}"
    )
    
    led = st.selectbox(
        "LED Bulbs Used?", ["Yes", "No"], key=f"led_{i}"
    )
    
    washing_hours = st.number_input(
        "Washing Machine Usage per Day (hours)", min_value=0, max_value=5, value=1, key=f"washing_{i}"
    )
    
    renewable = st.selectbox(
        "Renewable Energy Source (Solar)?", ["Yes", "No"], key=f"solar_{i}"
    )

    household_data.append([
        i, energy, cost, tip, occupants, house_type, ac, led, washing_hours, renewable
    ])

# Convert to DataFrame
columns = [
    "Household ID", "Daily Energy (kWh)", "Cost (₹)", "Implemented Tips?", 
    "Occupants", "Household Type", "AC Used", "LED Used", "Washing Hours", "Renewable"
]
data = pd.DataFrame(household_data, columns=columns)

# Display Data
st.subheader("Household Energy Data")
st.dataframe(data)

# Line chart for Daily Energy
st.subheader("Daily Energy Usage (kWh)")
st.line_chart(data['Daily Energy (kWh)'])

# Pie chart for tips implemented
st.subheader("Households Implementing Energy-Saving Tips")
tip_counts = data['Implemented Tips?'].value_counts()
fig1, ax1 = plt.subplots()
ax1.pie(tip_counts, labels=tip_counts.index, autopct='%1.1f%%', colors=['#66b3ff','#ff9999'])
st.pyplot(fig1)

# Bar chart for cost
st.subheader("Daily Cost (₹) per Household")
st.bar_chart(data.set_index('Household ID')['Cost (₹)'])

# Additional Insights
st.subheader("Average Energy Usage per Occupant")
avg_energy_per_occupant = (data['Daily Energy (kWh)'] / data['Occupants']).mean()
st.write(f"Average Energy per Occupant: {avg_energy_per_occupant:.2f} kWh")

st.subheader("Percentage Using LED Bulbs")
led_pct = (data['LED Used'] == "Yes").mean() * 100
st.write(f"{led_pct:.1f}% of households use LED bulbs")

st.subheader("Top 3 Energy-Saving Tips")
st.write("""
1. Turn off unused appliances.  
2. Use LED bulbs instead of CFL/Incandescent.  
3. Reduce AC usage or set optimal temperature.
""")
