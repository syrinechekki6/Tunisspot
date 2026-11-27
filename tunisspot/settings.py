import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'django-insecure-tunisspot-super-secret-key-wintokhrej-style-2026'

DEBUG = True

ALLOWED_HOSTS = ['*']

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # TunisSpot Modular Apps
    'users.apps.UsersConfig',
    'spots.apps.SpotsConfig',
    'transports.apps.TransportsConfig',
    'itineraries.apps.ItinerariesConfig',
    'events.apps.EventsConfig',
]

AUTH_USER_MODEL = 'users.Utilisateur'

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'tunisspot.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'spots.context_processors.tunisspot_context',
            ],
        },
    },
]

WSGI_APPLICATION = 'tunisspot.wsgi.application'

# =====================================================================
# CONFIGURATION DE BASE DE DONNÉES (SQL DEVELOPER / ORACLE / SQLITE)
# =====================================================================
# Par défaut, SQLite est activé pour une exécution immédiate sans prérequis.
# Pour brancher Django DIRECTEMENT sur votre base Oracle XE (SQL Developer) :
# Définissez USE_ORACLE=True ou vos identifiants Oracle ci-dessous.
USE_ORACLE = os.environ.get('USE_ORACLE', 'False').lower() in ('true', '1', 'yes')

if USE_ORACLE:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.oracle',
            'NAME': os.environ.get('ORACLE_DSN', '127.0.0.1:1521/XE'),
            'USER': os.environ.get('ORACLE_USER', 'TUNISSPOT'),
            'PASSWORD': os.environ.get('ORACLE_PASSWORD', 'tunisspot'),
        }
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {
            'min_length': 4,
        }
    },
]

LANGUAGE_CODE = 'fr-fr'
TIME_ZONE = 'Africa/Tunis'
USE_I18N = True
USE_TZ = True

STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

LOGIN_URL = '/users/login/'
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'
