from .settings import *

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

ALLOWED_HOSTS = ["https://oeradap.edutech-project.org"]

CORS_ALLOWED_ORIGINS = ["https://oeradap.edutech-project.org"]

CSRF_TRUSTED_ORIGINS = ["https://oeradap.edutech-project.org"]


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