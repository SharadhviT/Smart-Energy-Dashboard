import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from sklearn.ensemble import RandomForestRegressor, IsolationForest
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.metrics import mean_absolute_error, r2_score
from sklearn.model_selection import train_test_split
from sklearn.cluster import KMeans
from fpdf import FPDF
import io, base64
from datetime import datetime

# ---------- Page Config ----------
st.set_page_config(layout="wide", page_title="Smart Energy Dashboard", page_icon="💡")

# ---------- Helper Functions ----------
def ensure_cost_columns(df):
    if 'Cost (₹)' not in df.columns:
        df['Cost (₹)'] = df['Daily Energy (kWh)'] * 9
    if 'Cost (HKD)' not in df.columns:
        df['Cost (HKD)'] = df['Cost (₹)'] * 0.084
    if 'Cost (USD)' not in df.columns:
        df['Cost (USD)'] = df['Cost (₹)'] * 0.011
    return df

def get_currency_symbol(currency):
    return {"INR":"₹","HKD":"HKD","USD":"$"}.get(currency,"$")

def safe_mean(series, fallback=None):
    return fallback if series.empty else series.mean()

# ---------- Initialize Data ----------
if 'data' not in st.session_state:
    np.random.seed(42)
    n = 100
    df = pd.DataFrame({
        "Household ID": range(1,n+1),
        "Household Type": np.random.choice(["Apartment","Villa","Independent House"], n),
        "Occupants": np.random.randint(1,8,n),
        "Daily Energy (kWh)": np.random.randint(10,80,n),
        "AC Used": np.random.choice(["Yes","No"], n, p=[0.6,0.4]),
        "LED Used": np.random.choice(["Yes","No"], n, p=[0.5,0.5]),
        "Renewable": np.random.choice(["Yes","No"], n, p=[0.3,0.7]),
        "Implemented Tips?": np.random.choice(["Yes","No"], n, p=[0.4,0.6]),
        "Weather": np.random.choice(["Sunny","Rainy","Cloudy","Snowy"], n)
    })
    df = ensure_cost_columns(df)
    st.session_state.data = df

# ---------- Title ----------
st.title("💡 Smart Energy Awareness & Optimization Dashboard")

# ---------- Sidebar ----------
st.sidebar.header("⚙️ Controls")

# Currency selector
currency = st.sidebar.radio("💱 Select Currency", ["INR","HKD","USD"])
cost_col = f"Cost ({currency})"
currency_symbol = get_currency_symbol(currency)

# File upload
uploaded_file = st.sidebar.file_uploader("Upload CSV", type="csv")
if uploaded_file:
    new_data = pd.read_csv(uploaded_file)
    new_data = ensure_cost_columns(new_data)
    st.session_state.data = new_data
    st.sidebar.success("Data loaded successfully!")

data = st.session_state.data

# ---------- Add / Delete Households ----------
with st.sidebar.expander("➕ Add Household"):
    hh_id = st.number_input("Household ID", int(data['Household ID'].max()+1), step=1)
    hh_type = st.selectbox("Household Type", ["Apartment","Villa","Independent House"])
    occupants = st.number_input("Occupants", 1, 10, step=1)
    energy = st.number_input("Daily Energy (kWh)", 1, 200, step=1)
    ac = st.selectbox("AC Used", ["Yes","No"])
    led = st.selectbox("LED Used", ["Yes","No"])
    renewable = st.selectbox("Renewable", ["Yes","No"])
    tips = st.selectbox("Implemented Tips?", ["Yes","No"])
    weather = st.selectbox("Weather", ["Sunny","Rainy","Cloudy","Snowy"])
    if st.button("Add Household"):
        new_row = pd.DataFrame({
            "Household ID":[hh_id],
            "Household Type":[hh_type],
            "Occupants":[occupants],
            "Daily Energy (kWh)":[energy],
            "AC Used":[ac],
            "LED Used":[led],
            "Renewable":[renewable],
            "Implemented Tips?":[tips],
            "Weather":[weather]
        })
        new_row = ensure_cost_columns(new_row)
        st.session_state.data = pd.concat([data,new_row],ignore_index=True)
        st.success(f"Household {hh_id} added!")

