import boto3
from boto3.dynamodb.conditions import Key
import os
from flask import Flask, jsonify, request
from flask_cors import CORS
from datetime import datetime, timedelta
import time
from data_generation import generate_cell_tower_data, generate_predicted_outages
import uuid
from utils import n_towers_within_zone
from dotenv import load_dotenv

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

load_dotenv()

# --- AWS DynamoDB setup ---
dynamodb = boto3.resource(
    "dynamodb",
    region_name="us-east-1", # change region if needed
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY"), # load from env variables
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY")
)

cell_towers_table = dynamodb.Table("cell-towers")
outages_table = dynamodb.Table("outages")

bedrock_agent_runtime_client = boto3.client('bedrock-agent-runtime', region_name='us-east-1')

# Define the parameters for invoking the agent
agent_id = "GHZTFEK4B4"  # Replace with your agent ID
agent_alias_id = "WBJRP03YGP"  # Replace with your agent alias ID
session_id = "UNIQUE_SESSION_ID"  # A unique ID for the conversation session


# API Routes
@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'timestamp': datetime.now().isoformat()})


@app.route('/api/towers', methods=['GET'])
def get_towers():
    try:
        response = cell_towers_table.scan()
        towers_data = response.get("Items", [])

        return jsonify({'success': True, 'data': towers_data})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/predicted-outages', methods=['GET'])
def get_predicted_outages():
    try:
        response = outages_table.scan()
        outages_data = response.get("Items", [])
        
        return jsonify({'success': True, 'data': outages_data})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/deployment-notes', methods=['GET'])
def get_deployment_notes():
    try:
        # TODO: find tower info in DB, give to agent, return response
        tower_id = request.args.get('tower_id', default=None, type=str)
        notes_response = f"Here are the notes for cell tower '{tower_id}'..."
        
        return jsonify({'success': True, 'data': notes_response})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/assistant', methods=['GET'])
def get_assistant_response():
    try:
        # TODO: find tower info in DB, give that and the input to agent, return response
        user_input = request.args.get('user_input', default=None, type=str)
        tower_id = request.args.get('tower_id', default=None, type=str)
        assistant_response = f"Here is my response to '{user_input}' for tower {tower_id}..."
        
        return jsonify({'success': True, 'data': assistant_response})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500



if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)