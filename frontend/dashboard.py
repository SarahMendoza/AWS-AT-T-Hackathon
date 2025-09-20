import streamlit as st
import pandas as pd
import numpy as np
import requests
import time
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import folium
from streamlit_folium import st_folium
from map_creation import create_folium_map

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
    try:
        response = requests.get(f"{BACKEND_URL}/api/health", timeout=5)
        return response.status_code == 200
    except:
        return False


@st.cache_data(ttl=60)
def get_tower_data():
    try:
        response = requests.get(f"{BACKEND_URL}/api/towers", timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data['success']:
                return pd.DataFrame(data['data'])
        return pd.DataFrame()
    except Exception as e:
        st.error(f"Error fetching tower data: {str(e)}")
        return pd.DataFrame()

@st.cache_data(ttl=60)
def get_predicted_outage_data():
    try:
        response = requests.get(f"{BACKEND_URL}/api/predicted-outages", timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data['success']:
                return pd.DataFrame(data['data'])
        return pd.DataFrame()
    except Exception as e:
        st.error(f"Error fetching predicted outage data: {str(e)}")
        return pd.DataFrame()

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


st.markdown("### Cell and Predicted Outages Map")

tower_data = get_tower_data()
outage_data = get_predicted_outage_data()
m = create_folium_map(tower_data, outage_data)
st_data = st_folium(m, width=1000)


#     if st.session_state.backend_connected:
#         # Urgent Areas Information
#         st.markdown("### 🚨 Urgent Weather Areas")
#         alert_areas = get_alert_areas()
        
#         if alert_areas:
#             st.write(f"**{len(alert_areas)} active alerts**")
#             for area in alert_areas[:3]:  # Show first 3 alerts
#                 with st.expander(f"⚠️ {area['event']}", expanded=False):
#                     st.write(f"**Severity:** {area.get('severity', 'Unknown')}")
#                     st.write(f"**Urgency:** {area.get('urgency', 'Unknown')}")
#                     st.write(f"**Effective:** {area.get('effective', 'Unknown')}")
#                     st.write(f"**Expires:** {area.get('expires', 'Unknown')}")
                    
#             if len(alert_areas) > 3:
#                 st.caption(f"... and {len(alert_areas) - 3} more alerts")
#         else:
#             st.success("No urgent weather alerts")
        
#         # Filters
#         st.markdown("### 🔍 Filters")
        
#         # Get filter options from backend
#         tower_options = get_tower_options()
        
#         if tower_options:
#             # Technology filter
#             tech_options = ['All'] + tower_options.get('technologies', [])
#             selected_tech = st.selectbox("Technology", tech_options)
            
#             # Status filter
#             status_options = ['All'] + tower_options.get('statuses', [])
#             selected_status = st.selectbox("Status", status_options)
            
#             # Signal strength filter
#             signal_range = tower_options.get('signal_range', {'min': -120, 'max': -60})
#             min_signal, max_signal = st.slider(
#                 "Signal Strength Range (dBm)",
#                 float(signal_range['min']),
#                 float(signal_range['max']),
#                 (float(signal_range['min']), float(signal_range['max']))
#             )
            
#             # Number of towers
#             num_towers = st.slider("Number of Towers", 10, 200, 50)
#         else:
#             st.error("Unable to load filter options")
#             selected_tech = 'All'
#             selected_status = 'All'
#             min_signal, max_signal = -120, -60
#             num_towers = 50
        
#         # Auto-refresh toggle
#         auto_refresh = st.checkbox("Auto-refresh (30s)", value=False)
        
#         # Manual refresh button
#         if st.button("🔄 Refresh Data"):
#             st.cache_data.clear()
#             st.rerun()
    
#     else:
#         st.warning("Connect to backend to access dashboard features")

# # Auto-refresh logic
# if st.session_state.backend_connected and auto_refresh:
#     time.sleep(30)
#     st.rerun()

# # Main dashboard
# st.markdown('<h1 class="main-header">FirstNet Cell Tower Deployment Dashboard</h1>', unsafe_allow_html=True)

# if not st.session_state.backend_connected:
#     st.error("Dashboard unavailable - please check backend connection")
#     st.stop()

# # Get data from backend
# df_towers, total_count, filtered_count = get_tower_data(
#     selected_tech, selected_status, min_signal, max_signal, num_towers
# )
# network_metrics = get_network_metrics(num_towers)
# alerts = get_alerts(num_towers)
# alert_areas = get_alert_areas()

# # Key metrics row
# if network_metrics:
#     col1, col2, col3, col4, col5 = st.columns(5)
#     with col1:
#         st.metric(
#             "Total Towers", 
#             network_metrics.get('total_towers', 0),
#             delta=f"{filtered_count} filtered"
#         )
#     with col2:
#         availability = network_metrics.get('network_availability', 0)
#         st.metric(
#             "Network Availability", 
#             f"{availability:.1f}%",
#             delta=f"{'🟢' if availability > 95 else '🟡' if availability > 90 else '🔴'}"
#         )
#     with col3:
#         st.metric(
#             "Avg Signal Strength", 
#             f"{network_metrics.get('avg_signal_strength', 0):.1f} dBm"
#         )
#     with col4:
#         st.metric(
#             "Total Coverage", 
#             f"{network_metrics.get('total_coverage_area', 0):.1f} km²"
#         )
#     with col5:
#         st.metric(
#             "Connected Devices", 
#             f"{network_metrics.get('total_connected_devices', 0):,}"
#         )
# else:
#     st.error("Unable to load network metrics")

# # Map and charts row
# col1, col2 = st.columns([3, 1])

# if alert_areas:
#     col1, col2 = st.columns([2, 1])
    
#     with col1:
#         st.markdown("### 🗺️ Cell Tower Map")
        
#         # Create color mapping for status
#         color_map = {'Active': '#28a745', 'Inactive': '#dc3545', 'Maintenance': '#ffc107'}
#         df_towers['color'] = df_towers['status'].map(color_map)
        
#         # Streamlit map
#         st.map(
#             df_towers, 
#             latitude="latitude", 
#             longitude="longitude", 
#             size="coverage_radius",
#             color="color"
#         )
        
#         # Show filtered towers count
#         st.info(f"Showing {filtered_count} towers out of {total_count} total")
    
#     with col2:
#         st.markdown("### 📊 Alert Statistics")
        
#         if alert_areas:
#             # Alert type distribution
#             alert_types = {}
#             total_zones = 0
            
#             for area in alert_areas:
#                 event_type = area['event']
#                 zones_count = len(area.get('zone_circles', []))
#                 alert_types[event_type] = alert_types.get(event_type, 0) + zones_count
#                 total_zones += zones_count
            
#             # Create pie chart for alert types
#             if alert_types:
#                 fig_pie = px.pie(
#                     values=list(alert_types.values()),
#                     names=list(alert_types.keys()),
#                     title="Alert Types by Zone Count"
#                 )
#                 fig_pie.update_layout(height=300, showlegend=True)
#                 st.plotly_chart(fig_pie, use_container_width=True)
            
#             # Alert urgency/severity stats
#             st.markdown("### 🎯 Alert Details")
            
#             severity_counts = {}
#             urgency_counts = {}
            
#             for area in alert_areas:
#                 severity = area.get('severity', 'Unknown')
#                 urgency = area.get('urgency', 'Unknown')
                
#                 severity_counts[severity] = severity_counts.get(severity, 0) + 1
#                 urgency_counts[urgency] = urgency_counts.get(urgency, 0) + 1
            
#             col_sev, col_urg = st.columns(2)
            
#             with col_sev:
#                 st.markdown("**Severity**")
#                 for severity, count in severity_counts.items():
#                     emoji = "🔴" if severity in ['Extreme', 'Severe'] else "🟡" if severity == 'Moderate' else "🟢"
#                     st.markdown(f"{emoji} {severity}: {count}")
            
#             with col_urg:
#                 st.markdown("**Urgency**")
#                 for urgency, count in urgency_counts.items():
#                     emoji = "⚡" if urgency == 'Immediate' else "⏰" if urgency == 'Expected' else "📋"
#                     st.markdown(f"{emoji} {urgency}: {count}")
            
#             # Show metrics
#             st.metric("Total Alerts", len(alert_areas))
#             st.metric("Total Zones Affected", total_zones)
            
#         else:
#             st.info("No alert statistics available")
            
#             # Show a placeholder chart
#             fig_placeholder = go.Figure()
#             fig_placeholder.add_annotation(
#                 text="No Active Alerts",
#                 xref="paper", yref="paper",
#                 x=0.5, y=0.5,
#                 showarrow=False,
#                 font=dict(size=20, color="gray")
#             )
#             fig_placeholder.update_layout(
#                 height=300,
#                 xaxis=dict(visible=False),
#                 yaxis=dict(visible=False),
#                 plot_bgcolor='rgba(0,0,0,0)'
#             )
#             st.plotly_chart(fig_placeholder, use_container_width=True)

# else:
#     st.warning("⚠️ No urgent weather areas data available or unable to connect to backend")

# # Remove the Performance metrics section since we're focusing on weather alerts only
# # Performance metrics section removed - focusing on weather alerts

# # Remove detailed data table section since we're focusing on weather alerts
# # Detailed data table section removed - focusing on weather alerts

# # Alert system
# st.markdown("### 🚨 System Alerts")
# if alerts:
#     for alert in alerts:
#         if alert['type'] == 'success':
#             st.success(f"{alert['icon']} {alert['message']}")
#         elif alert['type'] == 'warning':
#             st.warning(f"{alert['icon']} {alert['message']}")
#         elif alert['type'] == 'info':
#             st.info(f"{alert['icon']} {alert['message']}")
#         else:
#             st.error(f"{alert['icon']} {alert['message']}")
# else:
#     st.error("Unable to load system alerts")

# # Footer
# st.markdown("---")
# st.markdown(
#     f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | "
#     f"Data points: {filtered_count} towers | "
#     f"Backend: {'🟢 Connected' if st.session_state.backend_connected else '🔴 Disconnected'}"
# )