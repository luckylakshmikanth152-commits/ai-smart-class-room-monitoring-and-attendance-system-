from django.apps import AppConfig
import os
import sys

class AttendanceConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'attendance'

    def ready(self):
        # Start scheduler only when running the server, not during migrations
        if 'runserver' in sys.argv and os.environ.get('RUN_MAIN') == 'true':
            from .scheduler import start_scheduler
            start_scheduler()
