import folium
import json

def create_folium_map(tower_data, outage_data):
    m = folium.Map(location=(31.96, -99.9), zoom_start=7, tiles="cartodb positron")
    
    # with open('frontend/assets/tx.geojson', 'r') as f:
    #     tx_geojson = json.load(f)
    
    # folium.GeoJson(
    # tx_geojson,
    # name='Texas',
    # style_function=lambda feature: {
    #     'color': 'black',
    #     'weight': 1,
    #     'fillOpacity': 0.0
    # }).add_to(m)
    
    severity_2_color = {
        'Critical': 'darkred',
        'High': 'red',
        'Medium': 'orange',
        'Low': 'Yellow'
    }

    status_2_color = {
        'Active': 'green',
        'Down': 'red'
    }

    for _, row in tower_data.iterrows():
        if row['status'] != 'Down':
            continue
        
        popup_text = ""
        popup_text += f"<strong>Tower ID:</strong> {row['tower_id']}<br>"
        popup_text += f"<strong>Status:</strong> {row['status']}<br>"
        popup_text += f"<strong>Signal Strength:</strong> {row['signal_strength']:.3f} dBm<br>"
        popup_text += f"<strong>Bandwidth:</strong> {row['bandwidth']} MHz<br>"
        popup_text += f"<strong>Technology:</strong> {row['technology']}<br>"
        popup_text += f"<strong>Lon:</strong> {row['longitude']:.4f}<br>"
        popup_text += f"<strong>Lat:</strong> {row['latitude']:.4f}<br>"
        
        popup = folium.Popup(popup_text, max_width=150)
        
        folium.Marker(
            location=[row['latitude'], row['longitude']],
            tooltip=row['tower_id'],
            popup=popup,
            icon=folium.Icon(color=status_2_color[row['status']])
        ).add_to(m)

    for _, row in outage_data.iterrows():
        popup_text = ""
        popup_text += f"<strong>Event:</strong> {row['event']}<br>"
        popup_text += f"<strong>Severity:</strong> {row['severity']}<br>"
        popup_text += f"<strong>Lon:</strong> {row['center_longitude']:.4f}<br>"
        popup_text += f"<strong>Lat:</strong> {row['center_latitude']:.4f}<br>"
        popup_text += f"<strong>Radius:</strong> {row['radius']:.2f} km<br>"
        
        popup = folium.Popup(popup_text, max_width=150)
        
        folium.Circle(
            location=[row['center_latitude'], row['center_longitude']],
            radius=row['radius'] * 1000,  # Convert to meters
            color=severity_2_color[row['severity']],
            fill=True,
            fill_color=severity_2_color[row['severity']],
            tooltip="Predicted Outage",
            popup=popup
        ).add_to(m)

    return m