with st.sidebar.expander("❌ Delete Household"):
    del_hh = st.selectbox("Select Household to Delete", options=data['Household ID'])
    if st.button("Delete Household"):
        st.session_state.data = data[data['Household ID'] != del_hh]
        st.success(f"Household {del_hh} deleted!")

# ---------- Filters ----------
household_types = st.sidebar.multiselect("Household Type", options=data['Household Type'].unique(), default=data['Household Type'].unique())
ac_filter = st.sidebar.multiselect("AC Used", options=['Yes','No'], default=['Yes','No'])
led_filter = st.sidebar.multiselect("LED Used", options=['Yes','No'], default=['Yes','No'])
renewable_filter = st.sidebar.multiselect("Renewable", options=['Yes','No'], default=['Yes','No'])
tips_filter = st.sidebar.multiselect("Implemented Tips?", options=['Yes','No'], default=['Yes','No'])
weather_filter = st.sidebar.multiselect("Weather", options=data['Weather'].unique(), default=data['Weather'].unique())

min_energy, max_energy = st.sidebar.slider("Daily Energy (kWh)", float(data['Daily Energy (kWh)'].min()), float(data['Daily Energy (kWh)'].max()), (float(data['Daily Energy (kWh)'].min()), float(data['Daily Energy (kWh)'].max())))
min_cost, max_cost = st.sidebar.slider(f"Daily Cost ({currency_symbol})", float(data[cost_col].min()), float(data[cost_col].max()), (float(data[cost_col].min()), float(data[cost_col].max())))
min_occupants, max_occupants = st.sidebar.slider("Occupants", int(data['Occupants'].min()), int(data['Occupants'].max()), (int(data['Occupants'].min()), int(data['Occupants'].max())))

filtered_data = data[
    (data['Household Type'].isin(household_types)) &
    (data['AC Used'].isin(ac_filter)) &
    (data['LED Used'].isin(led_filter)) &
    (data['Renewable'].isin(renewable_filter)) &
    (data['Implemented Tips?'].isin(tips_filter)) &
    (data['Weather'].isin(weather_filter)) &
    (data['Daily Energy (kWh)']>=min_energy) & (data['Daily Energy (kWh)']<=max_energy) &
    (data[cost_col]>=min_cost) & (data[cost_col]<=max_cost) &
    (data['Occupants']>=min_occupants) & (data['Occupants']<=max_occupants)
]

# ---------- Metrics ----------
avg_energy = safe_mean(filtered_data['Daily Energy (kWh)'], fallback=safe_mean(data['Daily Energy (kWh)']))
avg_cost = safe_mean(filtered_data[cost_col], fallback=safe_mean(data[cost_col]))
tips_percent = safe_mean((filtered_data['Implemented Tips?']=='Yes')*100, fallback=(data['Implemented Tips?']=='Yes').mean()*100)
renewable_percent = safe_mean((filtered_data['Renewable']=='Yes')*100, fallback=(data['Renewable']=='Yes').mean()*100)

st.subheader("📊 Key Metrics")
c1,c2,c3,c4 = st.columns(4)
c1.metric("Avg Energy (kWh)", f"{avg_energy:.2f}")
c2.metric(f"Avg Cost ({currency_symbol})", f"{avg_cost:.2f}")
c3.metric("% Implemented Tips", f"{tips_percent:.1f}%")
c4.metric("% Using Renewable", f"{renewable_percent:.1f}%")

# ---------- Visualizations ----------
st.subheader("🌤 Weather vs Energy")
fig_weather = px.box(filtered_data, x="Weather", y="Daily Energy (kWh)", color="Weather", title="Energy by Weather")
st.plotly_chart(fig_weather,use_container_width=True)

