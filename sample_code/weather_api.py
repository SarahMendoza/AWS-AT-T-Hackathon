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
import json
from typing import Dict, List, Optional, Tuple
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class WeatherService:
    """Service class for handling weather data from National Weather Service API"""
    
    def __init__(self, user_agent: str = "FirstNetDashboard (admin@firstnet.gov)"):
        self.user_agent = user_agent
        self.base_url = "https://api.weather.gov"
        self.headers = {
            "User-Agent": self.user_agent,
            "Accept": "application/geo+json"
        }
    
    def get_grid_point(self, latitude: float, longitude: float) -> Optional[Dict]:
        """Get grid point data for coordinates"""
        try:
            url = f"{self.base_url}/points/{latitude},{longitude}"
            response = requests.get(url, headers=self.headers, timeout=10)
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Grid point request failed: {response.status_code}")
                return None
        except Exception as e:
            logger.error(f"Error getting grid point: {e}")
            return None
    
    def get_forecast(self, grid_id: str, grid_x: int, grid_y: int) -> Optional[Dict]:
        """Get forecast for grid coordinates"""
        try:
            url = f"{self.base_url}/gridpoints/{grid_id}/{grid_x},{grid_y}/forecast"
            response = requests.get(url, headers=self.headers, timeout=10)
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Forecast request failed: {response.status_code}")
                return None
        except Exception as e:
            logger.error(f"Error getting forecast: {e}")
            return None
    
    def get_hourly_forecast(self, grid_id: str, grid_x: int, grid_y: int) -> Optional[Dict]:
        """Get hourly forecast for grid coordinates"""
        try:
            url = f"{self.base_url}/gridpoints/{grid_id}/{grid_x},{grid_y}/forecast/hourly"
            response = requests.get(url, headers=self.headers, timeout=10)
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Hourly forecast request failed: {response.status_code}")
                return None
        except Exception as e:
            logger.error(f"Error getting hourly forecast: {e}")
            return None
    
    @st.cache_data(ttl=1800)  # Cache for 30 minutes
    def get_weather_data(_self, latitude: float = 37.7749, longitude: float = -122.4194) -> Dict:
        """Get comprehensive weather data for given coordinates"""
        # Get grid point information
        grid_data = _self.get_grid_point(latitude, longitude)
        if not grid_data:
            return _self._get_fallback_weather()
        
        try:
            properties = grid_data['properties']
            grid_id = properties['gridId']
            grid_x = properties['gridX']
            grid_y = properties['gridY']
            
            # Get current forecast
            forecast_data = _self.get_forecast(grid_id, grid_x, grid_y)
            if not forecast_data:
                return _self._get_fallback_weather()
            
            current_period = forecast_data['properties']['periods'][0]
            
            # Get hourly forecast for more detailed data
            hourly_data = _self.get_hourly_forecast(grid_id, grid_x, grid_y)
            current_hour = hourly_data['properties']['periods'][0] if hourly_data else {}
            
            return {
                'temperature': current_period.get('temperature', 'N/A'),
                'temperature_unit': current_period.get('temperatureUnit', 'F'),
                'humidity': current_hour.get('relativeHumidity', {}).get('value', 'N/A'),
                'wind_speed': current_period.get('windSpeed', 'N/A'),
                'wind_direction': current_period.get('windDirection', 'N/A'),
                'weather_condition': current_period.get('shortForecast', 'N/A'),
                'detailed_forecast': current_period.get('detailedForecast', 'N/A'),
                'precipitation_probability': current_hour.get('probabilityOfPrecipitation', {}).get('value', 0),
                'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'location': f"{properties.get('relativeLocation', {}).get('properties', {}).get('city', 'Unknown')}, "
                           f"{properties.get('relativeLocation', {}).get('properties', {}).get('state', 'Unknown')}"
            }
            
        except KeyError as e:
            logger.error(f"Error parsing weather data: {e}")
            return _self._get_fallback_weather()
    
    def _get_fallback_weather(self) -> Dict:
        """Return fallback weather data when API fails"""
        return {
            'temperature': 'N/A',
            'temperature_unit': 'F',
            'humidity': 'N/A',
            'wind_speed': 'N/A',
            'wind_direction': 'N/A',
            'weather_condition': 'Data Unavailable',
            'detailed_forecast': 'Weather data temporarily unavailable',
            'precipitation_probability': 0,
            'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'location': 'Unknown'
        }
    
    def format_temperature(self, temp_value, temp_unit) -> str:
        """Format temperature for display"""
        if temp_value == 'N/A':
            return 'N/A'
        
        if temp_unit == 'F':
            # Convert to Celsius for display
            celsius = (temp_value - 32) * 5/9
            return f"{temp_value}°F ({celsius:.1f}°C)"
        else:
            return f"{temp_value}°{temp_unit}"
    
    def get_weather_alerts(self, weather_data: Dict) -> List[str]:
        """Generate weather-related alerts for network operations"""
        alerts = []
        
        if weather_data['temperature'] != 'N/A':
            temp = weather_data['temperature']
            if isinstance(temp, (int, float)):
                if weather_data['temperature_unit'] == 'F':
                    if temp > 95:
                        alerts.append("🌡️ High temperature alert: Potential equipment overheating risk")
                    elif temp < 32:
                        alerts.append("❄️ Freezing temperature alert: Monitor for ice formation on equipment")
                else:  # Celsius
                    if temp > 35:
                        alerts.append("🌡️ High temperature alert: Potential equipment overheating risk")
                    elif temp < 0:
                        alerts.append("❄️ Freezing temperature alert: Monitor for ice formation on equipment")
        
        if weather_data['precipitation_probability'] > 70:
            alerts.append("🌧️ High precipitation probability: Potential signal degradation")
        
        if weather_data['wind_speed'] != 'N/A':
            # Extract numeric value from wind speed string
            try:
                if isinstance(weather_data['wind_speed'], str):
                    wind_speed = float(weather_data['wind_speed'].split()[0])
                else:
                    wind_speed = float(weather_data['wind_speed'])
                
                if wind_speed > 40:  # mph
                    alerts.append("💨 High wind alert: Monitor tower stability and equipment")
            except (ValueError, AttributeError):
                pass
        
        return alerts