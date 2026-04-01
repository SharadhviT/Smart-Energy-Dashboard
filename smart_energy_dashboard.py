import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from scipy.optimize import linprog

st.set_page_config(layout="wide")
st.title("⚡ Research-Grade Smart Energy Optimization System")

# =========================================================
# 📊 DATA GENERATION (TIME SERIES)
# =========================================================
def generate_data(n=200):
    np.random.seed(42)
    time = pd.date_range(start="2024-01-01", periods=n, freq="H")

    df = pd.DataFrame({
        "Time": time,
        "Temperature": np.random.randint(20, 40, n),
        "Occupancy": np.random.randint(1, 6, n),
        "Appliance": np.random.randint(1, 10, n)
    })

    df["Hour"] = df["Time"].dt.hour

    # Dynamic pricing (peak hours)
    df["Price"] = np.where(df["Hour"].isin(range(18, 23)), 10, 5)

    # Energy formula
    df["Energy"] = (
        0.6 * df["Temperature"] +
        2.5 * df["Occupancy"] +
        1.8 * df["Appliance"] +
        np.random.normal(0, 2, n)
    )

    return df

df = generate_data()

st.subheader("📊 Dataset")
st.dataframe(df.head())

# =========================================================
# 🧠 FEATURE ENGINEERING
# =========================================================
df["Lag_1"] = df["Energy"].shift(1)
df["Rolling_Mean"] = df["Energy"].rolling(3).mean()

df = df.dropna()

features = ["Temperature", "Occupancy", "Appliance", "Hour", "Lag_1", "Rolling_Mean"]
X = df[features]
y = df["Energy"]

# =========================================================
# 🤖 MODEL TRAINING
# =========================================================
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)

model = RandomForestRegressor(n_estimators=100)
model.fit(X_train, y_train)

preds = model.predict(X_test)

st.subheader("📈 Model Performance")
st.write(f"Train Score: {model.score(X_train, y_train):.3f}")
st.write(f"Test Score: {model.score(X_test, y_test):.3f}")

# =========================================================
# 📊 VISUALIZATION
# =========================================================
st.subheader("📉 Actual vs Predicted")

fig, ax = plt.subplots()
ax.plot(y_test.values, label="Actual")
ax.plot(preds, label="Predicted")
ax.legend()
st.pyplot(fig)

# =========================================================
# ⚡ OPTIMIZATION (LINEAR PROGRAMMING)
# =========================================================
st.subheader("⚡ Cost Optimization")

energy = df["Energy"].values
price = df["Price"].values

# Objective: minimize cost
c = price

# Constraints: energy demand must be met
A_eq = [np.ones(len(energy))]
b_eq = [np.sum(energy)]

# Bounds (flexibility in usage)
bounds = [(0.8 * e, 1.2 * e) for e in energy]

result = linprog(c, A_eq=A_eq, b_eq=b_eq, bounds=bounds, method="highs")

optimized_usage = result.x

original_cost = np.sum(energy * price)
optimized_cost = np.sum(optimized_usage * price)

st.metric("Original Cost", f"₹{original_cost:.2f}")
st.metric("Optimized Cost", f"₹{optimized_cost:.2f}")
st.metric("Savings", f"₹{original_cost - optimized_cost:.2f}")

# =========================================================
# 📊 COST COMPARISON GRAPH
# =========================================================
st.subheader("📊 Energy Optimization Comparison")

fig2, ax2 = plt.subplots()
ax2.plot(energy, label="Original Energy")
ax2.plot(optimized_usage, label="Optimized Energy")
ax2.legend()
st.pyplot(fig2)

# =========================================================
# 🧠 FEATURE IMPORTANCE (EXPLAINABILITY)
# =========================================================
st.subheader("🧠 Feature Importance")

importance = model.feature_importances_

fig3, ax3 = plt.subplots()
ax3.barh(features, importance)
st.pyplot(fig3)

# =========================================================
# 💡 SMART INSIGHTS
# =========================================================
st.subheader("💡 Insights")

if optimized_cost < original_cost:
    st.success("✔ Optimization successful: Cost reduced")

peak_usage = df[df["Price"] == 10]["Energy"].mean()
offpeak_usage = df[df["Price"] == 5]["Energy"].mean()

st.write(f"⚡ Peak Avg Usage: {peak_usage:.2f}")
st.write(f"🌙 Off-Peak Avg Usage: {offpeak_usage:.2f}")

if peak_usage > offpeak_usage:
    st.warning("👉 Shift load to off-peak hours to save more energy")

st.success("Analysis Complete 🚀")
