from flask import Flask, jsonify, request
from flask_cors import CORS
from datetime import datetime, timedelta
import time
from data_generation import generate_cell_tower_data, generate_predicted_outages


app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# API Routes
@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'timestamp': datetime.now().isoformat()})

@app.route('/api/towers', methods=['GET'])
def get_towers():
    try:
        towers_data = generate_cell_tower_data()
        return jsonify({'success': True, 'data': towers_data})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/predicted-outages', methods=['GET'])
def get_predicted_outages():
    try:
        outages_data = generate_predicted_outages()
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

@app.route('/api/assistant-outage', methods=['GET'])
def get_assistant_response_for_outage():
    try:
        # TODO: find tower info in DB, give that and the input to agent, return response
        user_input = request.args.get('user_input', default=None, type=str)
        outage_id = request.args.get('outage_id', default=None, type=str)
        assistant_response = f"Here is my response to '{user_input}' for outage {outage_id}..."
        
        return jsonify({'success': True, 'data': assistant_response})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500





if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)