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
import plotly.graph_objects as go
from fpdf import FPDF
import io
import requests
from datetime import datetime
import base64

# ---------- Page Config ----------
st.set_page_config(layout="wide", page_title="Smart Energy Dashboard", page_icon="💡")

# ---------- Title ----------
st.title("💡 Smart Energy Awareness & Optimization Dashboard")
st.markdown("---")

# ---------- Session State Initialization ----------
if 'data' not in st.session_state:
    # Load or create sample data
    try:
        st.session_state.data = pd.read_csv("energy_data_100.csv")
        # Standardize categorical columns
        for col in ['AC Used', 'LED Used', 'Renewable', 'Implemented Tips?']:
            st.session_state.data[col] = st.session_state.data[col].str.title()
    except FileNotFoundError:
        # Create sample data if file missing
        np.random.seed(42)
        n = 100
        st.session_state.data = pd.DataFrame({
            "Household ID": range(1, n+1),
            "Household Type": np.random.choice(["Apartment", "Villa", "Independent House"], n),
            "Occupants": np.random.randint(1, 8, n),
            "Daily Energy (kWh)": np.random.randint(10, 80, n),
            "AC Used": np.random.choice(["Yes", "No"], n, p=[0.6, 0.4]),
            "LED Used": np.random.choice(["Yes", "No"], n, p=[0.5, 0.5]),
            "Renewable": np.random.choice(["Yes", "No"], n, p=[0.3, 0.7]),
            "Implemented Tips?": np.random.choice(["Yes", "No"], n, p=[0.4, 0.6])
        })
        st.session_state.data["Cost (₹)"] = st.session_state.data["Daily Energy (kWh)"] * 9
        for col in ['AC Used', 'LED Used', 'Renewable', 'Implemented Tips?']:
            st.session_state.data[col] = st.session_state.data[col].str.title()

# Currency conversion rates
conversion_rate_hkd = 0.084
conversion_rate_usd = 0.011
st.session_state.data['Cost (HKD)'] = st.session_state.data['Cost (₹)'] * conversion_rate_hkd
st.session_state.data['Cost (USD)'] = st.session_state.data['Cost (₹)'] * conversion_rate_usd

# ---------- Helper Functions ----------
def safe_mean(series, fallback=None):
    return fallback if series.empty else series.mean()

def get_currency_symbol(currency):
    if currency == "INR":
        return "₹"
    elif currency == "HKD":
        return "HKD"
    else:
        return "$"

# ---------- Sidebar: Filters & Controls ----------
st.sidebar.header("⚙️ Controls")

# Currency selector
currency = st.sidebar.radio("💱 Select Currency", options=["INR", "HKD", "USD"])
cost_col = f"Cost ({currency})"
currency_symbol = get_currency_symbol(currency)

# File upload
st.sidebar.subheader("📂 Upload Your Own Data")
uploaded_file = st.sidebar.file_uploader("Choose a CSV file", type="csv")
if uploaded_file is not None:
    new_data = pd.read_csv(uploaded_file)
    # Standardize columns
    for col in ['AC Used', 'LED Used', 'Renewable', 'Implemented Tips?']:
        if col in new_data.columns:
            new_data[col] = new_data[col].str.title()
    # Add cost columns if missing
    if 'Cost (₹)' not in new_data.columns:
        new_data['Cost (₹)'] = new_data['Daily Energy (kWh)'] * 9
    new_data['Cost (HKD)'] = new_data['Cost (₹)'] * conversion_rate_hkd
    new_data['Cost (USD)'] = new_data['Cost (₹)'] * conversion_rate_usd
    st.session_state.data = new_data
    st.sidebar.success("Data loaded successfully!")

# Filtering options
st.sidebar.subheader("🔎 Filter Households")
household_types = st.sidebar.multiselect(
    "Household Type",
    options=st.session_state.data['Household Type'].unique(),
    default=st.session_state.data['Household Type'].unique()
)
ac_filter = st.sidebar.multiselect("AC Used", options=['Yes','No'], default=['Yes','No'])
led_filter = st.sidebar.multiselect("LED Used", options=['Yes','No'], default=['Yes','No'])
renewable_filter = st.sidebar.multiselect("Renewable", options=['Yes','No'], default=['Yes','No'])
tips_filter = st.sidebar.multiselect("Implemented Tips?", options=['Yes','No'], default=['Yes','No'])

