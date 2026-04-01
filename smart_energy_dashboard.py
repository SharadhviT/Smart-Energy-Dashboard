import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression

st.set_page_config(page_title="Smart Energy Optimization", layout="wide")

# =====================================================
# 🎯 TITLE
# =====================================================
st.title("⚡ Smart Energy Optimization System")

# =====================================================
# 📂 DATA GENERATION / UPLOAD
# =====================================================
st.sidebar.header("📁 Data Options")

option = st.sidebar.radio("Choose Data Source", ["Generate Sample Data", "Upload CSV"])

def generate_data():
    np.random.seed(42)
    data = pd.DataFrame({
        "Temperature": np.random.randint(20, 40, 100),
        "Humidity": np.random.randint(30, 80, 100),
        "Occupancy": np.random.randint(1, 6, 100),
        "Appliance_Usage": np.random.randint(1, 10, 100)
    })
    data["Energy_kWh"] = (
        0.5 * data["Temperature"] +
        0.3 * data["Humidity"] +
        2 * data["Occupancy"] +
        1.5 * data["Appliance_Usage"] +
        np.random.normal(0, 5, 100)
    )
    return data

if option == "Generate Sample Data":
    df = generate_data()
else:
    uploaded_file = st.sidebar.file_uploader("Upload CSV", type=["csv"])
    if uploaded_file:
        df = pd.read_csv(uploaded_file)
    else:
        st.warning("Upload a dataset to proceed")
        st.stop()

# =====================================================
# 📊 DATA PREVIEW
# =====================================================
st.subheader("📊 Dataset Preview")
st.dataframe(df)

# =====================================================
# 📈 MODEL TRAINING
# =====================================================
X = df[["Temperature", "Humidity", "Occupancy", "Appliance_Usage"]]
y = df["Energy_kWh"]

model = LinearRegression()
model.fit(X, y)

# =====================================================
# 🔮 PREDICTION SECTION
# =====================================================
st.subheader("🔮 Predict Energy Usage")

col1, col2, col3, col4 = st.columns(4)

temp = col1.slider("Temperature", 15, 45, 30)
humidity = col2.slider("Humidity", 20, 90, 50)
occupancy = col3.slider("Occupancy", 1, 10, 3)
appliance = col4.slider("Appliance Usage", 1, 15, 5)

prediction = model.predict([[temp, humidity, occupancy, appliance]])

st.success(f"⚡ Predicted Energy Consumption: {prediction[0]:.2f} kWh")

# =====================================================
# 📉 VISUALIZATION
# =====================================================
st.subheader("📉 Energy Consumption Insights")

fig, ax = plt.subplots()
ax.scatter(df["Temperature"], df["Energy_kWh"])
ax.set_xlabel("Temperature")
ax.set_ylabel("Energy (kWh)")
st.pyplot(fig)

# =====================================================
# ⚙️ OPTIMIZATION SIMULATION
# =====================================================
st.subheader("⚙️ Optimization Simulation")

reduction = st.slider("Reduce Appliance Usage (%)", 0, 50, 10)

optimized_df = df.copy()
optimized_df["Appliance_Usage"] *= (1 - reduction / 100)

optimized_energy = model.predict(
    optimized_df[["Temperature", "Humidity", "Occupancy", "Appliance_Usage"]]
)

original_total = df["Energy_kWh"].sum()
optimized_total = optimized_energy.sum()

st.metric("Original Energy", f"{original_total:.2f} kWh")
st.metric("Optimized Energy", f"{optimized_total:.2f} kWh")
st.metric("Energy Saved", f"{original_total - optimized_total:.2f} kWh")

# =====================================================
# 📊 COMPARISON GRAPH
# =====================================================
st.subheader("📊 Before vs After Optimization")

fig2, ax2 = plt.subplots()
ax2.plot(df["Energy_kWh"].values, label="Original")
ax2.plot(optimized_energy, label="Optimized")
ax2.legend()
st.pyplot(fig2)

# =====================================================
# 💡 SMART SUGGESTIONS
# =====================================================
st.subheader("💡 Smart Recommendations")

if reduction > 20:
    st.write("✔ Significant energy savings achieved!")
else:
    st.write("👉 Try increasing appliance efficiency or reducing usage time.")

if temp > 35:
    st.write("🌡 High temperature detected: Optimize AC usage.")

if occupancy <= 2:
    st.write("🏠 Low occupancy: Turn off unused devices.")

st.success("System analysis complete!")
