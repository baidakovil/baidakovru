import logging
import signal
import sys

from apscheduler.schedulers.blocking import BlockingScheduler

from pyscripts import log_config
from pyscripts.update_data import update_all_services

logger = log_config.setup_logging()

scheduler = BlockingScheduler()
scheduler.add_job(update_all_services, 'interval', seconds=10)

logger.info('Scheduler started')


def sigterm_handler(signum, frame):
    logger.info("Received SIGTERM. Shutting down scheduler gracefully...")
    scheduler.shutdown()
    sys.exit(0)


signal.signal(signal.SIGTERM, sigterm_handler)

scheduler.start()