# Additional numeric filters
min_energy, max_energy = st.sidebar.slider(
    "Daily Energy (kWh)",
    min_value=float(st.session_state.data['Daily Energy (kWh)'].min()),
    max_value=float(st.session_state.data['Daily Energy (kWh)'].max()),
    value=(float(st.session_state.data['Daily Energy (kWh)'].min()),
           float(st.session_state.data['Daily Energy (kWh)'].max()))
)
min_cost, max_cost = st.sidebar.slider(
    f"Daily Cost ({currency_symbol})",
    min_value=float(st.session_state.data[cost_col].min()),
    max_value=float(st.session_state.data[cost_col].max()),
    value=(float(st.session_state.data[cost_col].min()),
           float(st.session_state.data[cost_col].max()))
)
min_occupants, max_occupants = st.sidebar.slider(
    "Occupants",
    min_value=int(st.session_state.data['Occupants'].min()),
    max_value=int(st.session_state.data['Occupants'].max()),
    value=(int(st.session_state.data['Occupants'].min()),
           int(st.session_state.data['Occupants'].max()))
)

# Apply filters
filtered_data = st.session_state.data[
    (st.session_state.data['Household Type'].isin(household_types)) &
    (st.session_state.data['AC Used'].isin(ac_filter)) &
    (st.session_state.data['LED Used'].isin(led_filter)) &
    (st.session_state.data['Renewable'].isin(renewable_filter)) &
    (st.session_state.data['Implemented Tips?'].isin(tips_filter)) &
    (st.session_state.data['Daily Energy (kWh)'] >= min_energy) &
    (st.session_state.data['Daily Energy (kWh)'] <= max_energy) &
    (st.session_state.data[cost_col] >= min_cost) &
    (st.session_state.data[cost_col] <= max_cost) &
    (st.session_state.data['Occupants'] >= min_occupants) &
    (st.session_state.data['Occupants'] <= max_occupants)
]

# Data management buttons
st.sidebar.subheader("➕ Add New Household")
with st.sidebar.form("add_household"):
    hh_type = st.selectbox("Household Type", ["Apartment", "Villa", "Independent House"])
    occupants = st.number_input("Occupants", min_value=1, max_value=10, value=3)
    daily_energy = st.number_input("Daily Energy (kWh)", min_value=1, max_value=200, value=30)
    ac = st.selectbox("AC Used", ["Yes", "No"])
    led = st.selectbox("LED Used", ["Yes", "No"])
    renewable = st.selectbox("Renewable", ["Yes", "No"])
    tips = st.selectbox("Implemented Tips?", ["Yes", "No"])
    submitted = st.form_submit_button("Add Household")
    if submitted:
        new_id = st.session_state.data["Household ID"].max() + 1
        new_row = {
            "Household ID": new_id,
            "Household Type": hh_type,
            "Occupants": occupants,
            "Daily Energy (kWh)": daily_energy,
            "Cost (₹)": daily_energy * 9,
            "AC Used": ac,
            "LED Used": led,
            "Renewable": renewable,
            "Implemented Tips?": tips,
            "Cost (HKD)": daily_energy * 9 * conversion_rate_hkd,
            "Cost (USD)": daily_energy * 9 * conversion_rate_usd
        }
        st.session_state.data = pd.concat([st.session_state.data, pd.DataFrame([new_row])], ignore_index=True)
        st.sidebar.success(f"✅ Household {new_id} added!")

st.sidebar.subheader("🗑️ Delete Household")
if not st.session_state.data.empty:
    del_id = st.sidebar.selectbox("Select Household ID to Delete", options=st.session_state.data['Household ID'].tolist())
    if st.sidebar.button("Delete Household"):
        st.session_state.data = st.session_state.data[st.session_state.data['Household ID'] != del_id]
        st.sidebar.success(f"✅ Household {del_id} deleted!")

if st.sidebar.button("🔄 Reset to Original Data"):
    # Reload original data
    try:
        st.session_state.data = pd.read_csv("energy_data_100.csv")
        for col in ['AC Used','LED Used','Renewable','Implemented Tips?']:
            st.session_state.data[col] = st.session_state.data[col].str.title()
        st.session_state.data['Cost (HKD)'] = st.session_state.data['Cost (₹)'] * conversion_rate_hkd
        st.session_state.data['Cost (USD)'] = st.session_state.data['Cost (₹)'] * conversion_rate_usd
        st.sidebar.success("Data reset to original!")
    except:
        st.sidebar.error("Original file not found.")

