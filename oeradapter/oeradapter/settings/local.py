from .settings import *

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ["*"]

CORS_ALLOWED_ORIGINS = [
    'http://localhost:4001',
]

CORS_ORIGIN_ALLOW_ALL=False
CORS_ORIGIN_WHITELIST = [
    'http://127.0.0.1:4001',
    'http://localhost:4001'
]

CSRF_TRUSTED_ORIGINS = [
    'http://localhost:4001',
]

# Database
# https://docs.djangoproject.com/en/3.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': get_secret_config('DB_NAME'),
        'USER': get_secret_config('DB_USER'),
        'PASSWORD': get_secret_config('DB_PASSWORD'),
        'HOST': get_secret_config('DB_HOST'),
        'PORT': get_secret_config('DB_PORT'),
    }
}

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.2/howto/static-files/

# Default primary key field type
# https://docs.djangoproject.com/en/3.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
