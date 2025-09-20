from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/api/sample', methods=['GET'])
def get_sample():
    sample_data = {
        'id': 1,
        'name': 'Sample Data',
        'description': 'This is a sample API response.'
    }
    return jsonify(sample_data)

if __name__ == '__main__':
    app.run(debug=True)
