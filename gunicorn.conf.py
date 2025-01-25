from pyscripts import log_config

workers = 3
bind = "unix:/tmp/gunicorn.sock"
module = "app:app"

# Set up logging
logger = log_config.setup_logging()

# Gunicorn logging settings
accesslog = "/var/log/baidakovru/gunicorn-access.log"
errorlog = "/var/log/baidakovru/gunicorn-error.log"


def on_starting(server):
    logger.info("Gunicorn starting")


def on_exit(server):
    logger.info("Gunicorn shutting down")
