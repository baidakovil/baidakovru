from pyscripts import log_config

workers = 3
bind = "unix:/tmp/gunicorn.sock"
module = "app:app"

# Set up logging
logger = log_config.setup_logging()

# Gunicorn logging settings
accesslog = "/var/log/baidakovru/gunicorn-access.log"
errorlog = "/var/log/baidakovru/gunicorn-error.log"

# Use the custom logger for Gunicorn
# logconfig_dict = {
#     'version': 1,
#     'disable_existing_loggers': False,
#     'root': {
#         'level': 'INFO',
#         'handlers': ['console', 'file'],
#     },
#     'handlers': {
#         'console': {
#             'class': 'logging.StreamHandler',
#             'formatter': 'generic',
#             'stream': 'ext://sys.stdout',
#         },
#         'file': {
#             'class': 'logging.handlers.RotatingFileHandler',
#             'formatter': 'generic',
#             'filename': '/var/log/baidakovru/app.log',
#             'maxBytes': 10240,
#             'backupCount': 5,
#         },
#     },
#     'formatters': {
#         'generic': {
#             'format': '%(asctime)s - %(name)-30s - %(levelname)-5s - %(filename)-25s:%(lineno)-5d - %(message)s',
#             'datefmt': '%Y-%m-%d %H:%M:%S',
#             'class': 'logging.Formatter',
#         },
#     },
# }


def on_starting(server):
    logger.info("Gunicorn starting")


def on_exit(server):
    logger.info("Gunicorn shutting down")
