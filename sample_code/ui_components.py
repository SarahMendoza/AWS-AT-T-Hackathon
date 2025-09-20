import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from typing import Dict, List
from datetime import datetime

class UIComponents:
    """Class containing reusable UI components and styling"""
    
    @staticmethod
    def apply_custom_css():
        """Apply custom CSS styling to the Streamlit app"""
        st.markdown("""
        <style>
            .main-header {
                font-size: 2.5rem;
                color: #1f77b4;
                text-align: center;
                margin-bottom: 2rem;
                font-weight: bold;
                text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
            }
            .section-header {
                font-size: 1.5rem;
                color: #2c3e50;
                margin: 1.5rem 0 1rem 0;
                border-bottom: 3px solid #1f77b4;
                padding-bottom: 0.5rem;
                font-weight: 600;
            }
            .metric-container {
                background: linear-gradient(135deg, #f8f9fa, #e9ecef);
                padding: 1.2rem;
                border-radius: 0.75rem;
                margin: 0.5rem 0;
                border-left: 5px solid #1f77b4;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }
            .weather-container {
                background: linear-gradient(135deg, #74b9ff, #0984e3);
                color: white;
                padding: 1.2rem;
                border-radius: 0.75rem;
                margin: 0.75rem 0;
                box-shadow: 0 4px 8px rgba(0,0,0,0.15);
            }
            .weather-metric {
                background: rgba(255, 255, 255, 0.15);
                padding: 0.5rem;
                border-radius: 0.5rem;
                margin: 0.25rem 0;
                text-align: center;
                backdrop-filter: blur(10px);
            }
            .status-active { 
                color: #28a745; 
                font-weight: bold;
                font-size: 1.1em;
            }
            .status-inactive { 
                color: #dc3545; 
                font-weight: bold;
                font-size: 1.1em;
            }
            .status-maintenance { 
                color: #ffc107; 
                font-weight: bold;
                font-size: 1.1em;
            }
            .alert-success {
                background: linear-gradient(135deg, #d4edda, #c3e6cb);
                border: 1px solid #c3e6cb;
                color: #155724;
                padding: 1rem;
                border-radius: 0.5rem;
                margin: 0.5rem 0;
                border-left: 4px solid #28a745;
            }
            .alert-warning {
                background: linear-gradient(135deg, #fff3cd, #ffeaa7);
                border: 1px solid #ffeaa7;
                color: #856404;
                padding: 1rem;
                border-radius: 0.5rem;
                margin: 0.5rem 0;
                border-left: 4px solid #ffc107;
            }
            .alert-danger {
                background: linear-gradient(135deg, #f8d7da, #f5c6cb);
                border: 1px solid #f5c6cb;
                color: #721c24;
                padding: 1rem;
                border-radius: 0.5rem;
                margin: 0.5rem 0;
                border-left: 4px solid #dc3545;
            }
            .sidebar-section {
                background: rgba(255, 255, 255, 0.05);
                padding: 1rem;
                border-radius: 0.5rem;
                margin: 1rem 0;
            }
            .map-legend {
                display: flex;
                justify-content: space-around;
                background: #f8f9fa;
                padding: 0.5rem;
                border-radius: 0.5rem;
                margin: 0.5rem 0;
            }
            .legend-item {
                display: flex;
                align-items: center;
                gap: 0.25rem;
            }
            .footer-stats {
                background: linear-gradient(135deg, #f8f9fa, #e9ecef);
                padding: 1rem;
                border-radius: 0.5rem;
                text-align: center;
                margin-top: 2rem;
                border-top: 3px solid #1f77b4;
            }
        </style>
        """, unsafe_allow_html=True)
    
    @staticmethod
    def render_main_header():
        """Render the main dashboard header"""
        st.markdown("""
        <div class="main-header">
            📡 FirstNet Cell Tower Deployment Dashboard
        </div>
        """, unsafe_allow_html=True)
    
    @staticmethod
    def render_weather_sidebar(weather_data: Dict, weather_service):
        """Render weather information in the sidebar"""
        st.markdown("### 🌤️ Current Weather")
        
        # Location info
        if weather_data.get('location', 'Unknown') != 'Unknown':
            st.info(f"📍 **Location:** {weather_data['location']}")
        
        # Weather container
        st.markdown('<div class="weather-container">', unsafe_allow_html=True)
        
        # Temperature display
        temp_display = weather_service.format_temperature(
            weather_data.get('temperature', 'N/A'),
            weather_data.get('temperature_unit', 'F')
        )
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"""
            <div class="weather-metric">
                <strong>🌡️ Temperature</strong><br>
                {temp_display}
            </div>
            """, unsafe_allow_html=True)
            
            humidity_val = weather_data.get('humidity', 'N/A')
            humidity_display = f"{humidity_val}%" if humidity_val != 'N/A' else "N/A"
            st.markdown(f"""
            <div class="weather-metric">
                <strong>💧 Humidity</strong><br>
                {humidity_display}
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            wind_speed = weather_data.get('wind_speed', 'N/A')
            st.markdown(f"""
            <div class="weather-metric">
                <strong>💨 Wind Speed</strong><br>
                {wind_speed}
            </div>
            """, unsafe_allow_html=True)
            
            precip_prob = weather_data.get('precipitation_probability', 0)
            precip_display = f"{precip_prob}%" if precip_prob > 0 else "0%"
            st.markdown(f"""
            <div class="weather-metric">
                <strong>🌧️ Rain Chance</strong><br>
                {precip_display}
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Weather condition
        condition = weather_data.get('weather_condition', 'N/A')
        st.markdown(f"**Current Condition:** {condition}")
        
        # Detailed forecast
        detailed = weather_data.get('detailed_forecast', '')
        if detailed and detailed != 'N/A' and len(detailed) > 20:
            with st.expander("📋 Detailed Forecast"):
                st.write(detailed)
        
        st.caption(f"⏱️ Last updated: {weather_data.get('last_updated', 'Unknown')}")
    
    @staticmethod
    def render_filters(df: pd.DataFrame):
        """Render filter controls and return filter values"""
        st.markdown("### 🔍 Filters")
        
        if df.empty:
            st.warning("No data available for filtering")
            return {
                'technology': 'All',
                'status': 'All',
                'signal_range': (-120, -60),
                'auto_refresh': False
            }
        
        # Technology filter
        tech_options = ['All'] + sorted(list(df['technology'].unique()))
        selected_tech = st.selectbox("📡 Technology", tech_options)
        
        # Status filter
        status_options = ['All'] + sorted(list(df['status'].unique()))
        selected_status = st.selectbox("🔄 Status", status_options)
        
        # Signal strength filter
        min_signal_val = float(df['signal_strength'].min())
        max_signal_val = float(df['signal_strength'].max())
        signal_range = st.slider(
            "📶 Signal Strength Range (dBm)",
            min_signal_val,
            max_signal_val,
            (min_signal_val, max_signal_val),
            step=1.0
        )
        
        # Additional filters
        st.markdown("**Advanced Filters**")
        
        # Uptime filter
        uptime_threshold = st.slider("⏱️ Minimum Uptime %", 90.0, 100.0, 95.0, 0.1)
        
        # Auto-refresh toggle
        auto_refresh = st.checkbox("🔄 Auto-refresh (30s)", value=False)
        
        return {
            'technology': selected_tech,
            'status': selected_status,
            'signal_range': signal_range,
            'uptime_threshold': uptime_threshold,
            'auto_refresh': auto_refresh
        }
    
    @staticmethod
    def render_key_metrics(metrics: Dict, filtered_count: int):
        """Render key performance metrics"""
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            delta_text = None
            if filtered_count != metrics['total_towers']:
                delta_text = f"{filtered_count} filtered"
            
            st.metric(
                "🏗️ Total Towers", 
                f"{metrics['total_towers']:,}",
                delta=delta_text
            )
        
        with col2:
            availability = metrics['network_availability']
            if availability > 95:
                delta_icon = "🟢 Excellent"
                delta_color = "normal"
            elif availability > 90:
                delta_icon = "🟡 Good"
                delta_color = "normal"
            else:
                delta_icon = "🔴 Critical"
                delta_color = "inverse"
            
            st.metric(
                "📊 Network Availability", 
                f"{availability:.1f}%",
                delta=delta_icon
            )
        
        with col3:
            avg_signal = metrics['avg_signal_strength']
            signal_display = f"{avg_signal:.1f} dBm" if avg_signal > 0 else "N/A"
            
            # Signal quality indicator
            if avg_signal > -70:
                signal_quality = "🟢 Strong"
            elif avg_signal > -85:
                signal_quality = "🟡 Fair"
            else:
                signal_quality = "🔴 Weak"
            
            st.metric(
                "📶 Avg Signal Strength", 
                signal_display,
                delta=signal_quality if avg_signal > 0 else None
            )
        
        with col4:
            coverage = metrics['total_coverage_area']
            coverage_display = f"{coverage:.1f} km²" if coverage > 0 else "N/A"
            
            st.metric(
                "🗺️ Total Coverage", 
                coverage_display
            )
        
        with col5:
            devices = int(metrics['total_connected_devices'])
            
            st.metric(
                "📱 Connected Devices", 
                f"{devices:,}"
            )
    
    @staticmethod
    def render_tower_map(df: pd.DataFrame):
        """Render the cell tower map"""
        st.markdown('<div class="section-header">🗺️ Cell Tower Map</div>', unsafe_allow_html=True)
        
        if df.empty:
            st.warning("No towers match the current filters.")
            return
        
        # Create color mapping for status
        color_map = {'Active': '#28a745', 'Inactive': '#dc3545', 'Maintenance': '#ffc107'}
        df_copy = df.copy()
        df_copy['color'] = df_copy['status'].map(color_map)
        
        # Streamlit map
        st.map(
            df_copy, 
            latitude="latitude", 
            longitude="longitude", 
            size="coverage_radius",
            color="color"
        )
        
        # Map legend and statistics
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.markdown("""
            <div class="map-legend">
                <div class="legend-item">
                    <span style="color: #28a745; font-size: 1.2em;">●</span>
                    <span>Active</span>
                </div>
                <div class="legend-item">
                    <span style="color: #ffc107; font-size: 1.2em;">●</span>
                    <span>Maintenance</span>
                </div>
                <div class="legend-item">
                    <span style="color: #dc3545; font-size: 1.2em;">●</span>
                    <span>Inactive</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.info(f"📊 Showing **{len(df):,}** towers")
    
    @staticmethod
    def create_technology_pie_chart(df: pd.DataFrame):
        """Create technology distribution pie chart"""
        if df.empty:
            return None
        
        tech_counts = df['technology'].value_counts()
        
        fig_pie = px.pie(
            values=tech_counts.values, 
            names=tech_counts.index,
            title="🔧 Tower Technology Distribution",
            color_discrete_sequence=px.colors.qualitative.Set3
        )
        fig_pie.update_traces(
            textposition='inside', 
            textinfo='percent+label',
            hovertemplate='<b>%{label}</b><br>Count: %{value}<br>Percentage: %{percent}<extra></extra>'
        )
        fig_pie.update_layout(height=400, showlegend=True, font=dict(size=12))
        return fig_pie
    
    @staticmethod
    def create_status_bar_chart(df: pd.DataFrame):
        """Create status distribution bar chart"""
        if df.empty:
            return None
        
        status_counts = df['status'].value_counts()
        colors = {'Active': '#28a745', 'Inactive': '#dc3545', 'Maintenance': '#ffc107'}
        
        fig_bar = px.bar(
            x=status_counts.index, 
            y=status_counts.values,
            color=status_counts.index,
            color_discrete_map=colors,
            title="📊 Tower Status Distribution"
        )
        fig_bar.update_traces(
            texttemplate='%{y}', 
            textposition='outside',
            hovertemplate='<b>%{x}</b><br>Count: %{y}<extra></extra>'
        )
        fig_bar.update_layout(height=400, showlegend=False, font=dict(size=12))
        return fig_bar
    
    @staticmethod
    def create_signal_histogram(df: pd.DataFrame):
        """Create signal strength distribution histogram"""
        if df.empty:
            return None
        
        fig_hist = px.histogram(
            df, 
            x='signal_strength', 
            nbins=25,
            title="📶 Signal Strength Distribution",
            labels={'signal_strength': 'Signal Strength (dBm)', 'count': 'Number of Towers'},
            color_discrete_sequence=['#1f77b4']
        )
        fig_hist.update_traces(
            hovertemplate='<b>Signal Range</b>: %{x} dBm<br><b>Tower Count</b>: %{y}<extra></extra>'
        )
        fig_hist.update_layout(height=400, font=dict(size=12))
        return fig_hist
    
    @staticmethod
    def create_usage_scatter(df: pd.DataFrame):
        """Create data usage vs connected devices scatter plot"""
        if df.empty:
            return None
        
        fig_scatter = px.scatter(
            df,
            x='connected_devices',
            y='data_usage_gb',
            color='technology',
            size='coverage_radius',
            title="📊 Data Usage vs Connected Devices",
            labels={
                'connected_devices': 'Connected Devices', 
                'data_usage_gb': 'Data Usage (GB)',
                'coverage_radius': 'Coverage Radius (km)'
            }
        )
        fig_scatter.update_traces(
            hovertemplate='<b>%{customdata[0]}</b><br>' +
                         'Devices: %{x:,}<br>' +
                         'Data Usage: %{y:.1f} GB<br>' +
                         'Coverage: %{marker.size:.1f} km<extra></extra>'
        )
        fig_scatter.update_layout(height=400, font=dict(size=12))
        return fig_scatter
    
    @staticmethod
    def create_uptime_box_plot(df: pd.DataFrame):
        """Create uptime by status box plot"""
        if df.empty:
            return None
        
        fig_box = px.box(
            df,
            x='status',
            y='uptime_percentage',
            color='status',
            title="⏱️ Uptime Distribution by Status",
            labels={'uptime_percentage': 'Uptime %', 'status': 'Tower Status'}
        )
        fig_box.update_traces(
            hovertemplate='<b>%{x}</b><br>' +
                         'Uptime: %{y:.2f}%<extra></extra>'
        )
        fig_box.update_layout(height=400, showlegend=False, font=dict(size=12))
        return fig_box
    
    @staticmethod
    def render_alerts(alerts: List[str], weather_alerts: List[str] = None):
        """Render system and weather alerts"""
        st.markdown('<div class="section-header">🚨 System Alerts</div>', unsafe_allow_html=True)
        
        # Combine all alerts
        all_alerts = alerts.copy() if alerts else []
        if weather_alerts:
            all_alerts.extend(weather_alerts)
        
        if all_alerts:
            # Categorize alerts by severity
            critical_alerts = []
            warning_alerts = []
            info_alerts = []
            
            for alert in all_alerts:
                if any(word in alert.lower() for word in ['inactive', 'critical', 'failed']):
                    critical_alerts.append(alert)
                elif any(word in alert.lower() for word in ['maintenance', 'high', 'low', 'freezing']):
                    warning_alerts.append(alert)
                else:
                    info_alerts.append(alert)
            
            # Render alerts by category
            for alert in critical_alerts:
                st.markdown(f'<div class="alert-danger">{alert}</div>', unsafe_allow_html=True)
            
            for alert in warning_alerts:
                st.markdown(f'<div class="alert-warning">{alert}</div>', unsafe_allow_html=True)
            
            for alert in info_alerts:
                st.info(alert)
            
            # Summary
            if len(all_alerts) > 3:
                st.caption(f"📋 Total alerts: {len(all_alerts)}")
        else:
            st.markdown('<div class="alert-success">✅ All systems operating normally</div>', 
                       unsafe_allow_html=True)
    
    @staticmethod
    def render_data_table(df: pd.DataFrame, columns_to_show: List[str]):
        """Render detailed data table"""
        st.markdown('<div class="section-header">📋 Detailed Tower Information</div>', 
                   unsafe_allow_html=True)
        
        if st.checkbox("Show detailed tower data"):
            if df.empty:
                st.info("No data available for the current filters.")
            else:
                # Add search functionality
                search_term = st.text_input("🔍 Search towers (by ID, technology, or status):", 
                                          placeholder="e.g., FN-1001, 5G, Active")
                
                filtered_df = df.copy()
                if search_term:
                    mask = (
                        filtered_df['tower_id'].str.contains(search_term, case=False, na=False) |
                        filtered_df['technology'].str.contains(search_term, case=False, na=False) |
                        filtered_df['status'].str.contains(search_term, case=False, na=False)
                    )
                    filtered_df = filtered_df[mask]
                
                # Display data
                st.dataframe(
                    filtered_df[columns_to_show],
                    use_container_width=True,
                    hide_index=True,
                    column_config={
                        'tower_id': st.column_config.TextColumn('Tower ID', width='small'),
                        'technology': st.column_config.TextColumn('Technology', width='small'),
                        'status': st.column_config.TextColumn('Status', width='small'),
                        'signal_strength': st.column_config.NumberColumn('Signal (dBm)', format='%.1f'),
                        'uptime_percentage': st.column_config.ProgressColumn('Uptime %', min_value=0, max_value=100),
                    }
                )
                
                # Export functionality
                col1, col2, col3 = st.columns([1, 1, 2])
                with col1:
                    csv = filtered_df.to_csv(index=False)
                    st.download_button(
                        label="📥 Download CSV",
                        data=csv,
                        file_name=f"firstnet_towers_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                        mime="text/csv"
                    )
                
                with col2:
                    st.metric("📊 Filtered Rows", len(filtered_df))
                
                with col3:
                    if search_term and len(filtered_df) == 0:
                        st.warning("No towers match your search criteria.")
    
    @staticmethod
    def render_footer(filtered_count: int):
        """Render dashboard footer"""
        st.markdown("---")
        st.markdown(f"""
        <div class="footer-stats">
            <strong>⏱️ Last updated:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | 
            <strong>📊 Data points:</strong> {filtered_count:,} towers | 
            <strong>🏢 FirstNet Deployment Dashboard</strong> v2.0
        </div>
        """, unsafe_allow_html=True)
    
    @staticmethod
    def render_sidebar_stats(df: pd.DataFrame):
        """Render additional statistics in sidebar"""
        if df.empty:
            return
        
        st.markdown("### 📈 Quick Stats")
        
        # Technology breakdown
        tech_stats = df['technology'].value_counts()
        for tech, count in tech_stats.items():
            percentage = (count / len(df)) * 100
            st.markdown(f"**{tech}:** {count} ({percentage:.1f}%)")
        
        st.markdown("---")
        
        # Performance indicators
        avg_uptime = df['uptime_percentage'].mean()
        avg_devices = df['connected_devices'].mean()
        
        st.metric("📊 Avg Uptime", f"{avg_uptime:.1f}%")
        st.metric("📱 Avg Devices", f"{avg_devices:.0f}")
        
        # Show newest and oldest towers
        if not df.empty and 'installation_date' in df.columns:
            newest = df['installation_date'].max().strftime('%Y-%m-%d')
            oldest = df['installation_date'].min().strftime('%Y-%m-%d')
            
            st.markdown(f"**🆕 Newest:** {newest}")
            st.markdown(f"**📅 Oldest:** {oldest}")