import logging
import os
import sqlite3
from logging.handlers import RotatingFileHandler

from dotenv import load_dotenv
from flask import Flask, jsonify, request, send_from_directory

from pyscripts import log_config

load_dotenv()
DB_PATH = os.getenv('DB_PATH')

logger = log_config.setup_logging()
logger.info('Application startup')

app = Flask(__name__, static_folder='styles', static_url_path='/styles')
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')


@app.route('/')
def index():
    return send_from_directory('.', 'index.html')


@app.route('/jsscripts/<path:filename>')
def serve_js(filename):
    return send_from_directory('jsscripts', filename)


@app.route('/api/updates', methods=['GET'])
def get_updates():
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT name, formatted_datetime FROM services")
        services = cursor.fetchall()
        conn.close()

        data = [
            {'name': name, 'formatted_datetime': formatted_datetime}
            for name, formatted_datetime in services
        ]
        return jsonify(data)
    except Exception as e:
        logger.error(f'Error fetching updates: {str(e)}')
        return jsonify({'error': 'Internal Server Error'}), 500


@app.after_request
def add_header(response):
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['Content-Security-Policy'] = "frame-ancestors 'none'"
    response.headers['X-XSS-Protection'] = '1; mode=block'
    return response


@app.route('/api/log-error', methods=['POST'])
def log_error():
    error_data = request.json
    logger.error(
        f"Client-side error: {error_data['message']}\nStack: {error_data['stack']}"
    )
    return jsonify({"status": "error logged"}), 200


if __name__ == '__main__':
    debug = os.environ.get('FLASK_DEBUG', 'False').lower() in ('true', '1', 't')
    port = int(os.environ.get('FLASK_PORT', 5000))
    host = os.environ.get('FLASK_HOST', '127.0.0.1')
    app.run(debug=debug, host=host, port=port)
