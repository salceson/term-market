"""
Django settings for TermMarket project.

Generated by 'django-admin startproject' using Django 1.8.1.

For more information on this file, see
https://docs.djangoproject.com/en/1.8/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.8/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.8/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'p%39(%wbmgkl1a_kk3+3!bv%t&hf88tav(wa1asx*)1n(v!cuz'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = (
    'djangojs',
    'django_extensions',
    'grappelli',
    'crispy_forms',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'term_market',
    'djcelery',
    'kombu.transport.django',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.security.SecurityMiddleware',
)

ROOT_URLCONF = 'TermMarket.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.request',
            ],
        },
    },
]

WSGI_APPLICATION = 'TermMarket.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.8/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}


# Internationalization
# https://docs.djangoproject.com/en/1.8/topics/i18n/

LANGUAGE_CODE = 'pl'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.8/howto/static-files/

STATIC_URL = '/static/'

AUTH_USER_MODEL = 'term_market.User'

LOGIN_REDIRECT_URL = 'index'

CELERY_RESULT_BACKEND = 'djcelery.backends.database:DatabaseBackend'
BROKER_URL = 'django://'

import os

os.environ['DEBUG'] = '1'
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

OAUTH_REDIRECT_URI = 'http://localhost:8000/accounts/oauth-callback/'
OAUTH_AUTHORIZATION_URI = 'https://accounts.iiet.pl/oauth/authorize'
OAUTH_TOKEN_URI = 'https://accounts.iiet.pl/oauth/token'
OAUTH_LOGOUT_URI = 'https://accounts.iiet.pl/students/sign_out'
OAUTH_SCOPE = ['public', 'extended', 'transcript_number']
OAUTH_DATA_URI = (
    'https://accounts.iiet.pl/oauth/v1/extended',
    'https://accounts.iiet.pl/oauth/v1/transcript_number',
)
OAUTH_DATA_TO_MODEL_MAPPING = (
    ('login', 'username'),
    ('first_name', 'first_name'),
    ('last_name', 'last_name'),
    ('email', 'email'),
    ('user_id', 'internal_id'),
    ('transcript_number', 'transcript_no'),
)

AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
    'term_market.auth_backends.IIETOAuthBackend',
)

GRAPPELLI_ADMIN_TITLE = 'TermMarket'

CRISPY_TEMPLATE_PACK = 'bootstrap3'