# ---------- Metrics ----------
avg_energy = safe_mean(filtered_data['Daily Energy (kWh)'], fallback=st.session_state.data['Daily Energy (kWh)'].mean())
avg_cost = safe_mean(filtered_data[cost_col], fallback=safe_mean(st.session_state.data[cost_col]))
tips_percent = safe_mean((filtered_data['Implemented Tips?']=='Yes')*100, fallback=(st.session_state.data['Implemented Tips?']=='Yes').mean()*100)
renewable_percent = safe_mean((filtered_data['Renewable']=='Yes')*100, fallback=(st.session_state.data['Renewable']=='Yes').mean()*100)

st.subheader("📊 Key Metrics")
col1, col2, col3, col4 = st.columns(4)
col1.metric("Avg Energy (kWh)", f"{avg_energy:.2f}")
col2.metric(f"Avg Cost ({currency_symbol})", f"{avg_cost:.2f}")
col3.metric("% Implemented Tips", f"{tips_percent:.1f}%")
col4.metric("% Using Renewable", f"{renewable_percent:.1f}%")

# ---------- Data Table with Color Coding ----------
st.subheader("🏠 Household Energy Data")
display_data = filtered_data if not filtered_data.empty else st.session_state.data
if filtered_data.empty:
    st.info("⚠️ No households match your filter. Showing overall dataset as fallback.")

# Add efficiency score
display_data['Efficiency Score'] = 100 - (display_data['Daily Energy (kWh)'] / display_data['Daily Energy (kWh)'].max() * 100)

def color_efficiency(val):
    if val >= 80:
        return 'background-color: #d4edda'
    elif val >= 50:
        return 'background-color: #fff3cd'
    else:
        return 'background-color: #f8d7da'

styled_df = display_data[['Household ID', 'Household Type', 'Occupants', 'Daily Energy (kWh)', cost_col,
                          'AC Used', 'LED Used', 'Renewable', 'Implemented Tips?', 'Efficiency Score']].style.applymap(color_efficiency, subset=['Efficiency Score'])
st.dataframe(styled_df)

# ---------- Interactive Visualizations with Plotly ----------
st.subheader("📈 Daily Energy Usage (kWh)")
fig_energy = px.line(display_data, x=display_data.index, y='Daily Energy (kWh)', title="Energy Trend")
st.plotly_chart(fig_energy, use_container_width=True)

st.subheader(f"💰 Daily Cost per Household ({currency_symbol})")
fig_cost = px.bar(display_data, x='Household ID', y=cost_col, title="Cost per Household")
st.plotly_chart(fig_cost, use_container_width=True)

st.subheader("✅ Households Implementing Energy-Saving Tips")
fig_tips = px.pie(display_data, names='Implemented Tips?', title="Energy-Saving Tips Implementation", color_discrete_sequence=['#66b3ff','#ff9999'])
st.plotly_chart(fig_tips, use_container_width=True)

st.subheader("🌞 Renewable Energy Adoption")
fig_renew = px.pie(display_data, names='Renewable', title="Renewable Energy Adoption", color_discrete_sequence=['#99ff99','#ffcc99'])
st.plotly_chart(fig_renew, use_container_width=True)

st.subheader("❄️ AC Usage vs Daily Energy")
fig_box = px.box(display_data, x='AC Used', y='Daily Energy (kWh)', title="Energy Distribution by AC Usage")
st.plotly_chart(fig_box, use_container_width=True)

st.subheader("👥 Energy vs Number of Occupants")
fig_scatter = px.scatter(display_data, x='Occupants', y='Daily Energy (kWh)', color='LED Used',
                         title="Energy vs Occupants (colored by LED usage)", trendline="ols")
st.plotly_chart(fig_scatter, use_container_width=True)

st.subheader("⚡ Energy Usage per Occupant")
display_data['Energy per Occupant'] = display_data['Daily Energy (kWh)'] / display_data['Occupants']
fig_energy_per = px.bar(display_data, x='Household ID', y='Energy per Occupant', title="Energy per Occupant")
st.plotly_chart(fig_energy_per, use_container_width=True)

