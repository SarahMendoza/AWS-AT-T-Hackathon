from datetime import datetime, timedelta
import numpy as np
from numpy.random import default_rng as rng


def generate_cell_tower_data(num_towers=500, lat_min=25.5, lon_min=-106.5, lat_max=35.5, lon_max=-93.5):
    """Generate realistic cell tower data with various attributes"""
    rng_gen = rng(42)  # Fixed seed for consistency
    
    data = {
        'tower_id': [f'FN-{1000 + i}' for i in range(num_towers)],
        'latitude': rng_gen.uniform(lat_min, lat_max, num_towers),
        'longitude': rng_gen.uniform(lon_min, lon_max, num_towers),
        'signal_strength': rng_gen.uniform(-120, -60, num_towers),  # dBm
        'bandwidth': rng_gen.choice([20, 40, 80, 100], num_towers),  # MHz
        'technology': rng_gen.choice(['4G LTE', '5G', '5G mmWave'], num_towers, p=[0.4, 0.5, 0.1]).tolist(),
        'status': rng_gen.choice(['Active', 'Down'], num_towers, p=[0.95, 0.05]).tolist(),
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


def generate_predicted_outages(n_areas=15, lat_min=25.5, lon_min=-106.5, lat_max=35.5, lon_max=-93.5):
    rng_gen = rng(42)  # Fixed seed for consistency
    
    data = {
        'center_latitude': rng_gen.uniform(lat_min, lat_max, n_areas),
        'center_longitude': rng_gen.uniform(lon_min, lon_max, n_areas),
        'radius': rng_gen.uniform(5.0, 50.0, n_areas),  # km
        'event': rng_gen.choice(['Flood', 'Wildfire', 'Cyber Attack'], n_areas, p=[0.5, 0.3, 0.2]).tolist(),
        'severity': rng_gen.choice(['Low', 'Medium', 'High', 'Critical'], n_areas, p=[0.5, 0.3, 0.15, 0.05]).tolist(),
    }
    
    # Convert numpy arrays to lists for JSON serialization
    for key, value in data.items():
        if isinstance(value, np.ndarray):
            data[key] = value.tolist()
    
    return data