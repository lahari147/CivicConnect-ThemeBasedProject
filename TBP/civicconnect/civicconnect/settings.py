import os
import warnings

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# ✅ Ignore Warnings in Development
warnings.filterwarnings("ignore", category=UserWarning)

# ✅ Secret Key (Use Environment Variable)
SECRET_KEY = os.getenv('DJANGO_SECRET_KEY', 'fallback-secret-key')

# ✅ Debug Mode (Disable in Production)
DEBUG = os.getenv('DJANGO_DEBUG', 'True') == 'True'

# ✅ Allowed Hosts (Update for Production)
ALLOWED_HOSTS = ['127.0.0.1', 'localhost']

# ✅ Database Configuration (PostgreSQL)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('DB_NAME', 'civicconnect_db'),
        'USER': os.getenv('DB_USER', 'postgres'),
        'PASSWORD': os.getenv('DB_PASSWORD', '555666'),  # Change in environment
        'HOST': os.getenv('DB_HOST', 'localhost'),
        'PORT': os.getenv('DB_PORT', '5432'),
    }
}

# ✅ Login URL
LOGIN_URL = '/citizen_login/'

# ✅ Installed Apps
INSTALLED_APPS = [
    'django.contrib.admin',
    "django_extensions",
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'reports',  # Your app
]

# ✅ Middleware
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'civicconnect.urls'

# ✅ Templates
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'reports/templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

# ✅ WSGI Application
WSGI_APPLICATION = 'civicconnect.wsgi.application'

# ✅ Static & Media Files
STATIC_URL = "/static/"
STATICFILES_DIRS = [os.path.join(BASE_DIR, "civicconnect/static")]
STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# ✅ Allow media files to be served in development
if DEBUG:
    import mimetypes
    mimetypes.add_type("image/svg+xml", ".svg", True)

# ✅ Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Asia/Kolkata'
USE_I18N = True
USE_L10N = True
USE_TZ = True

# ✅ Logging Configuration
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'ERROR',
            'class': 'logging.FileHandler',
            'filename': os.path.join(BASE_DIR, 'django_errors.log'),
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'level': 'ERROR',
            'propagate': True,
        },
    },
}

import logging
import warnings

# ✅ Suppress specific warnings
warnings.filterwarnings("ignore", category=UserWarning)

# ✅ Suppress Django's development server warnings
logging.getLogger("django").setLevel(logging.ERROR)
logging.getLogger("django.server").setLevel(logging.ERROR)
logging.getLogger("django.request").setLevel(logging.ERROR)
logging.getLogger("django.db.backends").setLevel(logging.ERROR)
