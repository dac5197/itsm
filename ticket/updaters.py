from datetime import datetime
import logging

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.executors.pool import ProcessPoolExecutor, ThreadPoolExecutor

from django_apscheduler.jobstores import DjangoJobStore, register_events
from django_apscheduler.models import DjangoJobExecution

from django.conf import settings

from .utils import set_resolved_tickets_closed

#Background scheduler to run daily procedures
#https://medium.com/@kevin.michael.horan/scheduling-tasks-in-django-with-the-advanced-python-scheduler-663f17e868e6


# Create scheduler to run in a thread inside the application process
#https://medium.com/@mrgrantanderson/replacing-cron-and-running-background-tasks-in-django-using-apscheduler-and-django-apscheduler-d562646c062e
scheduler = BackgroundScheduler(settings.SCHEDULER_CONFIG)

def start():

    # Hook into the apscheduler logger
    if settings.DEBUG:
        logging.basicConfig()
        logging.getLogger('apscheduler').setLevel(logging.DEBUG)

    #scheduler = BackgroundScheduler()
    #scheduler.add_jobstore(DjangoJobStore(), "default")
    #Set all resolved tickets to cloed with resolved date older than 3 days
    #scheduler.add_interval_job(set_resolved_tickets_closed, min=5) #days=1)
    scheduler.add_job(set_resolved_tickets_closed, 'interval', hours=24, name='Close Tickets')
    register_events(scheduler)
    scheduler.start()