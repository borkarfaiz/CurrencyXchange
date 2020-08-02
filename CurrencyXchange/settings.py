"""
Django settings for CurrencyXchange project.

Generated by 'django-admin startproject' using Django 3.0.8.

For more information on this file, see
https://docs.djangoproject.com/en/3.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.0/ref/settings/
"""

import os
from os import environ

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'dwygmnpphg4#7svzbtbqtdn7safxk$yb&=f%+e4u$)yuptl6hv'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

ALLOWED_HOSTS = ["127.0.0.1"]


# CACHES
# ------------------------------------------------------------------------------

CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/',
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    }
}

# CELERY STUFF
# ------------------------------------------------------------------------------

BROKER_URL = 'redis://localhost:6379'
CELERY_RESULT_BACKEND = 'redis://localhost:6379'
CELERY_ACCEPT_CONTENT = ['application/json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'Asia/Calcutta'


# Mail settings
# ------------------------------------------------------------------------------

EMAIL_PORT = 587

EMAIL_HOST = 'smtp.gmail.com'
EMAIL_USE_TLS = True
EMAIL_HOST_USER = environ.get("EMAIL_ID")
EMAIL_HOST_PASSWORD = environ.get("EMAIL_PASSWORD")

# APPS
# ------------------------------------------------------------------------------
DJANGO_APPS = [
	"django.contrib.admin",
	"django.contrib.auth",
	"django.contrib.contenttypes",
	"django.contrib.sessions",
	"django.contrib.sites",
	"django.contrib.messages",
	"django.contrib.staticfiles",
]

THIRD_PARTY_APPS = [
	"django_extensions",
	"rest_framework",
	"rest_framework.authtoken",
]

LOCAL_APPS = [
	"users",
	"wallet",
	"currency_converter",
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

MIDDLEWARE = [
	'django.middleware.security.SecurityMiddleware',
	'django.contrib.sessions.middleware.SessionMiddleware',
	'django.middleware.common.CommonMiddleware',
	'django.middleware.csrf.CsrfViewMiddleware',
	'django.contrib.auth.middleware.AuthenticationMiddleware',
	'django.contrib.messages.middleware.MessageMiddleware',
	'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'CurrencyXchange.urls'

# django-rest-framework
# -------------------------------------------------------------------------------
# django-rest-framework - https://www.django-rest-framework.org/api-guide/settings/
REST_FRAMEWORK = {
	"DEFAULT_AUTHENTICATION_CLASSES": (
		"rest_framework.authentication.TokenAuthentication",
	),
	"DEFAULT_PERMISSION_CLASSES": ("rest_framework.permissions.IsAuthenticated",),
	'DEFAULT_PARSER_CLASSES': [
		'rest_framework.parsers.JSONParser',
	]
}

# MEDIA
# ------------------------------------------------------------------------------
MEDIA_ROOT = os.path.join(BASE_DIR, "media")
# https://docs.djangoproject.com/en/dev/ref/settings/#media-url
MEDIA_URL = "/media/"

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
			],
		},
	},
]

WSGI_APPLICATION = 'CurrencyXchange.wsgi.application'

# Database
# https://docs.djangoproject.com/en/3.0/ref/settings/#databases

DATABASES = {
	'default': {
		'ENGINE': 'django.db.backends.postgresql',
		'NAME': 'currencyxchange',
		'USER': 'postgres',
		'PASSWORD': 'faiz@currency',
		'HOST': '127.0.0.1',
		'PORT': '5432',
	}
}

# Password validation
# https://docs.djangoproject.com/en/3.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
	{
		'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
	},
	{
		'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
	},
	{
		'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
	},
	{
		'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
	},
]
AUTH_USER_MODEL = "users.User"

# Internationalization
# https://docs.djangoproject.com/en/3.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Asia/Calcutta'

USE_I18N = True

USE_L10N = True

# USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.0/howto/static-files/

STATIC_URL = '/static/'

# Thirdparty API KEYS

EXCHANGE_RATE = "https://api.exchangeratesapi.io/latest"

CURRCONV_LIVE_RATE_API_URL = "https://free.currconv.com/api/v7/convert"
CURRCONV_LIVE_RATE_API_KEY = "87e12e97dc3de632bebf"
