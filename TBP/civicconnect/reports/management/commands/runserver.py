from django.core.management.commands.runserver import Command as RunserverCommand
import sys
import os

class Command(RunserverCommand):
    def handle(self, *args, **options):
        # ✅ Redirect stderr to null (Suppress warnings)
        sys.stderr = open(os.devnull, 'w')
        super().handle(*args, **options)
