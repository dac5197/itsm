from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler

from .utils import set_resolved_tickets_closed

#Background scheduler to run daily procedures
#https://medium.com/@kevin.michael.horan/scheduling-tasks-in-django-with-the-advanced-python-scheduler-663f17e868e6
def start():
    scheduler = BackgroundScheduler()

    #Set all resolved tickets to cloed with resolved date older than 3 days
    scheduler.add_interval_job(set_resolved_tickets_closed, days=1)

    scheduler.start()