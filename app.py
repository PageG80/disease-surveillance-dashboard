import sqlite3
import pandas as pd
import streamlit as st
import plotly.express as px
import folium
from streamlit_folium import st_folium

st.set_page_config(
    page_title="Geospatial Disease Surveillance & Outbreak Alert",
    page_icon="🦠",
    layout="wide"
)

@st.cache_data
def load_data():
    conn = sqlite3.connect('data/surveillance.db')
    query = "SELECT * FROM outbreak_reports"
    df = pd.read_sql(query, conn)
    conn.close()
    df['report_date'] = pd.to_datetime(df['report_date'])
    return df

df = load_data()

st.sidebar.header("🗺️ Public Health Control Panel")
selected_disease = st.sidebar.selectbox("Filter Disease", options=["All"] + list(df['disease'].unique()))
selected_week = st.sidebar.slider("Select Epidemiological Week", int(df['week_number'].min()), int(df['week_number'].max()), int(df['week_number'].max()))

filtered_df = df[(df['week_number'] == selected_week)]
if selected_disease != "All":
    filtered_df = filtered_df[filtered_df['disease'] == selected_disease]

st.title("🦠 Geospatial Disease Surveillance & Outbreak Alert System")
st.markdown("Early-warning public health intelligence tracking Nairobi sub-county outbreaks, case surges, and drug stock levels.")

col1, col2, col3, col4 = st.columns(4)

total_cases = int(filtered_df['cases_reported'].sum())
active_outbreaks = int(filtered_df['outbreak_alert'].sum())
stock_risks = int(filtered_df[filtered_df['drug_stock_left'] < 100].shape[0])
avg_cases_per_county = int(filtered_df['cases_reported'].mean()) if len(filtered_df) > 0 else 0

col1.metric("Total Cases Reported (Wk)", f"{total_cases:,}")
col2.metric("Active Outbreak Alerts", f"{active_outbreaks}", delta_color="inverse")
col3.metric("Low Drug Stock Clinics", f"{stock_risks}", delta_color="inverse")
col4.metric("Avg Cases / Sub-County", f"{avg_cases_per_county}")

st.markdown("---")

row1_col1, row1_col2 = st.columns([1.2, 1])

with row1_col1:
    st.subheader(f"📍 Nairobi Sub-County Outbreak Hotspots (Week {selected_week})")
    
    m = folium.Map(location=[-1.2921, 36.8219], zoom_start=11, tiles="OpenStreetMap")
    
    for _, row in filtered_df.iterrows():
        is_alert = row['outbreak_alert'] == 1
        color = 'red' if is_alert else 'green'
        radius = min(max(row['cases_reported'] * 1.5, 8), 35)
        
        alert_status = "YES 🚨" if is_alert else "NO ✅"
        
        popup_text = f"""
        <b>Sub-County:</b> {row['sub_county']}<br>
        <b>Disease:</b> {row['disease']}<br>
        <b>Cases:</b> {row['cases_reported']}<br>
        <b>Outbreak Alert:</b> {alert_status}<br>
        <b>Drug Stock Left:</b> {row['drug_stock_left']} units
        """
        
        folium.CircleMarker(
            location=[row['latitude'], row['longitude']],
            radius=radius,
            color=color,
            fill=True,
            fill_color=color,
            fill_opacity=0.6,
            popup=folium.Popup(popup_text, max_width=300)
        ).add_to(m)
        
    st_folium(m, width=650, height=450, key="nairobi_map")

with row1_col2:
    st.subheader("📈 Case Surge vs Historical Average")
    trend_df = df[df['disease'] == selected_disease] if selected_disease != "All" else df
    weekly_trend = trend_df.groupby('week_number')[['cases_reported', 'historical_average']].sum().reset_index()
    
    fig_trend = px.line(
        weekly_trend, x='week_number', y=['cases_reported', 'historical_average'],
        labels={'value': 'Number of Cases', 'week_number': 'Epidemiological Week'},
        color_discrete_map={'cases_reported': '#e74c3c', 'historical_average': '#3498db'}
    )
    st.plotly_chart(fig_trend, use_container_width=True, key="trend_chart")

row2_col1, row2_col2 = st.columns(2)

with row2_col1:
    st.subheader("🚨 Active Outbreak Warning Log")
    outbreak_logs = df[(df['outbreak_alert'] == 1)][['week_number', 'sub_county', 'disease', 'cases_reported', 'historical_average']]
    st.dataframe(outbreak_logs.head(10), use_container_width=True)

with row2_col2:
    st.subheader("💊 Local Clinic Drug Inventory Status")
    inventory_df = filtered_df[['sub_county', 'disease', 'drug_stock_left', 'outbreak_alert']]
    st.dataframe(inventory_df.head(10), use_container_width=True)