from django.apps import AppConfig
from django.conf import settings


class TicketConfig(AppConfig):
    name = 'ticket'

    #WIP - Auto start scheduled jobs
    def ready(self):
        if settings.SCHEDULER_AUTOSTART:
            from .updaters import start
            start()