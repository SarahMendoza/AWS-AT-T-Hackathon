import urllib.request
import json
import time
AREA = "TX"
API_URL = f"https://api.weather.gov/alerts/active/area/{AREA}"

# def parse_event_data(value):
#     # Get the current timestamp
#     timestamp = int(time.time())
#     # Safely extract nested properties
#     event = value["features"]["properties"]["event"]
#     certainty = value["features"]["properties"]["certainty"]
#     severity = value["features"]["properties"]["severity"]
#     urgency = value["features"]["properties"]["urgency"]
#     description = value["features"]["properties"]["description"]
#     headline = value["features"]["properties"]["headline"]
#     onset = value["features"]["properties"]["onset"]
#     response = value["features"]["properties"]["response"]
#     geography = value["features"]["geometry"]["GeoJSON Point"]["coordinates"]
#     return {
#         "timestamp": timestamp,
#         "event": event,
#         "certainty": certainty,
#         "severity": severity,
#         "urgency": urgency,
#         "description": description
#     }

# try:
#     with urllib.request.urlopen(API_URL) as response:
#         data = json.load(response)
#     print(json.dumps(data, indent=2))
#     print("\n\n")
#     print(len(data))
#     print(data)
#     #for it in data:
#     print(data["features"][0]["properties"]["event"])
#     print("\n\n")


#     value = data
#     print ("aaaaaaaaaaaaaaaaaaaaa")
#     event = data["features"][0]["properties"]["event"]
#     certainty = data["features"][0]["properties"]["certainty"]
#     severity = data["features"][0]["properties"]["severity"]
#     urgency = data["features"][0]["properties"]["urgency"]
#     description = data["features"][0]["properties"]["description"]
#     headline = data["features"][0]["properties"]["headline"]
#     print ("aaaaaaaaaaaaaaaaaaaaa")
#     onset = data["features"][0]["properties"]["onset"]
#     response = data["features"][0]["properties"]["response"]
#     print ("aaaaaaaaaaaaaaaaaaaaa")
#     geography = data["features"][0]["geometry"][0]["coordinates"]
#     print ("aaaaaaaaaaaaaaaaaaaaa")
#     # parse_event_data(data)

    # --- New version: Parse all events in the API response ---
def parse_all_events(data):
    results = []
    features = data.get("features", [])
    for feature in features:
        try:
            properties = feature.get("properties", {})
            geometry = feature.get("geometry", {})
            event = properties.get("event", None)
            certainty = properties.get("certainty", None)
            severity = properties.get("severity", None)
            urgency = properties.get("urgency", None)
            description = properties.get("description", None)
            headline = properties.get("headline", None)
            onset = properties.get("onset", None)
            response = properties.get("response", None)
            # Try to get coordinates if available
            coordinates = None
            if isinstance(geometry, dict):
                coordinates = geometry.get("coordinates", None)
            results.append({
                "timestamp": int(time.time()),
                "event": event,
                "certainty": certainty,
                "severity": severity,
                "urgency": urgency,
                "description": description,
                "headline": headline,
                "onset": onset,
                "response": response,
                "coordinates": coordinates
            })
        except Exception as e:
            print(f"Error parsing feature: {e}")
    return results

# Example usage:
try:
    with urllib.request.urlopen(API_URL) as response:
        data = json.load(response)
    all_events = parse_all_events(data)
    print(f"Parsed {len(all_events)} events:")
    for event in all_events:
        print(event)
except Exception as e:
    print(f"Error fetching or parsing alerts: {e}")

# except Exception as e:
#     print(f"Error fetching alerts: {e}")





