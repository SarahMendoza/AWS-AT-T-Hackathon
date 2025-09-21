import json
import boto3
import requests
from decimal import Decimal
from datetime import datetime
import time

AREA = "TX"  
API_URL = f"https://api.weather.gov/alerts/active/area/{AREA}"

def lambda_handler(event, context):
    try:
        # Fetch active alerts
        response = requests.get(API_URL, headers={"User-Agent": "(hackathon-demo, email@example.com)"})
        response.raise_for_status()
        data = response.json()

        #features = data.get('features', [])
        items = []

        #for data in data_json:

        timestamp = int(time.time())
        event = data["features"][0]["properties"]["event"]
        certainty = data["features"][0]["properties"]["certainty"]
        severity = data["features"][0]["properties"]["severity"]
        urgency = data["features"][0]["properties"]["urgency"]
        description = data["features"][0]["properties"]["description"]
        headline = data["features"][0]["properties"]["headline"]
        onset = data["features"][0]["properties"]["onset"]
        response_suggested = data["features"][0]["properties"]["response"]
        geography = data["features"][0]["geometry"][0]["coordinates"]

        item = {
            'timestamp': timestamp,
            'event': event,
            'certainty': certainty,
            'severity': severity,
            'urgency': urgency,
            'description': description,
            'headline': headline,
            'onset': onset,
            'response': response_suggested,
            'geography': geography,
            'location': AREA
        }
            #items.append(item)

        table.put_item(Item=item)

        # For demo: print items instead of inserting to DynamoDB
        # for it in items:
        #     table.put_item(Item=it)

        return {
            'statusCode': 200,
            'body': {"message": "Success", "items_count": len(items), "items": items}
        }

    except Exception as e:
        print(f"Error: {e}")
        return {
            'statusCode': 500,
            'body': {"message": "Error", "error": str(e)}
        }
