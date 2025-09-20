import pandas as pd
import streamlit as st
import numpy as np
from numpy.random import default_rng as rng
import requests
import time
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Page configuration
st.set_page_config(
    page_title="FirstNet Deployment Dashboard",
    layout="wide",
    initial_sidebar_state="expanded",
    page_icon="📡"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-container {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .status-active {
        color: #28a745;
    }
    .status-inactive {
        color: #dc3545;
    }
    .status-maintenance {
        color: #ffc107;
    }
</style>
""", unsafe_allow_html=True)

# Function to generate realistic cell tower data
@st.cache_data
def generate_cell_tower_data(num_towers=50):
    """Generate realistic cell tower data with various attributes"""
    rng_gen = rng(42)  # Fixed seed for consistency
    
    # San Francisco Bay Area coordinates
    lat_center, lon_center = 37.7749, -122.4194
    lat_range, lon_range = 0.5, 0.7
    
    data = {
        'tower_id': [f'FN-{1000 + i}' for i in range(num_towers)],
        'latitude': lat_center + rng_gen.uniform(-lat_range, lat_range, num_towers),
        'longitude': lon_center + rng_gen.uniform(-lon_range, lon_range, num_towers),
        'signal_strength': rng_gen.uniform(-120, -60, num_towers),  # dBm
        'bandwidth': rng_gen.choice([20, 40, 80, 100], num_towers),  # MHz
        'technology': rng_gen.choice(['4G LTE', '5G', '5G mmWave'], num_towers, p=[0.4, 0.5, 0.1]),
        'status': rng_gen.choice(['Active', 'Inactive', 'Maintenance'], num_towers, p=[0.8, 0.1, 0.1]),
        'coverage_radius': rng_gen.uniform(0.5, 5.0, num_towers),  # km
        'installation_date': [
            datetime.now() - timedelta(days=int(rng_gen.uniform(30, 1095))) 
            for _ in range(num_towers)
        ],
        'data_usage_gb': rng_gen.uniform(100, 10000, num_towers),
        'connected_devices': rng_gen.poisson(500, num_towers),
        'uptime_percentage': rng_gen.uniform(95, 100, num_towers)
    }
    
    return pd.DataFrame(data)

# Function to get weather data (mock function - replace with real API)
@st.cache_data(ttl=300)  # Cache for 5 minutes
def get_weather_data():
    """Get current weather data for the region"""
    # This is mock data - replace with real weather API like OpenWeatherMap
    return {
        'temperature': 22.5,
        'humidity': 65,
        'wind_speed': 12.3,
        'precipitation': 0.0,
        'visibility': 10.0,
        'weather_condition': 'Clear',
        'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }

# Function to calculate network metrics
def calculate_network_metrics(df):
    """Calculate key network performance metrics"""
    active_towers = df[df['status'] == 'Active']
    
    metrics = {
        'total_towers': len(df),
        'active_towers': len(active_towers),
        'inactive_towers': len(df[df['status'] == 'Inactive']),
        'maintenance_towers': len(df[df['status'] == 'Maintenance']),
        'avg_signal_strength': active_towers['signal_strength'].mean() if len(active_towers) > 0 else 0,
        'total_coverage_area': active_towers['coverage_radius'].sum() * 3.14159 if len(active_towers) > 0 else 0,
        'avg_uptime': active_towers['uptime_percentage'].mean() if len(active_towers) > 0 else 0,
        'total_data_usage': df['data_usage_gb'].sum(),
        'total_connected_devices': df['connected_devices'].sum(),
        'network_availability': (len(active_towers) / len(df) * 100) if len(df) > 0 else 0
    }
    
    return metrics

# Generate data
df_towers = generate_cell_tower_data()
weather_data = get_weather_data()
network_metrics = calculate_network_metrics(df_towers)

# Sidebar
with st.sidebar:
    st.markdown('<h1 style="color: #1f77b4;">📡 FirstNet Dashboard</h1>', unsafe_allow_html=True)
    
    # Weather Information
    st.markdown("### 🌤️ Current Weather")
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Temperature", f"{weather_data['temperature']:.1f}°C")
        st.metric("Humidity", f"{weather_data['humidity']}%")
    with col2:
        st.metric("Wind Speed", f"{weather_data['wind_speed']} km/h")
        st.metric("Visibility", f"{weather_data['visibility']} km")
    
    st.info(f"Condition: {weather_data['weather_condition']}")
    st.caption(f"Last updated: {weather_data['last_updated']}")
    
    # Filters
    st.markdown("### 🔍 Filters")
    
    # Technology filter
    tech_options = ['All'] + list(df_towers['technology'].unique())
    selected_tech = st.selectbox("Technology", tech_options)
    
    # Status filter
    status_options = ['All'] + list(df_towers['status'].unique())
    selected_status = st.selectbox("Status", status_options)
    
    # Signal strength filter
    min_signal, max_signal = st.slider(
        "Signal Strength Range (dBm)",
        float(df_towers['signal_strength'].min()),
        float(df_towers['signal_strength'].max()),
        (float(df_towers['signal_strength'].min()), float(df_towers['signal_strength'].max()))
    )
    
    # Auto-refresh toggle
    auto_refresh = st.checkbox("Auto-refresh (30s)", value=False)
    
    if auto_refresh:
        time.sleep(30)
        st.rerun()

# Apply filters
filtered_df = df_towers.copy()
if selected_tech != 'All':
    filtered_df = filtered_df[filtered_df['technology'] == selected_tech]
if selected_status != 'All':
    filtered_df = filtered_df[filtered_df['status'] == selected_status]
filtered_df = filtered_df[
    (filtered_df['signal_strength'] >= min_signal) & 
    (filtered_df['signal_strength'] <= max_signal)
]

# Main dashboard
st.markdown('<h1 class="main-header">FirstNet Cell Tower Deployment Dashboard</h1>', unsafe_allow_html=True)

# Key metrics row
col1, col2, col3, col4, col5 = st.columns(5)
with col1:
    st.metric(
        "Total Towers", 
        network_metrics['total_towers'],
        delta=f"{len(filtered_df)} filtered"
    )
with col2:
    st.metric(
        "Network Availability", 
        f"{network_metrics['network_availability']:.1f}%",
        delta=f"{'🟢' if network_metrics['network_availability'] > 95 else '🟡' if network_metrics['network_availability'] > 90 else '🔴'}"
    )
with col3:
    st.metric(
        "Avg Signal Strength", 
        f"{network_metrics['avg_signal_strength']:.1f} dBm"
    )
with col4:
    st.metric(
        "Total Coverage", 
        f"{network_metrics['total_coverage_area']:.1f} km²"
    )
with col5:
    st.metric(
        "Connected Devices", 
        f"{network_metrics['total_connected_devices']:,}"
    )

# Map and charts row
col1, col2 = st.columns([2, 1])

with col1:
    st.markdown("### 🗺️ Cell Tower Map")
    
    if not filtered_df.empty:
        # Create color mapping for status
        color_map = {'Active': '#28a745', 'Inactive': '#dc3545', 'Maintenance': '#ffc107'}
        filtered_df['color'] = filtered_df['status'].map(color_map)
        
        # Streamlit map
        st.map(
            filtered_df, 
            latitude="latitude", 
            longitude="longitude", 
            size="coverage_radius",
            color="color"
        )
        
        # Show filtered towers count
        st.info(f"Showing {len(filtered_df)} towers out of {len(df_towers)} total")
    else:
        st.warning("No towers match the current filters.")

with col2:
    st.markdown("### 📊 Technology Distribution")
    tech_counts = df_towers['technology'].value_counts()
    fig_pie = px.pie(
        values=tech_counts.values, 
        names=tech_counts.index,
        title="Tower Technology Mix"
    )
    fig_pie.update_layout(height=300)
    st.plotly_chart(fig_pie, use_container_width=True)
    
    st.markdown("### 📈 Status Overview")
    status_counts = df_towers['status'].value_counts()
    colors = ['#28a745', '#dc3545', '#ffc107']  # Green, Red, Yellow
    fig_bar = px.bar(
        x=status_counts.index, 
        y=status_counts.values,
        color=status_counts.index,
        color_discrete_sequence=colors,
        title="Tower Status Distribution"
    )
    fig_bar.update_layout(height=300, showlegend=False)
    st.plotly_chart(fig_bar, use_container_width=True)

# Performance metrics row
st.markdown("### 📊 Performance Analytics")
col1, col2, col3 = st.columns(3)

with col1:
    # Signal strength distribution
    fig_hist = px.histogram(
        filtered_df, 
        x='signal_strength', 
        nbins=20,
        title="Signal Strength Distribution",
        labels={'signal_strength': 'Signal Strength (dBm)', 'count': 'Number of Towers'}
    )
    fig_hist.update_layout(height=300)
    st.plotly_chart(fig_hist, use_container_width=True)

with col2:
    # Data usage vs connected devices
    fig_scatter = px.scatter(
        filtered_df,
        x='connected_devices',
        y='data_usage_gb',
        color='technology',
        size='coverage_radius',
        title="Data Usage vs Connected Devices",
        labels={'connected_devices': 'Connected Devices', 'data_usage_gb': 'Data Usage (GB)'}
    )
    fig_scatter.update_layout(height=300)
    st.plotly_chart(fig_scatter, use_container_width=True)

with col3:
    # Uptime performance
    fig_box = px.box(
        filtered_df,
        x='status',
        y='uptime_percentage',
        title="Uptime by Status",
        labels={'uptime_percentage': 'Uptime %', 'status': 'Tower Status'}
    )
    fig_box.update_layout(height=300)
    st.plotly_chart(fig_box, use_container_width=True)

# Detailed data table
st.markdown("### 📋 Detailed Tower Information")
if st.checkbox("Show detailed tower data"):
    # Format the dataframe for display
    display_df = filtered_df.copy()
    display_df['installation_date'] = display_df['installation_date'].dt.strftime('%Y-%m-%d')
    display_df['signal_strength'] = display_df['signal_strength'].round(2)
    display_df['coverage_radius'] = display_df['coverage_radius'].round(2)
    display_df['data_usage_gb'] = display_df['data_usage_gb'].round(2)
    display_df['uptime_percentage'] = display_df['uptime_percentage'].round(2)
    
    # Select columns to display
    columns_to_show = [
        'tower_id', 'technology', 'status', 'signal_strength', 
        'bandwidth', 'connected_devices', 'uptime_percentage', 'installation_date'
    ]
    
    st.dataframe(
        display_df[columns_to_show],
        use_container_width=True,
        hide_index=True
    )

# Alert system
st.markdown("### 🚨 System Alerts")
alerts = []

# Check for low signal towers
low_signal_towers = df_towers[df_towers['signal_strength'] < -100]
if not low_signal_towers.empty:
    alerts.append(f"⚠️ {len(low_signal_towers)} towers have signal strength below -100 dBm")

# Check for low uptime
low_uptime_towers = df_towers[df_towers['uptime_percentage'] < 98]
if not low_uptime_towers.empty:
    alerts.append(f"⚠️ {len(low_uptime_towers)} towers have uptime below 98%")

# Check maintenance towers
maintenance_towers = df_towers[df_towers['status'] == 'Maintenance']
if not maintenance_towers.empty:
    alerts.append(f"🔧 {len(maintenance_towers)} towers are currently under maintenance")

if alerts:
    for alert in alerts:
        st.warning(alert)
else:
    st.success("✅ All systems operating normally")

# Footer
st.markdown("---")
st.markdown(
    f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | "
    f"Data points: {len(filtered_df)} towers"
)