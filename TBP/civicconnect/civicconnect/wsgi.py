import os
import sys
import warnings
from django.core.wsgi import get_wsgi_application

# ✅ Suppress the Development Server Warning
warnings.filterwarnings("ignore", category=UserWarning, module="django.utils.autoreload")

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'civicconnect.settings')

application = get_wsgi_application()
