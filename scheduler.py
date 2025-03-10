import logging
import os
import signal
import sys
from datetime import datetime, timedelta

from apscheduler.executors.pool import ThreadPoolExecutor
from apscheduler.schedulers.blocking import BlockingScheduler
from dotenv import load_dotenv

from pyscripts import log_config
from pyscripts.update_data import update_all_platforms

load_dotenv()
# Default to 1 hour if not specified
SCHEDULER_INTERVAL_SEC = int(os.getenv('SCHEDULER_INTERVAL_SEC', '3600'))
# Default to 5 seconds if not specified
SCHEDULER_FIRST_RUN_SEC = int(os.getenv('SCHEDULER_FIRST_RUN_SEC', '5'))

logger = log_config.setup_logging()

logger.info(
    f'Using scheduler interval: {SCHEDULER_INTERVAL_SEC}s, '
    f'first run delay: {SCHEDULER_FIRST_RUN_SEC}s'
)

# Configure executor and job defaults
executors = {'default': ThreadPoolExecutor(max_workers=1)}
job_defaults = {
    'coalesce': True,
    'max_instances': 1,
    'misfire_grace_time': 300,  # 5 minutes grace time
}

scheduler = BlockingScheduler()
first_run_time = datetime.now() + timedelta(seconds=SCHEDULER_FIRST_RUN_SEC)
scheduler.add_job(
    update_all_platforms,
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
