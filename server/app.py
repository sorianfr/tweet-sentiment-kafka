import eventlet
eventlet.monkey_patch()

from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO, emit
import requests
import threading
import logging
import json
from routes.upload import upload_bp

# Configure logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    handlers=[logging.StreamHandler()])

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")  # Enable CORS for SocketIO

app.register_blueprint(upload_bp, url_prefix='/upload')

# ksqlDB server URL
KSQLDB_SERVER = 'http://ksqldb-server:8088'

def fetch_data():
    logging.info("Querying ksqlDB...")

    query = {
        "sql": "SELECT sentiment_label, count, avg_polarity FROM sentiment_stats EMIT CHANGES;",
        "streamsProperties": {
            "ksql.streams.auto.offset.reset": "latest"
        }
    }
    headers = {'Content-Type': 'application/vnd.ksql.v1+json; charset=utf-8'}

    try:
        response = requests.post(f"{KSQLDB_SERVER}/query-stream", json=query, headers=headers, stream=True)
        for line in response.iter_lines():
            if line:
                logging.info(f"Received line: {line.decode('utf-8')}")
                data = line.decode('utf-8')
                socketio.emit('update', {'data': data}, namespace='/stats')  # Emit 'update' event
    except requests.exceptions.RequestException as e:
        logging.error(f"Failed to query ksqlDB: {e}")

def start_ksql_stream():
    """Start the ksqlDB query in a background thread to prevent blocking the main thread."""
    thread = threading.Thread(target=fetch_data)
    thread.daemon = True  # Ensures the thread will close when the main thread closes
    thread.start()


@socketio.on('connect', namespace='/stats')
def test_connect():
    print('Client connected')
    app.logger.info("Client connected")
    emit('update', {'data': 'Connected and waiting for real-time data...'})

@socketio.on('disconnect', namespace='/stats')
def test_disconnect():
    print('Client disconnected')

if __name__ == "__main__":
    start_ksql_stream()
    socketio.run(app, host='0.0.0.0', port=5000, use_reloader=False)
