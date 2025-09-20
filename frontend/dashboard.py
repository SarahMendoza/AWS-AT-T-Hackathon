import streamlit as st
import pandas as pd
import numpy as np
import requests
import time
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Configuration
BACKEND_URL = "http://localhost:5000"  # Change this to your backend URL

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
    .api-status {
        padding: 0.5rem;
        border-radius: 0.25rem;
        margin: 0.5rem 0;
    }
    .api-status-connected {
        background-color: #d4edda;
        color: #155724;
        border: 1px solid #c3e6cb;
    }
    .api-status-disconnected {
        background-color: #f8d7da;
        color: #721c24;
        border: 1px solid #f5c6cb;
    }
</style>
""", unsafe_allow_html=True)

# API Functions
@st.cache_data(ttl=300)
def check_backend_health():
    """Check if backend is healthy"""
    try:
        response = requests.get(f"{BACKEND_URL}/api/health", timeout=5)
        return response.status_code == 200
    except:
        return False

@st.cache_data(ttl=300)
def get_weather_data():
    """Get weather data from backend"""
    try:
        response = requests.get(f"{BACKEND_URL}/api/weather", timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data['success']:
                return data['data']
        return None
    except Exception as e:
        st.error(f"Error fetching weather data: {str(e)}")
        return None

@st.cache_data(ttl=60)
def get_tower_data(technology='All', status='All', min_signal=None, max_signal=None, num_towers=50):
    """Get tower data from backend with filters"""
    try:
        params = {
            'technology': technology,
            'status': status,
            'num_towers': num_towers
        }
        if min_signal is not None:
            params['min_signal'] = min_signal
        if max_signal is not None:
            params['max_signal'] = max_signal
            
        response = requests.get(f"{BACKEND_URL}/api/towers", params=params, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data['success']:
                return pd.DataFrame(data['data']), data['total_count'], data['filtered_count']
        return pd.DataFrame(), 0, 0
    except Exception as e:
        st.error(f"Error fetching tower data: {str(e)}")
        return pd.DataFrame(), 0, 0

@st.cache_data(ttl=60)
def get_network_metrics(num_towers=50):
    """Get network metrics from backend"""
    try:
        response = requests.get(f"{BACKEND_URL}/api/metrics", params={'num_towers': num_towers}, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data['success']:
                return data['data']
        return {}
    except Exception as e:
        st.error(f"Error fetching network metrics: {str(e)}")
        return {}

@st.cache_data(ttl=60)
def get_alerts(num_towers=50):
    """Get system alerts from backend"""
    try:
        response = requests.get(f"{BACKEND_URL}/api/alerts", params={'num_towers': num_towers}, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data['success']:
                return data['data']
        return []
    except Exception as e:
        st.error(f"Error fetching alerts: {str(e)}")
        return []

@st.cache_data(ttl=3600)
def get_tower_options():
    """Get available filter options from backend"""
    try:
        response = requests.get(f"{BACKEND_URL}/api/tower-options", timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data['success']:
                return data['data']
        return {}
    except Exception as e:
        st.error(f"Error fetching tower options: {str(e)}")
        return {}

# Initialize session state
if 'backend_connected' not in st.session_state:
    st.session_state.backend_connected = False

# Check backend connection
backend_healthy = check_backend_health()
st.session_state.backend_connected = backend_healthy

# Sidebar
with st.sidebar:
    st.markdown('<h1 style="color: #1f77b4;">📡 FirstNet Dashboard</h1>', unsafe_allow_html=True)
    
    # Backend status indicator
    if st.session_state.backend_connected:
        st.markdown(
            '<div class="api-status api-status-connected">🟢 Backend Connected</div>', 
            unsafe_allow_html=True
        )
    else:
        st.markdown(
            '<div class="api-status api-status-disconnected">🔴 Backend Disconnected</div>', 
            unsafe_allow_html=True
        )
        st.error(f"Cannot connect to backend at {BACKEND_URL}")
    
    if st.session_state.backend_connected:
        # Weather Information
        st.markdown("### 🌤️ Current Weather")
        weather_data = get_weather_data()
        
        if weather_data:
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Temperature", f"{weather_data['temperature']:.1f}°C")
                st.metric("Humidity", f"{weather_data['humidity']:.1f}%")
            with col2:
                st.metric("Wind Speed", f"{weather_data['wind_speed']:.1f} km/h")
                st.metric("Visibility", f"{weather_data['visibility']:.1f} km")
            
            st.info(f"Condition: {weather_data['weather_condition']}")
            st.caption(f"Last updated: {weather_data['last_updated']}")
        else:
            st.error("Unable to load weather data")
        
        # Filters
        st.markdown("### 🔍 Filters")
        
        # Get filter options from backend
        tower_options = get_tower_options()
        
        if tower_options:
            # Technology filter
            tech_options = ['All'] + tower_options.get('technologies', [])
            selected_tech = st.selectbox("Technology", tech_options)
            
            # Status filter
            status_options = ['All'] + tower_options.get('statuses', [])
            selected_status = st.selectbox("Status", status_options)
            
            # Signal strength filter
            signal_range = tower_options.get('signal_range', {'min': -120, 'max': -60})
            min_signal, max_signal = st.slider(
                "Signal Strength Range (dBm)",
                float(signal_range['min']),
                float(signal_range['max']),
                (float(signal_range['min']), float(signal_range['max']))
            )
            
            # Number of towers
            num_towers = st.slider("Number of Towers", 10, 200, 50)
        else:
            st.error("Unable to load filter options")
            selected_tech = 'All'
            selected_status = 'All'
            min_signal, max_signal = -120, -60
            num_towers = 50
        
        # Auto-refresh toggle
        auto_refresh = st.checkbox("Auto-refresh (30s)", value=False)
        
        # Manual refresh button
        if st.button("🔄 Refresh Data"):
            st.cache_data.clear()
            st.rerun()
    
    else:
        st.warning("Connect to backend to access dashboard features")

# Auto-refresh logic
if st.session_state.backend_connected and auto_refresh:
    time.sleep(30)
    st.rerun()

# Main dashboard
st.markdown('<h1 class="main-header">FirstNet Cell Tower Deployment Dashboard</h1>', unsafe_allow_html=True)

if not st.session_state.backend_connected:
    st.error("Dashboard unavailable - please check backend connection")
    st.stop()

# Get data from backend
df_towers, total_count, filtered_count = get_tower_data(
    selected_tech, selected_status, min_signal, max_signal, num_towers
)
network_metrics = get_network_metrics(num_towers)
alerts = get_alerts(num_towers)

# Key metrics row
if network_metrics:
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.metric(
            "Total Towers", 
            network_metrics.get('total_towers', 0),
            delta=f"{filtered_count} filtered"
        )
    with col2:
        availability = network_metrics.get('network_availability', 0)
        st.metric(
            "Network Availability", 
            f"{availability:.1f}%",
            delta=f"{'🟢' if availability > 95 else '🟡' if availability > 90 else '🔴'}"
        )
    with col3:
        st.metric(
            "Avg Signal Strength", 
            f"{network_metrics.get('avg_signal_strength', 0):.1f} dBm"
        )
    with col4:
        st.metric(
            "Total Coverage", 
            f"{network_metrics.get('total_coverage_area', 0):.1f} km²"
        )
    with col5:
        st.metric(
            "Connected Devices", 
            f"{network_metrics.get('total_connected_devices', 0):,}"
        )
else:
    st.error("Unable to load network metrics")

# Map and charts row
if not df_towers.empty:
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("### 🗺️ Cell Tower Map")
        
        # Create color mapping for status
        color_map = {'Active': '#28a745', 'Inactive': '#dc3545', 'Maintenance': '#ffc107'}
        df_towers['color'] = df_towers['status'].map(color_map)
        
        # Streamlit map
        st.map(
            df_towers, 
            latitude="latitude", 
            longitude="longitude", 
            size="coverage_radius",
            color="color"
        )
        
        # Show filtered towers count
        st.info(f"Showing {filtered_count} towers out of {total_count} total")
    
    with col2:
        # Get full dataset for distribution charts
        full_df, _, _ = get_tower_data('All', 'All', None, None, num_towers)
        
        if not full_df.empty:
            st.markdown("### 📊 Technology Distribution")
            tech_counts = full_df['technology'].value_counts()
            fig_pie = px.pie(
                values=tech_counts.values, 
                names=tech_counts.index,
                title="Tower Technology Mix"
            )
            fig_pie.update_layout(height=300)
            st.plotly_chart(fig_pie, use_container_width=True)
            
            st.markdown("### 📈 Status Overview")
            status_counts = full_df['status'].value_counts()
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
        else:
            st.error("Unable to load chart data")

else:
    col1, col2 = st.columns([2, 1])
    with col1:
        st.warning("No towers match the current filters or unable to load data.")
    with col2:
        st.warning("Chart data unavailable")

# Performance metrics row
if not df_towers.empty:
    st.markdown("### 📊 Performance Analytics")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # Signal strength distribution
        fig_hist = px.histogram(
            df_towers, 
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
            df_towers,
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
            df_towers,
            x='status',
            y='uptime_percentage',
            title="Uptime by Status",
            labels={'uptime_percentage': 'Uptime %', 'status': 'Tower Status'}
        )
        fig_box.update_layout(height=300)
        st.plotly_chart(fig_box, use_container_width=True)

# Detailed data table
if not df_towers.empty:
    st.markdown("### 📋 Detailed Tower Information")
    if st.checkbox("Show detailed tower data"):
        # Format the dataframe for display
        display_df = df_towers.copy()
        
        # Convert datetime strings back to datetime for formatting
        display_df['installation_date'] = pd.to_datetime(display_df['installation_date']).dt.strftime('%Y-%m-%d')
        display_df['signal_strength'] = pd.to_numeric(display_df['signal_strength']).round(2)
        display_df['coverage_radius'] = pd.to_numeric(display_df['coverage_radius']).round(2)
        display_df['data_usage_gb'] = pd.to_numeric(display_df['data_usage_gb']).round(2)
        display_df['uptime_percentage'] = pd.to_numeric(display_df['uptime_percentage']).round(2)
        
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
if alerts:
    for alert in alerts:
        if alert['type'] == 'success':
            st.success(f"{alert['icon']} {alert['message']}")
        elif alert['type'] == 'warning':
            st.warning(f"{alert['icon']} {alert['message']}")
        elif alert['type'] == 'info':
            st.info(f"{alert['icon']} {alert['message']}")
        else:
            st.error(f"{alert['icon']} {alert['message']}")
else:
    st.error("Unable to load system alerts")

# Footer
st.markdown("---")
st.markdown(
    f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | "
    f"Data points: {filtered_count} towers | "
    f"Backend: {'🟢 Connected' if st.session_state.backend_connected else '🔴 Disconnected'}"
)