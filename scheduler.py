import logging
import os
import signal
import sys
from datetime import datetime, timedelta

from apscheduler.schedulers.blocking import BlockingScheduler
from dotenv import load_dotenv

from pyscripts import log_config
from pyscripts.update_data import update_all_services

load_dotenv()
SCHEDULER_INTERVAL_SEC = int(os.getenv('SCHEDULER_INTERVAL_SEC'))
SCHEDULER_FIRST_RUN_SEC = int(os.getenv('SCHEDULER_FIRST_RUN_SEC'))


logger = log_config.setup_logging()

scheduler = BlockingScheduler()
first_run_time = datetime.now() + timedelta(seconds=SCHEDULER_FIRST_RUN_SEC)
scheduler.add_job(
    update_all_services,
    'interval',
    seconds=SCHEDULER_INTERVAL_SEC,
    next_run_time=first_run_time,
)

logger.info(
    f'Scheduler started. First run in {SCHEDULER_FIRST_RUN_SEC} seconds, then every {SCHEDULER_INTERVAL_SEC} seconds.'
)


def sigterm_handler(signum, frame):
    logger.info("Received SIGTERM. Shutting down scheduler gracefully...")
    scheduler.shutdown()
    sys.exit(0)


signal.signal(signal.SIGTERM, sigterm_handler)

scheduler.start()
