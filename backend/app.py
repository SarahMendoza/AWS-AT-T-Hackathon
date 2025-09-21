import boto3
import os
from flask import Flask, jsonify, request
from flask_cors import CORS
from datetime import datetime, timedelta
import time
from data_generation import generate_cell_tower_data, generate_predicted_outages
import uuid


app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# --- AWS DynamoDB setup ---
dynamodb = boto3.resource(
    "dynamodb",
    region_name="us-east-1",  # change region if needed
    aws_access_key_id=os.getenv("key"),     # load from env variables
    aws_secret_access_key=os.getenv("key")
)

# Change this to your DynamoDB table name
weather_table = dynamodb.Table("AWS-weather-data")
network_table = dynamodb.Table("network-status-data")
weather_outages_table = dynamodb.Table("weatheroutages")
network_outages_table = dynamodb.Table("networkoutages")

bedrock_agent_runtime_client = boto3.client('bedrock-agent-runtime')

# Define the parameters for invoking the agent
agent_id = "GHZTFEK4B4"  # Replace with your agent ID
agent_alias_id = "WBJRP03YGP"  # Replace with your agent alias ID
session_id = "UNIQUE_SESSION_ID"  # A unique ID for the conversation session
input_text = "What is the current status of my order?" # The user's prompt




# API Routes
@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'timestamp': datetime.now().isoformat()})

@app.route('/api/towers', methods=['GET'])
def get_towers():
    try:
        # towers_data = generate_cell_tower_data()
        response = network_table.scan()
        items = response.get("Items", [])


        return jsonify({'success': True, 'data': items})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/predicted-outages', methods=['GET'])
def get_predicted_outages():
    try:
        #outages_data = generate_predicted_outages()
        response = weather_outages_table.scan()
        outages_data = response.get("Items", [])

        return jsonify({'success': True, 'data': outages_data})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/instructions-cell', methods=['GET'])
def get_instructions_for_cell():
    try:
        # TODO: find tower info in DB, give to agent, return response
        tower_id = request.args.get('tower_id', default=None, type=str)
        instructions_response = f"Here are the instructions for cell tower '{tower_id}'..."
        
        return jsonify({'success': True, 'data': instructions_response})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/instructions-outage', methods=['GET'])
def get_instructions_for_outage():
    try:
        # TODO: find outage info in DB, give to agent, return response
        outage_id = request.args.get('outage_id', default=None, type=str)
        instructions_response = f"Here are the instructions for outage {outage_id}..."
        
        return jsonify({'success': True, 'data': instructions_response})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/assistant-cell', methods=['GET'])
def get_assistant_response_for_cell():
    try:
        # TODO: find tower info in DB, give that and the input to agent, return response
        user_input = request.args.get('user_input', default=None, type=str)
        tower_id = request.args.get('tower_id', default=None, type=str)
        assistant_response = f"Here is my response to '{user_input}' for tower {tower_id}..."
        
        return jsonify({'success': True, 'data': assistant_response})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/assistant-outage', methods=['POST'])
def get_assistant_response_for_outage():
    #try:
        # TODO: find tower info in DB, give that and the input to agent, return response
        #user_input = request.args.get('user_input', default=None, type=str)
        #outage_id = request.args.get('outage_id', default=None, type=str)
        #assistant_response = f"Here is my response to '{user_input}' for outage {outage_id}..."

    try:

        user_input = request.args.get('user_input', default=None, type=str)
        outage_id = request.args.get('outage_id', default=None, type=str)
        data = request.json
        #user_input = data.get("inputText")
        
        if not user_input:
            return jsonify({"status": "error", "message": f"user input not valid: f{user_input}"}), 400

        # Generate or reuse sessionId (frontend can also pass it in if you want persistent chat)
        session_id = data.get("sessionId", str(uuid.uuid4()))

        # Call the agent
        response = client.invoke_agent(
            agentId=GHZTFEK4B4,
            agentAliasId=WBJRP03YGP,
            sessionId=session_id,
            inputText=user_input
        )

        # Extract text from agent’s response
        messages = []
        for event in response["completion"]:
            if "chunk" in event:
                messages.append(event["chunk"]["bytes"].decode("utf-8"))

        assistant_response = "".join(messages)

        return jsonify({'success': True, 'data': assistant_response})

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500





if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)