st.subheader("🏘️ Avg Energy Usage by Household Type")
avg_by_type = display_data.groupby('Household Type')['Daily Energy (kWh)'].mean().reset_index()
fig_type = px.bar(avg_by_type, x='Household Type', y='Daily Energy (kWh)', title="Average Energy by Household Type")
st.plotly_chart(fig_type, use_container_width=True)

# ---------- Advanced Analytics ----------
st.markdown("---")
st.subheader("🧠 Advanced Analytics")

# Prepare data for ML
ml_data = display_data.copy()
label_enc = LabelEncoder()
for col in ['AC Used','LED Used','Renewable']:
    ml_data[col] = label_enc.fit_transform(ml_data[col])
X = ml_data[['Occupants','AC Used','LED Used','Renewable']]
y = ml_data['Daily Energy (kWh)']

# Train/Test split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Random Forest Model
rf = RandomForestRegressor(n_estimators=100, random_state=42)
rf.fit(X_train, y_train)
y_pred = rf.predict(X_test)
mae = mean_absolute_error(y_test, y_pred)
r2 = r2_score(y_test, y_pred)

st.write(f"**Random Forest Model Performance:**")
st.write(f"- Mean Absolute Error: {mae:.2f} kWh")
st.write(f"- R² Score: {r2:.2f}")

# Feature Importance
feature_imp = pd.DataFrame({'Feature': X.columns, 'Importance': rf.feature_importances_}).sort_values('Importance', ascending=False)
fig_imp = px.bar(feature_imp, x='Importance', y='Feature', orientation='h', title="Feature Importance (Random Forest)")
st.plotly_chart(fig_imp, use_container_width=True)

# Anomaly Detection
iso_forest = IsolationForest(contamination=0.1, random_state=42)
ml_data['Anomaly'] = iso_forest.fit_predict(X)
anomalies = ml_data[ml_data['Anomaly'] == -1]
st.write(f"**Anomaly Detection:** {len(anomalies)} households flagged as unusual (potential outliers).")
if not anomalies.empty:
    st.dataframe(anomalies[['Household ID', 'Daily Energy (kWh)', cost_col, 'AC Used', 'LED Used']])

# Clustering
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)
kmeans = KMeans(n_clusters=3, random_state=42)
display_data['Cluster'] = kmeans.fit_predict(X_scaled)
fig_cluster = px.scatter(display_data, x='Daily Energy (kWh)', y='Occupants', color='Cluster',
                         title="Household Segments (Clusters)", hover_data=['Household ID'])
st.plotly_chart(fig_cluster, use_container_width=True)
st.write("**Cluster Characteristics:**")
for i in range(3):
    cluster_data = display_data[display_data['Cluster'] == i]
    st.write(f"Cluster {i}: {len(cluster_data)} households, avg energy {cluster_data['Daily Energy (kWh)'].mean():.2f} kWh, avg occupants {cluster_data['Occupants'].mean():.2f}")

# What-If Simulation
st.subheader("💡 What-If Simulator")
with st.expander("Simulate Energy Savings"):
    sim_household = st.selectbox("Select Household ID", display_data['Household ID'].tolist())
    sim_row = display_data[display_data['Household ID'] == sim_household].iloc[0]
    st.write(f"Current Daily Energy: {sim_row['Daily Energy (kWh)']} kWh | Cost: {currency_symbol}{sim_row[cost_col]:.2f}")

    led_savings = st.checkbox("Switch to LED bulbs")
    ac_optimize = st.checkbox("Optimize AC usage (reduce 20% energy)")
    solar_adopt = st.checkbox("Adopt solar panels (reduce 30% energy)")

    new_energy = sim_row['Daily Energy (kWh)']
    if led_savings and sim_row['LED Used'] == 'No':
        new_energy *= 0.9  # 10% reduction
    if ac_optimize and sim_row['AC Used'] == 'Yes':
        new_energy *= 0.8  # 20% reduction
    if solar_adopt and sim_row['Renewable'] == 'No':
        new_energy *= 0.7  # 30% reduction

    new_cost = new_energy * (sim_row[cost_col] / sim_row['Daily Energy (kWh)'])
    st.write(f"**New Daily Energy:** {new_energy:.2f} kWh")
    st.write(f"**New Daily Cost:** {currency_symbol}{new_cost:.2f}")
    st.write(f"**Daily Savings:** {currency_symbol}{sim_row[cost_col] - new_cost:.2f}")

