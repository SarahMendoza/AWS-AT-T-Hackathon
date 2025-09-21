import requests
import math
from typing import List, Tuple, Dict, Any

def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculate the great circle distance between two points on Earth in kilometers.
    Uses the Haversine formula: https://en.wikipedia.org/wiki/Haversine_formula
    """
    R = 6371  # Earth's radius in kilometers
    
    lat1_rad = math.radians(lat1)
    lon1_rad = math.radians(lon1)
    lat2_rad = math.radians(lat2)
    lon2_rad = math.radians(lon2)
    
    dlat = lat2_rad - lat1_rad
    dlon = lon2_rad - lon1_rad
    
    a = math.sin(dlat/2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    
    return R * c

def n_towers_within_zone(lat, lon, radius, towers):
    # calculate the number of towers within the zone
    n_towers = 0
    n_down_towers = 0
    
    # calculate the distance from the center of each tower to the center of the zone
    for tower in towers:
        distance = haversine_distance(lat, lon, float(tower['latitude']), float(tower['longitude']))
        if distance <= radius:
            n_towers += 1
            if tower['status'] == 'Down':
                n_down_towers += 1
    
    return n_towers, n_down_towers

# def polygon_to_circle(coordinates: List[List[List[float]]]) -> Dict[str, float]:
#     """
#     Convert a polygon to a circle by finding the centroid and maximum distance to any vertex.
    
#     Args:
#         coordinates: GeoJSON polygon coordinates (array of rings, each ring is array of [lon, lat] points)
    
#     Returns:
#         Dict with 'lat', 'lon' (center), and 'radius_km' (radius in kilometers)
#     """
#     if not coordinates or not coordinates[0]:
#         raise ValueError("Invalid coordinates")
    
#     # Get the outer ring (first ring in the coordinates)
#     outer_ring = coordinates[0]
    
#     # Calculate centroid
#     total_lat = sum(point[1] for point in outer_ring)  # lat is index 1
#     total_lon = sum(point[0] for point in outer_ring)  # lon is index 0
#     num_points = len(outer_ring)
    
#     center_lat = total_lat / num_points
#     center_lon = total_lon / num_points
    
#     # Find maximum distance from center to any vertex
#     max_distance = 0
#     for point in outer_ring:
#         distance = haversine_distance(center_lat, center_lon, point[1], point[0])
#         max_distance = max(max_distance, distance)
    
#     return {
#         'lat': center_lat,
#         'lon': center_lon,
#         'radius_km': max_distance
#     }

# def fetch_zone_geometry(zone_url: str, headers: Dict[str, str]) -> Dict[str, float]:
#     """
#     Fetch zone geometry from NWS API and convert to circle.
    
#     Args:
#         zone_url: URL to the zone endpoint
#         headers: HTTP headers for the request
    
#     Returns:
#         Dict with 'lat', 'lon', and 'radius_km'
#     """
#     try:
#         response = requests.get(zone_url, headers=headers)
#         response.raise_for_status()
#         zone_data = response.json()
        
#         geometry = zone_data.get('geometry', {})
#         coordinates = geometry.get('coordinates', [])
        
#         if not coordinates:
#             raise ValueError(f"No coordinates found for zone {zone_url}")
        
#         return polygon_to_circle(coordinates)
    
#     except Exception as e:
#         print(f"Error fetching zone {zone_url}: {e}")
#         return None


# def get_alert_areas() -> List[Dict[str, Any]]:
#     HEADERS = {'User-Agent': 'myapp'}
#     endpoint = f'https://api.weather.gov/alerts/active?area=TX'
    
#     try:
#         response = requests.get(endpoint, headers=HEADERS)
#         response.raise_for_status()
#         data = response.json()
#     except Exception as e:
#         print(f"Error fetching alerts: {e}")
#         return []
    
#     urgent_zones = []
    
#     for feature in data.get("features", []):
#         properties = feature.get("properties", {})
        
#         event = properties.get("event")
#         if not event or event.lower() == "test message":
#             continue
        
#         affected_zones = properties.get("affectedZones", [])
        
#         alert_info = {
#             "id": feature.get("id"),
#             "event": event,
#             "reason": properties.get("description", "")[:300],
#             "affected_zones": affected_zones,
#             "severity": properties.get("severity"),
#             "urgency": properties.get("urgency"),
#             "certainty": properties.get("certainty"),
#             "effective": properties.get("effective"),
#             "expires": properties.get("expires"),
#             "zone_circles": []  # Will store the converted circle data
#         }
        
#         # Convert each affected zone to a circle
#         for zone_url in affected_zones:
#             circle_data = fetch_zone_geometry(zone_url, HEADERS)
#             if circle_data:
#                 # Add zone name from URL for reference
#                 zone_id = zone_url.split('/')[-1] if '/' in zone_url else zone_url
#                 circle_data['zone_id'] = zone_id
#                 alert_info["zone_circles"].append(circle_data)
        
#         urgent_zones.append(alert_info)
    
#     return urgent_zones


