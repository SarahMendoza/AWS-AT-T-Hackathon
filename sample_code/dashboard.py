import streamlit as st
import time
import logging
from datetime import datetime

# Import our custom modules
from weather_api import WeatherService
from cell_api import CellTowerDataService
from ui_components import UIComponents

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Page configuration
st.set_page_config(
    page_title="FirstNet Deployment Dashboard",
    layout="wide",
    initial_sidebar_state="expanded",
    page_icon="📡"
)

class FirstNetDashboard:
    """Main dashboard class that orchestrates all components"""
    
    def __init__(self):
        self.weather_service = WeatherService()
        self.data_service = CellTowerDataService()
        self.ui = UIComponents()
        
        # Default coordinates (can be made configurable)
        self.default_lat = 37.7749
        self.default_lon = -122.4194
        
        # Initialize session state
        self._init_session_state()
    
    def _init_session_state(self):
        """Initialize session state variables"""
        if 'last_refresh' not in st.session_state:
            st.session_state.last_refresh = datetime.now()
        if 'tower_count' not in st.session_state:
            st.session_state.tower_count = 50
    
    def run(self):
        """Main method to run the dashboard"""
        try:
            # Apply custom styling
            self.ui.apply_custom_css()
            
            # Load data
            weather_data = self._load_weather_data()
            tower_data = self._load_tower_data()
            
            # Render sidebar
            filters = self._render_sidebar(tower_data, weather_data)
            
            # Handle auto-refresh
            if filters['auto_refresh']:
                self._handle_auto_refresh()
            
            # Apply filters to data
            filtered_data = self.data_service.apply_filters(
                tower_data,
                filters['technology'],
                filters['status'],
                filters['signal_range']
            )
            
            # Calculate metrics
            metrics = self.data_service.calculate_network_metrics(filtered_data)
            
            # Render main dashboard
            self._render_main_dashboard(filtered_data, metrics, weather_data)
            
        except Exception as e:
            logger.error(f"Dashboard error: {e}")
            st.error("An error occurred while loading the dashboard. Please refresh the page.")
    
    def _load_weather_data(self):
        """Load weather data with error handling"""
        try:
            return self.weather_service.get_weather_data(self.default_lat, self.default_lon)
        except Exception as e:
            logger.error(f"Weather data error: {e}")
            return self.weather_service._get_fallback_weather()
    
    def _load_tower_data(self):
        """Load tower data with error handling"""
        try:
            return self.data_service.generate_cell_tower_data(
                st.session_state.tower_count,
                self.default_lat,
                self.default_lon
            )
        except Exception as e:
            logger.error(f"Tower data error: {e}")
            st.error("Failed to load tower data")
            return pd.DataFrame()  # Return empty DataFrame
    
    def _render_sidebar(self, tower_data, weather_data):
        """Render sidebar with weather info and filters"""
        with st.sidebar:
            st.markdown('<h1 style="color: #1f77b4;">📡 FirstNet Dashboard</h1>', 
                       unsafe_allow_html=True)
            
            # Weather information
            self.ui.render_weather_sidebar(weather_data, self.weather_service)
            
            st.markdown("---")
            
            # Configuration section
            st.markdown("### ⚙️ Configuration")
            new_tower_count = st.slider("Number of Towers", 10, 100, st.session_state.tower_count, 5)
            if new_tower_count != st.session_state.tower_count:
                st.session_state.tower_count = new_tower_count
                st.cache_data.clear()  # Clear cache to regenerate data
                st.rerun()
            
            st.markdown("---")
            
            # Filters
            if not tower_data.empty:
                filters = self.ui.render_filters(tower_data)
            else:
                filters = {
                    'technology': 'All',
                    'status': 'All', 
                    'signal_range': (-120, -60),
                    'auto_refresh': False
                }
            
            st.markdown("---")
            
            # Manual refresh button
            if st.button("🔄 Refresh Data"):
                st.cache_data.clear()
                st.session_state.last_refresh = datetime.now()
                st.rerun()
            
            return filters
    
    def _handle_auto_refresh(self):
        """Handle auto-refresh functionality"""
        time.sleep(30)
        st.session_state.last_refresh = datetime.now()
        st.rerun()
    
    def _render_main_dashboard(self, filtered_data, metrics, weather_data):
        """Render the main dashboard content"""
        # Header
        self.ui.render_main_header()
        
        # Key metrics
        self.ui.render_key_metrics(metrics, len(filtered_data))
        
        # Main content area
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # Tower map
            self.ui.render_tower_map(filtered_data)
        
        with col2:
            # Technology distribution
            if not filtered_data.empty:
                fig_pie = self.ui.create_technology_pie_chart(filtered_data)
                st.plotly_chart(fig_pie, use_container_width=True)
                
                # Status overview
                fig_bar = self.ui.create_status_bar_chart(filtered_data)
                st.plotly_chart(fig_bar, use_container_width=True)
        
        # Performance analytics
        if not filtered_data.empty:
            st.markdown('<div class="section-header">📊 Performance Analytics</div>', 
                       unsafe_allow_html=True)
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                fig_hist = self.ui.create_signal_histogram(filtered_data)
                st.plotly_chart(fig_hist, use_container_width=True)
            
            with col2:
                fig_scatter = self.ui.create_usage_scatter(filtered_data)
                st.plotly_chart(fig_scatter, use_container_width=True)
            
            with col3:
                fig_box = self.ui.create_uptime_box_plot(filtered_data)
                st.plotly_chart(fig_box, use_container_width=True)
        
        # Detailed data table
        if not filtered_data.empty:
            formatted_data = self.data_service.format_dataframe_for_display(filtered_data)
            columns_to_show = self.data_service.get_display_columns()
            self.ui.render_data_table(formatted_data, columns_to_show)
        
        # Alerts section
        system_alerts = self.data_service.get_system_alerts(filtered_data)
        weather_alerts = self.weather_service.get_weather_alerts(weather_data)
        self.ui.render_alerts(system_alerts, weather_alerts)
        
        # Footer
        self.ui.render_footer(len(filtered_data))

def main():
    """Main function to run the dashboard"""
    dashboard = FirstNetDashboard()
    dashboard.run()

if __name__ == "__main__":
    main()