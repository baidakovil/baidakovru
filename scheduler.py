# scheduler.py

from apscheduler.schedulers.blocking import BlockingScheduler
from update_data import update_all_services

scheduler = BlockingScheduler()
scheduler.add_job(update_all_services, 'interval', minutes=1)
scheduler.start()
