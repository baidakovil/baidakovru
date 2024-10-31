import logging

from apscheduler.schedulers.blocking import BlockingScheduler

from pyscripts import log_config
from pyscripts.update_data import update_all_services

logger = log_config.setup_logging()

scheduler = BlockingScheduler()
scheduler.add_job(update_all_services, 'interval', seconds=10)

logger.info('Scheduler started')
scheduler.start()
