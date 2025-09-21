import boto3
from boto3.dynamodb.conditions import Key
import os
from flask import Flask, jsonify, request
from flask_cors import CORS
from datetime import datetime, timedelta
import time
from data_generation import generate_cell_tower_data, generate_predicted_outages
import uuid
from dotenv import load_dotenv
import logging

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

app.logger.setLevel(logging.DEBUG)

load_dotenv()

# --- AWS DynamoDB setup ---
dynamodb = boto3.resource(
    "dynamodb",
    region_name="us-east-1",
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY")
)

cell_towers_table = dynamodb.Table("cell-towers")
outages_table = dynamodb.Table("outages")

bedrock_agent_runtime_client = boto3.client(
    'bedrock-agent-runtime', 
    region_name='us-east-1',
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY")
)

chatbot_id = os.getenv("CHATBOT_ID")
chatbot_alias_id = os.getenv("CHATBOT_ALIAS_ID")

notes_agent_id = os.getenv("NOTES_AGENT_ID")
notes_agent_alias_id = os.getenv("NOTES_AGENT_ALIAS_ID")


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
        session_id = str(uuid.uuid4())
        
        tower_id = request.args.get('tower_id', default=None, type=str)
        
        tower_item = cell_towers_table.query(
            KeyConditionExpression=Key('tower_id').eq(tower_id)
        )['Items'][0]
        
        
        prompt_text = ""
        prompt_text += f"Tower ID: {tower_item['tower_id']}<br>"
        prompt_text += f"Status: {tower_item['status']}<br>"
        prompt_text += f"RSRP: {float(tower_item['signal_strength']):.2f} dBm<br>"
        prompt_text += f"Bandwidth: {tower_item['bandwidth']} MHz<br>"
        prompt_text += f"Technology: {tower_item['technology']}<br>"
        prompt_text += f"Coverage: {float(tower_item['coverage_radius']):.2f} mi<br>"
        prompt_text += f"Lon: {float(tower_item['longitude']):.4f}<br>"
        prompt_text += f"Lat: {float(tower_item['latitude']):.4f}<br>"
        
        agent_response = bedrock_agent_runtime_client.invoke_agent(
            agentId=notes_agent_id,
            agentAliasId=notes_agent_alias_id,
            sessionId=session_id,
            inputText=prompt_text
        )
        app.logger.info(agent_response)

        output_text = ""
        event_stream = agent_response.get('completion', [])
        
        for event in event_stream:
            app.logger.debug(f"Event type: {type(event)}, Event: {event}")
            
            if 'chunk' in event:
                chunk = event['chunk']
                if 'bytes' in chunk:
                    chunk_text = chunk['bytes'].decode('utf-8')
                    output_text += chunk_text
                    app.logger.info(f"Chunk: {chunk_text}")
            elif 'trace' in event:
                # Handle trace events for debugging
                app.logger.info(f"Trace: {event['trace']}")
            elif 'returnControl' in event:
                # Handle return control events
                app.logger.info(f"Return control: {event['returnControl']}")
        
        app.logger.info(f"Final output: {output_text}")
        return jsonify({'success': True, 'data': output_text})

        return jsonify({'success': True, 'data': output_text})
    except Exception as e:
        app.logger.error(e)
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/assistant', methods=['GET'])
def get_assistant_response():
    try:
        user_input = request.args.get('user_input', default=None, type=str)
        session_id = str(uuid.uuid4())
        
        agent_response = bedrock_agent_runtime_client.invoke_agent(
            agentId=chatbot_id,
            agentAliasId=chatbot_alias_id,
            sessionId=session_id,
            inputText=user_input
        )
        app.logger.info(agent_response)

        output_text = ""
        for event in agent_response["completion"]:
            if "chunk" in event:
                output_text += event["chunk"]["bytes"].decode('utf-8')
        app.logger.info(output_text)

        return jsonify({'success': True, 'data': output_text})
    except Exception as e:
        app.logger.error(e)
        return jsonify({'success': False, 'error': str(e)}), 500



if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)