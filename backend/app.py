from flask import Flask, jsonify, request
from flask_cors import CORS
import pandas as pd
import numpy as np
from numpy.random import default_rng as rng
from datetime import datetime, timedelta
import time

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Function to generate realistic cell tower data
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
        'technology': rng_gen.choice(['4G LTE', '5G', '5G mmWave'], num_towers, p=[0.4, 0.5, 0.1]).tolist(),
        'status': rng_gen.choice(['Active', 'Inactive', 'Maintenance'], num_towers, p=[0.8, 0.1, 0.1]).tolist(),
        'coverage_radius': rng_gen.uniform(0.5, 5.0, num_towers),  # km
        'installation_date': [
            (datetime.now() - timedelta(days=int(rng_gen.uniform(30, 1095)))).isoformat()
            for _ in range(num_towers)
        ],
        'data_usage_gb': rng_gen.uniform(100, 10000, num_towers),
        'connected_devices': rng_gen.poisson(500, num_towers).tolist(),
        'uptime_percentage': rng_gen.uniform(95, 100, num_towers)
    }
    
    # Convert numpy arrays to lists for JSON serialization
    for key, value in data.items():
        if isinstance(value, np.ndarray):
            data[key] = value.tolist()
    
    return data

# Mock weather data cache
weather_cache = {
    'data': None,
    'timestamp': None,
    'ttl': 300  # 5 minutes
}

def get_weather_data():
    """Get current weather data for the region with caching"""
    current_time = time.time()
    
    # Check if cache is valid
    if (weather_cache['data'] is not None and 
        weather_cache['timestamp'] is not None and 
        current_time - weather_cache['timestamp'] < weather_cache['ttl']):
        return weather_cache['data']
    
    # Generate new weather data (replace with real API call)
    rng_gen = rng(int(current_time))  # Use current time as seed for variation
    weather_data = {
        'temperature': float(rng_gen.uniform(15, 30)),
        'humidity': float(rng_gen.uniform(40, 80)),
        'wind_speed': float(rng_gen.uniform(5, 25)),
        'precipitation': float(rng_gen.uniform(0, 5)),
        'visibility': float(rng_gen.uniform(8, 12)),
        'weather_condition': rng_gen.choice(['Clear', 'Cloudy', 'Partly Cloudy', 'Light Rain']),
        'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
    
    # Update cache
    weather_cache['data'] = weather_data
    weather_cache['timestamp'] = current_time
    
    return weather_data

def calculate_network_metrics(towers_data):
    """Calculate key network performance metrics"""
    if not towers_data:
        return {}
    
    df = pd.DataFrame(towers_data)
    active_towers = df[df['status'] == 'Active']
    
    metrics = {
        'total_towers': len(df),
        'active_towers': len(active_towers),
        'inactive_towers': len(df[df['status'] == 'Inactive']),
        'maintenance_towers': len(df[df['status'] == 'Maintenance']),
        'avg_signal_strength': float(active_towers['signal_strength'].mean()) if len(active_towers) > 0 else 0,
        'total_coverage_area': float(active_towers['coverage_radius'].sum() * 3.14159) if len(active_towers) > 0 else 0,
        'avg_uptime': float(active_towers['uptime_percentage'].mean()) if len(active_towers) > 0 else 0,
        'total_data_usage': float(df['data_usage_gb'].sum()),
        'total_connected_devices': int(df['connected_devices'].sum()),
        'network_availability': float(len(active_towers) / len(df) * 100) if len(df) > 0 else 0
    }
    
    return metrics

# API Routes
@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'timestamp': datetime.now().isoformat()})

# TODO: Replace with real weather data api
@app.route('/api/weather', methods=['GET'])
def get_weather():
    """Get current weather data"""
    try:
        weather_data = get_weather_data()
        return jsonify({'success': True, 'data': weather_data})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# TODO: Replace with real cell tower api
@app.route('/api/towers', methods=['GET'])
def get_towers():
    """Get cell tower data with optional filtering"""
    try:
        # Get query parameters for filtering
        technology = request.args.get('technology', 'All')
        status = request.args.get('status', 'All')
        min_signal = request.args.get('min_signal', type=float)
        max_signal = request.args.get('max_signal', type=float)
        num_towers = request.args.get('num_towers', default=50, type=int)
        
        # Generate tower data
        towers_data = generate_cell_tower_data(num_towers)
        df = pd.DataFrame(towers_data)
        
        # Apply filters
        if technology != 'All':
            df = df[df['technology'] == technology]
        if status != 'All':
            df = df[df['status'] == status]
        if min_signal is not None and max_signal is not None:
            df = df[(df['signal_strength'] >= min_signal) & (df['signal_strength'] <= max_signal)]
        
        # Convert back to dict for JSON response
        filtered_data = df.to_dict('records')
        
        return jsonify({
            'success': True, 
            'data': filtered_data,
            'total_count': len(towers_data),
            'filtered_count': len(filtered_data)
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/metrics', methods=['GET'])
def get_metrics():
    """Get network performance metrics"""
    try:
        num_towers = request.args.get('num_towers', default=50, type=int)
        towers_data = generate_cell_tower_data(num_towers)
        metrics = calculate_network_metrics(towers_data)
        
        return jsonify({'success': True, 'data': metrics})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/alerts', methods=['GET'])
def get_alerts():
    """Get system alerts based on current tower data"""
    try:
        num_towers = request.args.get('num_towers', default=50, type=int)
        towers_data = generate_cell_tower_data(num_towers)
        df = pd.DataFrame(towers_data)
        
        alerts = []
        
        # Check for low signal towers
        low_signal_towers = df[df['signal_strength'] < -100]
        if not low_signal_towers.empty:
            alerts.append({
                'type': 'warning',
                'message': f"{len(low_signal_towers)} towers have signal strength below -100 dBm",
                'icon': '⚠️'
            })
        
        # Check for low uptime
        low_uptime_towers = df[df['uptime_percentage'] < 98]
        if not low_uptime_towers.empty:
            alerts.append({
                'type': 'warning',
                'message': f"{len(low_uptime_towers)} towers have uptime below 98%",
                'icon': '⚠️'
            })
        
        # Check maintenance towers
        maintenance_towers = df[df['status'] == 'Maintenance']
        if not maintenance_towers.empty:
            alerts.append({
                'type': 'info',
                'message': f"{len(maintenance_towers)} towers are currently under maintenance",
                'icon': '🔧'
            })
        
        if not alerts:
            alerts.append({
                'type': 'success',
                'message': "All systems operating normally",
                'icon': '✅'
            })
        
        return jsonify({'success': True, 'data': alerts})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/tower-options', methods=['GET'])
def get_tower_options():
    """Get available options for filtering (technologies, statuses, etc.)"""
    try:
        towers_data = generate_cell_tower_data()
        df = pd.DataFrame(towers_data)
        
        options = {
            'technologies': list(df['technology'].unique()),
            'statuses': list(df['status'].unique()),
            'signal_range': {
                'min': float(df['signal_strength'].min()),
                'max': float(df['signal_strength'].max())
            }
        }
        
        return jsonify({'success': True, 'data': options})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)