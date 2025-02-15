import json
import logging
import os
import signal
import sys
from traceback import format_exc
from typing import Dict, List, Optional, Tuple, Union

from dotenv import load_dotenv
from flask import Flask, Response, g, jsonify, render_template, request
from flask_babel import Babel, gettext
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_mail import Mail, Message

from pyscripts import log_config
from pyscripts.config import EVENT_TYPES, config
from pyscripts.database.dbmanager import DatabaseManager
from pyscripts.date_formatters import format_full_date, format_time_ago

load_dotenv()

SECRET_KEY = os.getenv('SECRET_KEY')
FLASK_DEBUG = os.getenv('FLASK_DEBUG', 'false').lower() in ('true', '1', 't')
FLASK_PORT = int(os.getenv('FLASK_PORT', '5000'))
FLASK_HOST = os.getenv('FLASK_HOST', '127.0.0.1')

logger = log_config.setup_logging()
logger.info('Application startup')

app = Flask(__name__, static_folder='static', template_folder='templates')
app.config['SECRET_KEY'] = SECRET_KEY

# Mail configuration
app.config.update(
    MAIL_SERVER=os.getenv('MAIL_SERVER', 'smtp.gmail.com'),
    MAIL_PORT=int(os.getenv('MAIL_PORT', '587')),
    MAIL_USE_TLS=os.getenv('MAIL_USE_TLS', 'true').lower() in ('true', '1', 't'),
    MAIL_USERNAME=os.getenv('MAIL_USERNAME'),
    MAIL_PASSWORD=os.getenv('MAIL_PASSWORD'),
    MAIL_DEFAULT_SENDER=('Сайт baidakov.ru', os.getenv('MAIL_DEFAULT_SENDER')),
    MAIL_RECIPIENT=os.getenv('MAIL_RECIPIENT'),
)

mail = Mail(app)

# Initialize database manager
db_manager = DatabaseManager(config.db_path)

limiter = Limiter(
    app=app, key_func=get_remote_address, default_limits=["200 per day", "50 per hour"]
)

# Конфигурация Babel
app.config['LANGUAGES'] = {'en': 'English', 'ru': 'Русский'}
app.config['BABEL_DEFAULT_LOCALE'] = 'ru'


def get_locale():
    lang = request.args.get('lang')
    if lang in app.config['LANGUAGES']:
        return lang
    return request.accept_languages.best_match(app.config['LANGUAGES'].keys())


@app.context_processor
def utility_processor():
    return {'get_locale': get_locale}


babel = Babel(app, locale_selector=get_locale)


# Page routes
@app.route('/')
def index():
    return render_template('index.html')


@app.route('/bio')
def bio():
    return render_template('bio.html')


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/contact', methods=['GET', 'POST'])
def contact():
    message = None
    message_type = None

    if request.method == 'POST':
        try:
            email = request.form['email']
            subject = request.form['subject']
            message_text = request.form['message']

            # Проверяем конфигурацию
            required_settings = [
                'MAIL_SERVER',
                'MAIL_USERNAME',
                'MAIL_PASSWORD',
                'MAIL_RECIPIENT',
            ]
            missing_settings = [s for s in required_settings if not app.config.get(s)]

            if missing_settings:
                raise ValueError(
                    f"Missing required mail settings: {', '.join(missing_settings)}"
                )

            msg = Message(
                subject=f"Сообщение с сайта: {subject}",
                recipients=[app.config['MAIL_RECIPIENT']],
                body=f"От: {'<не указан>' if not email else email}\n\n{message_text}",
                reply_to=email if email else None,
            )

            mail.send(msg)
            message = "Сообщение успешно отправлено!"
            message_type = "success"

        except ValueError as ve:
            message = str(ve)
            message_type = "error"
        except Exception as e:
            logger.error(f"Failed to send email. Error: {str(e)}")
            message = "Произошла ошибка при отправке сообщения."
            message_type = "error"

    return render_template(
        'contact.html',
        message=message,
        message_type=message_type,
    )


# API routes
@app.route('/api/updates', methods=['GET'])
@limiter.limit("1 per second")
def get_updates() -> Tuple[Response, int]:
    try:
        if not db_manager.health_check():
            logger.error("Database health check failed")
            return jsonify({'error': 'Database unavailable'}), 503

        updates: List[Dict] = []
        with db_manager.get_connection() as conn:
            try:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    WITH LatestDatetimes AS (
                        -- First get the latest NON-ERROR datetime for each platform
                        SELECT platform_id, MAX(formatted_datetime) as max_datetime
                        FROM updates
                        WHERE NOT is_error
                        GROUP BY platform_id
                    ),
                    LatestIds AS (
                        -- Then for each platform's latest datetime, get the latest ID
                        SELECT u.platform_id, MAX(u.id) as max_id
                        FROM updates u
                        INNER JOIN LatestDatetimes lt 
                            ON u.platform_id = lt.platform_id 
                            AND u.formatted_datetime = lt.max_datetime
                            AND NOT u.is_error
                        GROUP BY u.platform_id
                    )
                    -- Finally, get the full records using the latest IDs
                    SELECT u.platform_id, u.platform_name, u.formatted_datetime, 
                           u.update_desc, u.update_event, u.platform_url
                    FROM updates u
                    INNER JOIN LatestIds li 
                        ON u.platform_id = li.platform_id 
                        AND u.id = li.max_id
                    WHERE NOT u.is_error
                    ORDER BY u.formatted_datetime DESC
                    """
                )
                updates = cursor.fetchall()
            except Exception as db_error:
                logger.error(f"Database query error: {db_error}")
                return jsonify({'error': 'Database query failed'}), 500

        data = [
            {
                'platform_id': platform_id,
                'platform_name': platform_name,
                'formatted_datetime': formatted_datetime,
                'update_desc': update_desc,
                'update_event': update_event,
                'platform_url': platform_url,
                'time_ago': format_time_ago(formatted_datetime),
                'full_date': format_full_date(formatted_datetime),
            }
            for platform_id, platform_name, formatted_datetime, update_desc, update_event, platform_url in updates
        ]

        return jsonify(data), 200
    except Exception as e:
        logger.error(f'Error fetching updates: {str(e)}\n{format_exc()}')
        return jsonify({'error': 'Internal Server Error'}), 500


@app.route('/api/event-types')
@limiter.limit("10 per minute")
def get_event_types():
    """Return all event types with translations based on current locale."""
    translations = {
        event_type: gettext(description)
        for event_type, description in EVENT_TYPES.items()
    }
    return jsonify(translations)


@app.route('/api/log-error', methods=['POST'])
@limiter.limit("5 per minute")
def log_error():
    error_data = request.json
    logger.error(
        f"Client-side error: {error_data['message']}\nStack: {error_data['stack']}"
    )
    return jsonify({"status": "error logged"}), 200


# Security headers
@app.after_request
def add_header(response):
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['Content-Security-Policy'] = "frame-ancestors 'none'"
    response.headers['X-XSS-Protection'] = '1; mode=block'
    return response


# Shutdown handling
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
