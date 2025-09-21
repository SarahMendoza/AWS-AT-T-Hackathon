import json
import boto3
import requests
from datetime import datetime
import time

AREA = "TX"
API_URL = f"https://api.weather.gov/alerts/active/area/{AREA}"

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('AWS-weather-data')

def lambda_handler(event, context):
    try:
        # Fetch active alerts
        resp = requests.get(API_URL, headers={"User-Agent": "(hackathon-demo, email@example.com)"})
        resp.raise_for_status()
        data = resp.json()

        if not data.get("features"):
            return {"statusCode": 200, "body": {"message": "No active alerts"}}

        feature = data["features"][0]
        props = feature.get("properties", {})
        geom = feature.get("geometry", {})

        timestamp = timestamp = str(int(time.time()))
        event_name = props.get("event")
        certainty = props.get("certainty")
        severity = props.get("severity")
        urgency = props.get("urgency")
        description = props.get("description")
        headline = props.get("headline")
        onset = props.get("onset")
        alert_response = props.get("response")
        geography = geom.get("coordinates")

        item = {
            'timestamp': timestamp,
            'location': AREA,
            'event': event_name or "N/A",
            'certainty': certainty or "N/A",
            'severity': severity or "N/A",
            'urgency': urgency or "N/A",
            'description': description or "N/A",
            'headline': headline or "N/A",
            'onset': onset or "N/A",
            'response': alert_response or "N/A",
            'geography': json.dumps(geography) if geography else "N/A"  # stringify list for DynamoDB
        }

        table.put_item(Item=item)

        return {
            'statusCode': 200,
            'body': {"message": "Success", "inserted_item": item}
        }

    except Exception as e:
        print(f"Error: {e}")
        return {
            'statusCode': 500,
            'body': {"message": "Error", "error": str(e)}
        }
