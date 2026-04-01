import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.ensemble import RandomForestRegressor, IsolationForest
from sklearn.cluster import KMeans
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.metrics import mean_absolute_error, r2_score
from sklearn.model_selection import train_test_split
import plotly.express as px
from fpdf import FPDF
import io
import requests
from datetime import datetime
import base64

# ---------- Page Config ----------
st.set_page_config(layout="wide", page_title="Smart Energy Dashboard", page_icon="💡")

# ---------- Helper Functions ----------
def ensure_cost_columns(df):
    if 'Cost (₹)' not in df.columns and 'Daily Energy (kWh)' in df.columns:
        df['Cost (₹)'] = df['Daily Energy (kWh)'] * 9
    if 'Cost (HKD)' not in df.columns and 'Cost (₹)' in df.columns:
        df['Cost (HKD)'] = df['Cost (₹)'] * 0.084
    if 'Cost (USD)' not in df.columns and 'Cost (₹)' in df.columns:
        df['Cost (USD)'] = df['Cost (₹)'] * 0.011
    return df

def safe_mean(series, fallback=None):
    return fallback if series.empty else series.mean()

def get_currency_symbol(currency):
    return {"INR":"₹","HKD":"HKD","USD":"$"}.get(currency, "$")

# ---------- Load Data ----------
@st.cache_data
def load_initial_data():
    try:
        df = pd.read_csv("energy_data_100.csv")
        for col in ['AC Used', 'LED Used', 'Renewable', 'Implemented Tips?']:
            df[col] = df[col].str.title()
        df = ensure_cost_columns(df)
    except FileNotFoundError:
        np.random.seed(42)
        n = 100
        df = pd.DataFrame({
            "Household ID": range(1, n+1),
            "Household Type": np.random.choice(["Apartment","Villa","Independent House"], n),
            "Occupants": np.random.randint(1,8,n),
            "Daily Energy (kWh)": np.random.randint(10,80,n),
            "AC Used": np.random.choice(["Yes","No"],n,p=[0.6,0.4]),
            "LED Used": np.random.choice(["Yes","No"],n,p=[0.5,0.5]),
            "Renewable": np.random.choice(["Yes","No"],n,p=[0.3,0.7]),
            "Implemented Tips?": np.random.choice(["Yes","No"],n,p=[0.4,0.6])
        })
        df['Cost (₹)'] = df['Daily Energy (kWh)'] * 9
        df = ensure_cost_columns(df)
        for col in ['AC Used', 'LED Used', 'Renewable', 'Implemented Tips?']:
            df[col] = df[col].str.title()
    return df

if 'data' not in st.session_state:
    st.session_state.data = load_initial_data()

# ---------- Sidebar Controls ----------
st.sidebar.header("⚙️ Controls")
currency = st.sidebar.radio("💱 Select Currency", ["INR","HKD","USD"])
cost_col = f"Cost ({currency})"
currency_symbol = get_currency_symbol(currency)

# File upload
uploaded_file = st.sidebar.file_uploader("Upload CSV", type="csv")
if uploaded_file:
    new_data = pd.read_csv(uploaded_file)
    for col in ['AC Used','LED Used','Renewable','Implemented Tips?']:
        if col in new_data.columns: new_data[col] = new_data[col].str.title()
    new_data = ensure_cost_columns(new_data)
    st.session_state.data = new_data
    st.sidebar.success("✅ Data loaded successfully!")

# Filters
st.sidebar.subheader("🔎 Filter Households")
data = st.session_state.data
household_types = st.sidebar.multiselect("Household Type", data['Household Type'].unique(), default=data['Household Type'].unique())
ac_filter = st.sidebar.multiselect("AC Used", ["Yes","No"], default=["Yes","No"])
led_filter = st.sidebar.multiselect("LED Used", ["Yes","No"], default=["Yes","No"])
renewable_filter = st.sidebar.multiselect("Renewable", ["Yes","No"], default=["Yes","No"])
tips_filter = st.sidebar.multiselect("Implemented Tips?", ["Yes","No"], default=["Yes","No"])
min_energy, max_energy = st.sidebar.slider("Daily Energy (kWh)", float(data['Daily Energy (kWh)'].min()), float(data['Daily Energy (kWh)'].max()), (float(data['Daily Energy (kWh)'].min()), float(data['Daily Energy (kWh)'].max())))
min_cost, max_cost = st.sidebar.slider(f"Daily Cost ({currency_symbol})", float(data[cost_col].min()), float(data[cost_col].max()), (float(data[cost_col].min()), float(data[cost_col].max())))
min_occupants, max_occupants = st.sidebar.slider("Occupants", int(data['Occupants'].min()), int(data['Occupants'].max()), (int(data['Occupants'].min()), int(data['Occupants'].max())))

filtered_data = data[
    (data['Household Type'].isin(household_types)) &
    (data['AC Used'].isin(ac_filter)) &
    (data['LED Used'].isin(led_filter)) &
    (data['Renewable'].isin(renewable_filter)) &
    (data['Implemented Tips?'].isin(tips_filter)) &
    (data['Daily Energy (kWh)'].between(min_energy,max_energy)) &
    (data[cost_col].between(min_cost,max_cost)) &
    (data['Occupants'].between(min_occupants,max_occupants))
]

# ---------- Metrics ----------
avg_energy = safe_mean(filtered_data['Daily Energy (kWh)'], fallback=data['Daily Energy (kWh)'].mean())
avg_cost = safe_mean(filtered_data[cost_col], fallback=safe_mean(data[cost_col]))
tips_percent = safe_mean((filtered_data['Implemented Tips?']=="Yes")*100, fallback=(data['Implemented Tips?']=="Yes").mean()*100)
renewable_percent = safe_mean((filtered_data['Renewable']=="Yes")*100, fallback=(data['Renewable']=="Yes").mean()*100)

st.subheader("📊 Key Metrics")
col1,col2,col3,col4 = st.columns(4)
col1.metric("Avg Energy (kWh)", f"{avg_energy:.2f}")
col2.metric(f"Avg Cost ({currency_symbol})", f"{avg_cost:.2f}")
col3.metric("% Implemented Tips", f"{tips_percent:.1f}%")
col4.metric("% Using Renewable", f"{renewable_percent:.1f}%")

# ---------- Data Table ----------
display_data = filtered_data if not filtered_data.empty else data
display_data = display_data.copy()
display_data['Efficiency Score'] = 100 - (display_data['Daily Energy (kWh)']/display_data['Daily Energy (kWh)'].max()*100)

def color_efficiency(val):
    if val>=80: return 'background-color:#d4edda'
    elif val>=50: return 'background-color:#fff3cd'
    else: return 'background-color:#f8d7da'

st.subheader("🏠 Household Energy Data")
st.dataframe(display_data[['Household ID','Household Type','Occupants','Daily Energy (kWh)',cost_col,'AC Used','LED Used','Renewable','Implemented Tips?','Efficiency Score']].style.applymap(color_efficiency,subset=['Efficiency Score']))

# ---------- Visualizations ----------
st.subheader("📈 Energy Trend")
st.plotly_chart(px.line(display_data,x='Household ID',y='Daily Energy (kWh)',title="Energy Trend"),use_container_width=True)

st.subheader(f"💰 Daily Cost ({currency_symbol})")
st.plotly_chart(px.bar(display_data,x='Household ID',y=cost_col,title="Cost per Household"),use_container_width=True)

# ... keep other plots and advanced analytics as before ...