# ---------- Personalized Recommendations ----------
st.subheader("📝 Data-Driven Recommendations")
recs = []
if avg_cost > safe_mean(display_data[display_data['LED Used']=='Yes'][cost_col], fallback=avg_cost):
    recs.append("- Encourage households to switch to LED bulbs to save cost.")
if avg_energy > safe_mean(display_data[display_data['AC Used']=='No']['Daily Energy (kWh)'], fallback=avg_energy):
    recs.append("- Reduce AC usage or optimize temperature settings to save energy.")
if renewable_percent < 30:
    recs.append("- Promote renewable energy adoption for higher efficiency.")
if tips_percent < 50:
    recs.append("- More households should implement energy-saving tips to reduce consumption.")
if not recs:
    recs.append("- Great job! Your selected households are already quite efficient.")
for rec in recs:
    st.write(rec)

# Top 5 Energy-Saving Tips
st.subheader("💡 Top 5 Energy-Saving Tips")
st.write("""
1. Turn off unused appliances.  
2. Use LED bulbs instead of CFL/Incandescent.  
3. Reduce AC usage or set optimal temperature (24°C).  
4. Install solar panels if possible.  
5. Optimize washing machine usage and laundry loads.
""")

# ---------- PDF Report Generation ----------
st.subheader("📄 Generate PDF Report")
if st.button("Generate Report"):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="Smart Energy Dashboard Report", ln=True, align='C')
    pdf.cell(200, 10, txt=f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}", ln=True, align='C')
    pdf.ln(10)
    pdf.cell(200, 10, txt=f"Key Metrics:", ln=True)
    pdf.cell(200, 10, txt=f"Avg Energy: {avg_energy:.2f} kWh", ln=True)
    pdf.cell(200, 10, txt=f"Avg Cost: {currency_symbol}{avg_cost:.2f}", ln=True)
    pdf.cell(200, 10, txt=f"% Implemented Tips: {tips_percent:.1f}%", ln=True)
    pdf.cell(200, 10, txt=f"% Renewable: {renewable_percent:.1f}%", ln=True)
    pdf.ln(10)
    pdf.cell(200, 10, txt="Recommendations:", ln=True)
    for rec in recs:
        pdf.cell(200, 10, txt=rec, ln=True)
    # Save PDF to bytes
    pdf_output = io.BytesIO()
    pdf.output(pdf_output)
    pdf_output.seek(0)
    b64 = base64.b64encode(pdf_output.read()).decode()
    href = f'<a href="data:application/octet-stream;base64,{b64}" download="energy_report.pdf">Download PDF Report</a>'
    st.markdown(href, unsafe_allow_html=True)

# ---------- Weather API Integration (Optional) ----------
st.subheader("🌤️ Weather Correlation")
city = st.text_input("Enter city name for weather data (optional)", value="Mumbai")
if city:
    try:
        # Using Open-Meteo free API (no key needed)
        geo_url = f"https://geocoding-api.open-meteo.com/v1/search?name={city}&count=1"
        geo_resp = requests.get(geo_url)
        geo_data = geo_resp.json()
        if geo_data.get("results"):
            lat = geo_data["results"][0]["latitude"]
            lon = geo_data["results"][0]["longitude"]
            weather_url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true"
            weather_resp = requests.get(weather_url)
            weather = weather_resp.json()
            temp = weather["current_weather"]["temperature"]
            st.write(f"Current temperature in {city}: {temp}°C")
            st.write("Note: Higher temperatures often correlate with increased AC usage and energy consumption.")
        else:
            st.write("City not found.")
    except Exception as e:
        st.write("Could not fetch weather data.")

# ---------- Download Filtered Data ----------
st.subheader("💾 Download Filtered Data")
@st.cache_data
def convert_df(df):
    return df.to_csv(index=False).encode('utf-8')

display_data_download = display_data.copy()
display_data_download["Cost"] = display_data_download[cost_col]
csv = convert_df(display_data_download)
st.download_button(
    label=f"Download Filtered Data ({currency}) as CSV",
    data=csv,
    file_name=f'filtered_energy_data_{currency}.csv',
    mime='text/csv'
)
