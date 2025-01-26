import logging
import os
import signal
import sys

from dotenv import load_dotenv
from flask import Flask, jsonify, request, send_from_directory
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

from pyscripts import log_config
from pyscripts.config import config
from pyscripts.database.dbmanager import DatabaseManager

load_dotenv()

SECRET_KEY = os.getenv('SECRET_KEY')
FLASK_DEBUG = os.getenv('FLASK_DEBUG', 'false').lower() in ('true', '1', 't')
FLASK_PORT = int(os.getenv('FLASK_PORT', '5000'))
FLASK_HOST = os.getenv('FLASK_HOST', '127.0.0.1')

logger = log_config.setup_logging()
logger.info('Application startup')

app = Flask(__name__, static_folder='styles', static_url_path='/styles')
app.config['SECRET_KEY'] = SECRET_KEY

# Initialize database manager
db_manager = DatabaseManager(config.db_path)

limiter = Limiter(
    app=app, key_func=get_remote_address, default_limits=["200 per day", "50 per hour"]
)


@app.route('/')
def index():
    return send_from_directory('.', 'index.html')


@app.route('/jsscripts/<path:filename>')
def serve_js(filename):
    return send_from_directory('jsscripts', filename)


@app.route('/api/updates', methods=['GET'])
@limiter.limit("1 per second")  # Add rate limiting
def get_updates():
    try:
        # Check database health before operations
        if not db_manager.health_check():
            logger.error("Database health check failed")
            return jsonify({'error': 'Database unavailable'}), 503

        with db_manager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT platform_id, platform_name, formatted_datetime, update_desc 
                FROM updates 
                ORDER BY formatted_datetime DESC
            """
            )
            updates = cursor.fetchall()

        data = [
            {
                'platform_id': platform_id,
                'platform_name': platform_name,
                'formatted_datetime': formatted_datetime,
                'update_desc': update_desc,
            }
            for platform_id, platform_name, formatted_datetime, update_desc in updates
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
@limiter.limit("5 per minute")  # Add rate limiting
def log_error():
    error_data = request.json
    logger.error(
        f"Client-side error: {error_data['message']}\nStack: {error_data['stack']}"
    )
    return jsonify({"status": "error logged"}), 200


def sigterm_handler(signum, frame):
    logger.info("Received SIGTERM. Shutting down gracefully...")
    # Clean up database connections
    try:
        db_manager.close_all()
    except Exception as e:
        logger.error(f"Error during shutdown: {e}")
    sys.exit(0)


signal.signal(signal.SIGTERM, sigterm_handler)

if __name__ == '__main__':
    # Ensure database is properly initialized on startup
    if not db_manager.health_check():
        logger.error("Database initialization failed. Exiting.")
        sys.exit(1)

    app.run(debug=FLASK_DEBUG, host=FLASK_HOST, port=FLASK_PORT)