st.subheader("📈 Energy Trend by Household")
fig_energy = px.line(filtered_data, x='Household ID', y='Daily Energy (kWh)', color='Weather', title="Energy Trend")
st.plotly_chart(fig_energy,use_container_width=True)

st.subheader("💰 Daily Cost per Household")
fig_cost = px.bar(filtered_data, x='Household ID', y=cost_col, color='Weather', title=f"Cost per Household ({currency_symbol})")
st.plotly_chart(fig_cost,use_container_width=True)

# ---------- Advanced Analytics ----------
st.markdown("---")
st.subheader("🧠 Advanced Analytics")
ml_data = filtered_data.copy()
le = LabelEncoder()
for col in ['AC Used','LED Used','Renewable','Weather']:
    ml_data[col] = le.fit_transform(ml_data[col])
X = ml_data[['Occupants','AC Used','LED Used','Renewable','Weather']]
y = ml_data['Daily Energy (kWh)']

if len(X)>1:
    # Random Forest
    X_train,X_test,y_train,y_test = train_test_split(X,y,test_size=0.2,random_state=42)
    rf = RandomForestRegressor(n_estimators=100,random_state=42)
    rf.fit(X_train,y_train)
    y_pred = rf.predict(X_test)
    st.write(f"**Random Forest Performance:** MAE={mean_absolute_error(y_test,y_pred):.2f}, R²={r2_score(y_test,y_pred):.2f}")

    # Feature Importance
    fi = pd.DataFrame({'Feature':X.columns,'Importance':rf.feature_importances_}).sort_values('Importance',ascending=False)
    fig_fi = px.bar(fi,x='Importance',y='Feature',orientation='h',title="Feature Importance")
    st.plotly_chart(fig_fi,use_container_width=True)

    # Anomaly Detection
    iso = IsolationForest(contamination=0.1,random_state=42)
    ml_data['Anomaly'] = iso.fit_predict(X)
    anomalies = ml_data[ml_data['Anomaly']==-1]
    st.write(f"**Anomalies Detected:** {len(anomalies)} households")
    if not anomalies.empty:
        st.dataframe(anomalies[['Household ID','Daily Energy (kWh)',cost_col,'AC Used','LED Used','Weather']])

    # Clustering
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    kmeans = KMeans(n_clusters=3,random_state=42)
    filtered_data['Cluster'] = kmeans.fit_predict(X_scaled)
    fig_cluster = px.scatter(filtered_data, x='Daily Energy (kWh)', y='Occupants', color='Cluster', hover_data=['Household ID'], title="Household Clusters")
    st.plotly_chart(fig_cluster,use_container_width=True)

# ---------- What-If Simulator ----------
st.subheader("💡 What-If Simulator")
with st.expander("Simulate Energy Savings"):
    if not filtered_data.empty:
        sim_hh = st.selectbox("Select Household ID", filtered_data['Household ID'].tolist())
        row = filtered_data[filtered_data['Household ID']==sim_hh].iloc[0]
        st.write(f"Current Energy: {row['Daily Energy (kWh)']} kWh, Cost: {currency_symbol}{row[cost_col]:.2f}")
        led_opt = st.checkbox("Switch to LED bulbs")
        ac_opt = st.checkbox("Optimize AC usage (reduce 20%)")
        solar_opt = st.checkbox("Adopt solar panels (reduce 30%)")
        new_energy = row['Daily Energy (kWh)']
        if led_opt and row['LED Used']=='No': new_energy*=0.9
        if ac_opt and row['AC Used']=='Yes': new_energy*=0.8
        if solar_opt and row['Renewable']=='No': new_energy*=0.7
        new_cost = new_energy*(row[cost_col]/row['Daily Energy (kWh)'])
        st.write(f"**New Energy:** {new_energy:.2f} kWh")
        st.write(f"**New Cost:** {currency_symbol}{new_cost:.2f}")
        st.write(f"**Savings:** {currency_symbol}{row[cost_col]-new_cost:.2f}")
