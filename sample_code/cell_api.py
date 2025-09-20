import pandas as pd
import streamlit as st
import numpy as np
from numpy.random import default_rng as rng
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import logging

logger = logging.getLogger(__name__)

class CellTowerDataService:
    """Service class for handling cell tower data generation and processing"""
    
    def __init__(self):
        self.rng_gen = rng(42)  # Fixed seed for consistency
        
        # Default coordinates (San Francisco Bay Area)
        self.default_lat = 37.7749
        self.default_lon = -122.4194
        self.lat_range = 0.5
        self.lon_range = 0.7
    
    @st.cache_data(ttl=3600)  # Cache for 1 hour
    def generate_cell_tower_data(_self, num_towers: int = 50, 
                               center_lat: float = None, 
                               center_lon: float = None) -> pd.DataFrame:
        """Generate realistic cell tower data with various attributes"""
        
        # Use provided coordinates or defaults
        lat_center = center_lat or _self.default_lat
        lon_center = center_lon or _self.default_lon
        
        data = {
            'tower_id': [f'FN-{1000 + i}' for i in range(num_towers)],
            'latitude': lat_center + _self.rng_gen.uniform(-_self.lat_range, _self.lat_range, num_towers),
            'longitude': lon_center + _self.rng_gen.uniform(-_self.lon_range, _self.lon_range, num_towers),
            'signal_strength': _self.rng_gen.uniform(-120, -60, num_towers),  # dBm
            'bandwidth': _self.rng_gen.choice([20, 40, 80, 100], num_towers),  # MHz
            'technology': _self.rng_gen.choice(['4G LTE', '5G', '5G mmWave'], num_towers, p=[0.4, 0.5, 0.1]),
            'status': _self.rng_gen.choice(['Active', 'Inactive', 'Maintenance'], num_towers, p=[0.8, 0.1, 0.1]),
            'coverage_radius': _self.rng_gen.uniform(0.5, 5.0, num_towers),  # km
            'installation_date': [
                datetime.now() - timedelta(days=int(_self.rng_gen.uniform(30, 1095))) 
                for _ in range(num_towers)
            ],
            'data_usage_gb': _self.rng_gen.uniform(100, 10000, num_towers),
            'connected_devices': _self.rng_gen.poisson(500, num_towers),
            'uptime_percentage': _self.rng_gen.uniform(95, 100, num_towers)
        }
        
        return pd.DataFrame(data)
    
    def calculate_network_metrics(self, df: pd.DataFrame) -> Dict:
        """Calculate key network performance metrics"""
        if df.empty:
            return self._get_empty_metrics()
        
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
            'network_availability': (len(active_towers) / len(df) * 100) if len(df) > 0 else 0,
            'avg_bandwidth': active_towers['bandwidth'].mean() if len(active_towers) > 0 else 0,
            'newest_tower': df['installation_date'].max() if len(df) > 0 else None,
            'oldest_tower': df['installation_date'].min() if len(df) > 0 else None
        }
        
        return metrics
    
    def _get_empty_metrics(self) -> Dict:
        """Return empty metrics when no data is available"""
        return {
            'total_towers': 0,
            'active_towers': 0,
            'inactive_towers': 0,
            'maintenance_towers': 0,
            'avg_signal_strength': 0,
            'total_coverage_area': 0,
            'avg_uptime': 0,
            'total_data_usage': 0,
            'total_connected_devices': 0,
            'network_availability': 0,
            'avg_bandwidth': 0,
            'newest_tower': None,
            'oldest_tower': None
        }
    
    def apply_filters(self, df: pd.DataFrame, 
                     technology: str = 'All',
                     status: str = 'All',
                     signal_range: Tuple[float, float] = None) -> pd.DataFrame:
        """Apply filters to the dataframe"""
        filtered_df = df.copy()
        
        if technology != 'All':
            filtered_df = filtered_df[filtered_df['technology'] == technology]
        
        if status != 'All':
            filtered_df = filtered_df[filtered_df['status'] == status]
        
        if signal_range:
            min_signal, max_signal = signal_range
            filtered_df = filtered_df[
                (filtered_df['signal_strength'] >= min_signal) & 
                (filtered_df['signal_strength'] <= max_signal)
            ]
        
        return filtered_df
    
    def get_system_alerts(self, df: pd.DataFrame) -> List[str]:
        """Generate system alerts based on tower data"""
        alerts = []
        
        if df.empty:
            alerts.append("⚠️ No tower data available")
            return alerts
        
        # Check for low signal towers
        low_signal_towers = df[df['signal_strength'] < -100]
        if not low_signal_towers.empty:
            alerts.append(f"⚠️ {len(low_signal_towers)} towers have signal strength below -100 dBm")
        
        # Check for low uptime
        low_uptime_towers = df[df['uptime_percentage'] < 98]
        if not low_uptime_towers.empty:
            alerts.append(f"⚠️ {len(low_uptime_towers)} towers have uptime below 98%")
        
        # Check maintenance towers
        maintenance_towers = df[df['status'] == 'Maintenance']
        if not maintenance_towers.empty:
            alerts.append(f"🔧 {len(maintenance_towers)} towers are currently under maintenance")
        
        # Check inactive towers
        inactive_towers = df[df['status'] == 'Inactive']
        if not inactive_towers.empty:
            alerts.append(f"🔴 {len(inactive_towers)} towers are currently inactive")
        
        # Check for high data usage towers
        high_usage_towers = df[df['data_usage_gb'] > 8000]
        if not high_usage_towers.empty:
            alerts.append(f"📊 {len(high_usage_towers)} towers have high data usage (>8TB)")
        
        return alerts
    
    def format_dataframe_for_display(self, df: pd.DataFrame) -> pd.DataFrame:
        """Format dataframe for better display in Streamlit"""
        if df.empty:
            return df
        
        display_df = df.copy()
        display_df['installation_date'] = display_df['installation_date'].dt.strftime('%Y-%m-%d')
        display_df['signal_strength'] = display_df['signal_strength'].round(2)
        display_df['coverage_radius'] = display_df['coverage_radius'].round(2)
        display_df['data_usage_gb'] = display_df['data_usage_gb'].round(2)
        display_df['uptime_percentage'] = display_df['uptime_percentage'].round(2)
        
        return display_df
    
    def get_display_columns(self) -> List[str]:
        """Get the columns to display in the data table"""
        return [
            'tower_id', 'technology', 'status', 'signal_strength', 
            'bandwidth', 'connected_devices', 'uptime_percentage', 'installation_date'
        ]