import os
import environ
from pathlib import Path

env = environ.Env(
    DEBUG=(bool, False)
)

BASE_DIR = Path(__file__).resolve().parent.parent
environ.Env.read_env(os.path.join(Path(__file__).resolve().parent.parent.parent, '.env'))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.2/howto/deployment/checklist/

DEBUG = env('DEBUG')
# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env('SECRET_KEY')

# Application definition

DJANGO_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

LOCAL_APPS = [
    'applications.learning_object',
    'applications.adaptation',
    'applications.helpers_functions',
    'applications.integration',
]

THIRD_PARTY_APPS = [
    'channels',
    'rest_framework',
    'drf_yasg',
    'corsheaders',
    # 'django_crontab'
]

INSTALLED_APPS = DJANGO_APPS + LOCAL_APPS + THIRD_PARTY_APPS

WSGI_APPLICATION = 'oeradapter.wsgi.application'
ASGI_APPLICATION = 'oeradapter.asgi.application'

CHANNEL_LAYERS = {
    'default': {
        "BACKEND": "channels.layers.InMemoryChannelLayer",
        # "BACKEND": "channels_redis.core.RedisChannelLayer",
        # 'CONFIG': {
        #    "hosts": [(env('REDIS_HOST'), env('REDIS_PORT'))],
        # },
    },
}

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

X_FRAME_OPTIONS = 'SAMEORIGIN'

ROOT_URLCONF = 'oeradapter.urls'

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

ALLOWED_HOSTS = [
    '127.0.0.1',
    'localhost',
    'oeradap.edutech-project.org',
    '172.16.42.60',
    '192.168.137.91',
    '192.168.137.1',
]

CORS_ALLOWED_ORIGINS = [
    'http://localhost:4200',
    'https://oeradap.edutech-project.org',
    'http://192.168.137.91:4200',
    'http://192.168.137.1:4200',
]

# CORS_ORIGIN_ALLOW_ALL=False
CORS_ORIGIN_WHITELIST = [
    'http://127.0.0.1:4200',
    'http://localhost:4200',
    'https://oeradap.edutech-project.org'
    'http://192.168.137.91:4200',
    'http://192.168.137.1:4200',
]

CSRF_TRUSTED_ORIGINS = [
    'http://localhost:4200',
    'https://oeradap.edutech-project.org'
    'http://192.168.137.91:4200',
    'http://192.168.137.1:4200',
]

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': env('DB_NAME'),
        'USER': env('DB_USER'),
        'PASSWORD': env('DB_PASSWORD'),
        'HOST': env('DB_HOST'),
        'PORT': env('DB_PORT'),
    }
}

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Password validation
# https://docs.djangoproject.com/en/3.2/ref/settings/#auth-password-validators

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
''' 
CRONJOBS = [
    ('*/1 * * * *', 'oeradapter.cron_job.my_cron_job', '>> ' + os.path.join(BASE_DIR, 'test.log'))
]
'''

STATIC_URL = '/uploads/'
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'uploads')]

# Internationalization
# https://docs.djangoproject.com/en/3.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True
