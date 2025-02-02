import logging
import os
import signal
import sys
from traceback import format_exc

from dotenv import load_dotenv
from flask import Flask, jsonify, render_template, request
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_mail import Mail, Message
from werkzeug.utils import secure_filename

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

UPLOAD_FOLDER = 'temp_uploads'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'doc', 'docx', 'jpg', 'jpeg', 'png'}
MAX_CONTENT_LENGTH = 5 * 1024 * 1024  # 5 MB

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH

mail = Mail(app)

# Initialize database manager
db_manager = DatabaseManager(config.db_path)

limiter = Limiter(
    app=app, key_func=get_remote_address, default_limits=["200 per day", "50 per hour"]
)


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


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/contact', methods=['GET', 'POST'])
def contact():
    message = None
    message_type = None
    error_details = None  # для режима разработки

    if request.method == 'POST':
        try:
            email = request.form['email']
            subject = request.form['subject']
            message_text = request.form['message']
            attachment = request.files.get('attachment')

            # Создаем временную директорию, если её нет
            if not os.path.exists(UPLOAD_FOLDER):
                os.makedirs(UPLOAD_FOLDER)

            # Обработка прикрепленного файла
            attachment_path = None
            if attachment and attachment.filename:
                if allowed_file(attachment.filename):
                    filename = secure_filename(attachment.filename)
                    attachment_path = os.path.join(
                        app.config['UPLOAD_FOLDER'], filename
                    )
                    attachment.save(attachment_path)
                else:
                    raise ValueError("Недопустимый формат файла")

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

            # Прикрепляем файл к письму, если он есть
            if attachment_path:
                with open(attachment_path, 'rb') as f:
                    msg.attach(
                        filename=secure_filename(attachment.filename),
                        content_type=attachment.content_type,
                        data=f.read(),
                    )

            mail.send(msg)

            # Удаляем временный файл
            if attachment_path and os.path.exists(attachment_path):
                os.remove(attachment_path)

            message = "Сообщение успешно отправлено!"
            message_type = "success"

        except ValueError as ve:
            message = str(ve)
            message_type = "error"
        except Exception as e:
            error_trace = format_exc()
            logger.error(
                f"Failed to send email. Error: {str(e)}\nTraceback:\n{error_trace}"
            )
            message = "Произошла ошибка при отправке сообщения."
            message_type = "error"
            if app.debug:  # Только в режиме разработки
                error_details = f"{str(e)}\n{error_trace}"

        finally:
            # Очистка временных файлов
            if (
                'attachment_path' in locals()
                and attachment_path
                and os.path.exists(attachment_path)
            ):
                try:
                    os.remove(attachment_path)
                except:
                    pass

    return render_template(
        'contact.html',
        message=message,
        message_type=message_type,
        error_details=error_details,
    )


# API routes
@app.route('/api/updates', methods=['GET'])
@limiter.limit("1 per second")
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
                WITH LatestDatetimes AS (
                    -- First get the latest datetime for each platform
                    SELECT platform_id, MAX(formatted_datetime) as max_datetime
                    FROM updates
                    GROUP BY platform_id
                ),
                LatestIds AS (
                    -- Then for each platform's latest datetime, get the latest ID
                    SELECT u.platform_id, MAX(u.id) as max_id
                    FROM updates u
                    INNER JOIN LatestDatetimes lt 
                        ON u.platform_id = lt.platform_id 
                        AND u.formatted_datetime = lt.max_datetime
                    GROUP BY u.platform_id
                )
                -- Finally, get the full records using the latest IDs
                SELECT u.platform_id, u.platform_name, u.formatted_datetime, 
                       u.update_desc, u.platform_url
                FROM updates u
                INNER JOIN LatestIds li 
                    ON u.platform_id = li.platform_id 
                    AND u.id = li.max_id
                ORDER BY u.formatted_datetime DESC
                """
            )
            updates = cursor.fetchall()

        data = [
            {
                'platform_id': platform_id,
                'platform_name': platform_name,
                'formatted_datetime': formatted_datetime,
                'update_desc': update_desc,
                'platform_url': platform_url,
            }
            for platform_id, platform_name, formatted_datetime, update_desc, platform_url in updates
        ]

        return jsonify(data)
    except Exception as e:
        logger.error(f'Error fetching updates: {str(e)}')
        return jsonify({'error': 'Internal Server Error'}), 500


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
