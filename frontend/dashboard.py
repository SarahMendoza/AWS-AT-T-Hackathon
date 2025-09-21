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


@st.cache_data(ttl=300)
def get_tower_data():
    try:
        response = requests.get(f"{BACKEND_URL}/api/towers", timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data['success']:
                df = pd.DataFrame(data['data'])
                df['latitude'] = df['latitude'].astype(float)
                df['longitude'] = df['longitude'].astype(float)
                df['signal_strength'] = df['signal_strength'].astype(float)
                df['coverage_radius'] = df['coverage_radius'].astype(float)
                return df
        return pd.DataFrame()
    except Exception as e:
        st.error(f"Error fetching tower data: {str(e)}")
        return pd.DataFrame()

@st.cache_data(ttl=300)
def get_predicted_outage_data():
    try:
        response = requests.get(f"{BACKEND_URL}/api/predicted-outages", timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data['success']:
                df = pd.DataFrame(data['data'])
                df['center_latitude'] = df['center_latitude'].astype(float)
                df['center_longitude'] = df['center_longitude'].astype(float)
                df['radius'] = df['radius'].astype(float)
                return df
        return pd.DataFrame()
    except Exception as e:
        st.error(f"Error fetching predicted outage data: {str(e)}")
        return pd.DataFrame()

@st.cache_data(ttl=300)
def get_deployment_notes(cell_tower):
    try:
        response = requests.get(f"{BACKEND_URL}/api/deployment-notes", params={'tower_id': cell_tower['tower_id']}, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data['success']:
                return data['data']
        return pd.DataFrame()
    except Exception as e:
        st.error(f"Error fetching deployment notes: {str(e)}")
        return pd.DataFrame()

# @st.cache_data(ttl=300)
# def get_deployment_instructions_for_outage(outage):
#     try:
#         response = requests.get(f"{BACKEND_URL}/api/instructions-outage", params={'outage_id': 0}, timeout=10)
#         if response.status_code == 200:
#             data = response.json()
#             if data['success']:
#                 return data['data']
#         return pd.DataFrame()
#     except Exception as e:
#         st.error(f"Error fetching deployment instructions: {str(e)}")
#         return pd.DataFrame()

@st.cache_data(ttl=300)
def get_assistant_response(user_input, cell_tower):
    try:
        response = requests.get(
            f"{BACKEND_URL}/api/assistant", 
            params={
                'user_input': user_input, 
                'tower_id': cell_tower['tower_id']
            }, 
            timeout=10
        )
        if response.status_code == 200:
            data = response.json()
            if data['success']:
                return data['data']
        return pd.DataFrame()
    except Exception as e:
        st.error(f"Error fetching assistant response: {str(e)}")
        return pd.DataFrame()

# @st.cache_data(ttl=300)
# def get_assistant_response_for_outage(user_input, outage):
#     try:
#         response = requests.get(
#             f"{BACKEND_URL}/api/assistant-outage", 
#             params={
#                 'user_input': user_input, 
#                 'outage_id': 0
#             }, 
#             timeout=10
#         )
#         if response.status_code == 200:
#             data = response.json()
#             if data['success']:
#                 return data['data']
#         return pd.DataFrame()
#     except Exception as e:
#         st.error(f"Error fetching assistant response: {str(e)}")
#         return pd.DataFrame()

# Initialize session state
if 'backend_connected' not in st.session_state:
    st.session_state.backend_connected = False

if 'selected_tower' not in st.session_state:
    st.session_state.selected_tower = None

if 'selected_outage' not in st.session_state:
    st.session_state.selected_outage = None

if 'chat_area' not in st.session_state:
    st.session_state.chat_area = None

if 'messages' not in st.session_state:
    st.session_state.messages = []

if 'show_notes' not in st.session_state:
    st.session_state.show_notes = False

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

tower_data = get_tower_data()
outage_data = get_predicted_outage_data()

st.markdown("### Outages Map")
m = create_folium_map(tower_data, outage_data)
st_data = st_folium(m, width=1000)

if st_data["last_object_clicked"]:
    lat, lon = st_data["last_object_clicked"]['lat'], st_data["last_object_clicked"]['lng']
    
    # find the corresponding predicted outage or cell tower using lat lon
    cell_tower_matches = tower_data[
        (tower_data['latitude'] == lat) & 
        (tower_data['longitude'] == lon)
    ]
    outage_matches = outage_data[
        (outage_data['center_latitude']-0.5 <= lat) &
        (outage_data['center_longitude']-0.5 <= lon) &
        (outage_data['center_latitude']+0.5 >= lat) &
        (outage_data['center_longitude']+0.5 >= lon)
    ]
    
    if not cell_tower_matches.empty:
        cell_tower = cell_tower_matches.iloc[0]
        st.session_state.selected_tower = cell_tower
        st.session_state.selected_outage = None
    
    elif not outage_matches.empty:
        outage = outage_matches.iloc[0]
        st.session_state.selected_outage = outage
        st.session_state.selected_tower = None

with st.sidebar:
    if st.session_state.selected_tower is not None:
        cell_tower = st.session_state.selected_tower
        st.markdown(f"### Cell Tower {cell_tower['tower_id']}")
        with st.expander('Details', expanded=True):
            st.write(f"**Status:** {cell_tower['status']}")
            st.write(f"**Signal Strength:** {float(cell_tower['signal_strength']):.3f} dBm")
            st.write(f"**Bandwidth:** {cell_tower['bandwidth']} MHz")
            st.write(f"**Technology:** {cell_tower['technology']}")
            st.write(f"**Coverage:** {float(cell_tower['coverage_radius'])} mi")
            st.write(f"**Lon:** {float(cell_tower['longitude']):.4f}")
            st.write(f"**Lat:** {float(cell_tower['latitude']):.4f}")
        
        if st.button("Generate Deployment Notes", key="show_notes_btn"):
            st.session_state.show_notes = True
            st.session_state.messages = []
            st.rerun()

    elif st.session_state.selected_outage is not None:
        outage = st.session_state.selected_outage
        st.markdown(f"### {outage['outage_id']}")
        with st.expander('Details', expanded=True):
            st.write(f"**Event:** {outage['event']}")
            st.write(f"**Severity:** {outage['severity']}")
            st.write(f"**Number of Total Towers:** {outage['towers_total']}")
            st.write(f"**Number of Affected Towers:** {outage['towers_affected']}")
            st.write(f"**Lon:** {float(outage['center_longitude']):.4f}")
            st.write(f"**Lat:** {float(outage['center_latitude']):.4f}")
            st.write(f"**Radius:** {float(outage['radius']):.2f} km")

# Function to render chat interface
def render_chat_interface(notes):
    with st.container():
        st.markdown("### Deployment Notes")
        st.write(notes)
        st.markdown("### Chat")
        
        # Display existing chat history
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
        
        # Handle new user input - place input box at the end
        user_input = st.chat_input("Ask me anything")
        if user_input:
            # Add user message to session state
            st.session_state.messages.append({"role": "user", "content": user_input})
            
            # Generate response
            assistant_response = get_assistant_response(user_input, st.session_state.selected_tower)
            
            # Add assistant response to session state
            st.session_state.messages.append({"role": "assistant", "content": assistant_response})
            
            # Rerun to display the new messages
            st.rerun()

# Render appropriate chat interface based on current state
if st.session_state.get('show_notes', False) and st.session_state.selected_tower is not None:
    notes = get_deployment_notes(st.session_state.selected_tower)
    render_chat_interface(notes)



