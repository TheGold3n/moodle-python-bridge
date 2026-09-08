from pathlib import Path
from decouple import config

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config('SECRET_KEY', default='django-insecure-kioskbridge-demo-key-12345')

# SECURITY WARNING: don't run with debug turned on in production!
def parse_bool(val):
    if isinstance(val, bool):
        return val
    return str(val).lower() in ('true', '1', 't', 'yes', 'y')

DEBUG = config('DEBUG', default=True, cast=parse_bool)

ALLOWED_HOSTS = ['*']


# Application definition
INSTALLED_APPS = [
    'django.contrib.contenttypes',
    'django.contrib.staticfiles',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'kioskbridge.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
            ],
        },
    },
]

WSGI_APPLICATION = 'kioskbridge.wsgi.application'


# Database - Deshabilitada segun especificaciones del proyecto (Persistencia exclusiva en datos.json)
DATABASES = {}


# Internationalization
LANGUAGE_CODE = 'es-cl'

TIME_ZONE = 'America/Santiago'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
STATIC_URL = 'static/'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Moodle Integration Settings (PoC)
MOODLE_BASE_URL = str(config('MOODLE_BASE_URL', default='http://localhost:8080')).rstrip('/')
MOODLE_WS_TOKEN = str(config('MOODLE_WS_TOKEN', default='')).strip()
MOODLE_PHP_URL = str(config('MOODLE_PHP_URL', default='http://localhost:8080/test_db.php'))

# MongoDB Configuration
MONGO_HOST = config('MONGO_HOST', default='localhost')
MONGO_PORT = config('MONGO_PORT', default=27017, cast=int)
MONGO_DB_NAME = config('MONGO_INITDB_DATABASE', default='kioskbridge_db')
MONGO_URI = config('MONGO_URI', default=f'mongodb://{MONGO_HOST}:{MONGO_PORT}/{MONGO_DB_NAME}')

