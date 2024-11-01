import os
import socket
from pathlib import Path
from datetime import timedelta
from environ import Env
from decouple import config

env = Env()
READ_ENV_FILE = env.bool("DJANGO_READ_ENV_FILE", default=True)

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

if READ_ENV_FILE:
    Env.read_env(str(BASE_DIR / ".env"))

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-g5u*myt(vy)grwuiq=++5n#(44&y8a*%=vnc5^9^9ku4gu1nsc'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['localhost', '127.0.0.1', '0.0.0.0', '13.58.69.214']

hostname, _, ips = socket.gethostbyname_ex(socket.gethostname())
INTERNAL_IPS = [ip[:-1] + '1' for ip in ips] + ['127.0.0.1']

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'whitenoise.runserver_nostatic',
    'corsheaders',
    'rest_framework',
    'rest_framework_simplejwt.token_blacklist',
    'drf_yasg',
    'django_extensions',
    'django_celery_beat',
    # My apps
    'vlog',
    'post',
    'profile_app',
    'authentication',
    'storages',
]

AUTH_USER_MODEL = "authentication.CustomUser"



MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ),
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.LimitOffsetPagination',
    'PAGE_SIZE': 10,
}

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=60),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=90),
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": True,
    "UPDATE_LAST_LOGIN": False,
    "ALGORITHM": "HS256",
    "AUTH_HEADER_TYPES": ("Bearer",),
    "AUTH_HEADER_NAME": "HTTP_AUTHORIZATION",
    "USER_ID_FIELD": "id",
    "USER_ID_CLAIM": "user_id",
    "AUTH_TOKEN_CLASSES": ("rest_framework_simplejwt.tokens.AccessToken",),
    "TOKEN_TYPE_CLAIM": "token_type",
    "JTI_CLAIM": "jti",
    "SLIDING_TOKEN_LIFETIME": timedelta(minutes=1000),
    "SLIDING_TOKEN_REFRESH_LIFETIME": timedelta(days=1),
    "TOKEN_OBTAIN_SERIALIZER": "rest_framework_simplejwt.serializers.TokenObtainPairSerializer",
    "TOKEN_REFRESH_SERIALIZER": "rest_framework_simplejwt.serializers.TokenRefreshSerializer",
    "TOKEN_VERIFY_SERIALIZER": "rest_framework_simplejwt.serializers.TokenVerifySerializer",
    "TOKEN_BLACKLIST_SERIALIZER": "rest_framework_simplejwt.serializers.TokenBlacklistSerializer",
    "SLIDING_TOKEN_OBTAIN_SERIALIZER": "rest_framework_simplejwt.serializers.TokenObtainSlidingSerializer",
    "SLIDING_TOKEN_REFRESH_SERIALIZER": "rest_framework_simplejwt.serializers.TokenRefreshSlidingSerializer",
}

ROOT_URLCONF = 'trend.urls'

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

WSGI_APPLICATION = 'trend.wsgi.application'

# Database settings
USE_POSTGRES_DB = os.environ.get("USE_POSTGRES_DB", False)
if not USE_POSTGRES_DB:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": os.environ.get("SQL_ENGINE", "django.db.backends.sqlite3"),
            "NAME": os.environ.get("POSTGRES_DB", BASE_DIR / "db.sqlite3"),
            "USER": os.environ.get("POSTGRES_USER", "user"),
            "PASSWORD": os.environ.get("POSTGRES_PASSWORD", "password"),
            "HOST": os.environ.get("POSTGRES_HOST", "localhost"),
            "PORT": os.environ.get("POSTGRES_PORT", "5432"),
        }
    }

# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators
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

# Internationalization
# https://docs.djangoproject.com/en/4.2/topics/i18n/
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Static and Media Files Configuration (AWS changes)
STATICFILES_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'  # For storing static files in S3 (AWS changes)
DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'  # For storing media files in S3 (AWS changes)

# AWS Configuration (AWS changes)
AWS_ACCESS_KEY_ID = config('AWS_ACCESS_KEY_ID')  # Your AWS Access Key (AWS changes)
AWS_SECRET_ACCESS_KEY = config('AWS_SECRET_ACCESS_KEY')  # Your AWS Secret Key (AWS changes)
AWS_STORAGE_BUCKET_NAME = 'trend-aws-bucketz'  # Use the bucket name shown in the screenshot (AWS changes)
AWS_S3_REGION_NAME = 'us-east-2'  # The region of your bucket as shown in the screenshot (AWS changes)
AWS_S3_CUSTOM_DOMAIN = f"{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com"  # AWS changes

STATIC_URL = f"https://{AWS_S3_CUSTOM_DOMAIN}/static/"  # AWS changes
STATICFILES_DIRS = [os.path.join(BASE_DIR, "static")]  # AWS changes
MEDIA_URL = f"https://{AWS_S3_CUSTOM_DOMAIN}/media/"  # AWS changes
MEDIA_ROOT = os.path.join(BASE_DIR, "media")  # AWS changes
AWS_DEFAULT_ACL = None  # AWS changes  # Optional, default setting to None allows you to handle permissions in the bucket settings.

# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Email configuration
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 465
EMAIL_HOST_USER = 'kevinwaweru1233@gmail.com'
EMAIL_HOST_PASSWORD = 'tunt vqiw zkpm xbvn'
EMAIL_USE_SSL = True
EMAIL_USE_TLS = False

# CORS settings
CORS_ALLOW_ALL_ORIGINS = True
CSRF_TRUSTED_ORIGINS = []

# Celery settings
CELERY_BROKER_URL = env.str(
    "CELERY_BROKER_URL",
    default='redis://localhost:6379/0'
)
CELERY_RESULT_BACKEND = env.str(
    "CELERY_RESULT_BACKEND",
    default='redis://localhost:6379/0'
)
CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"

# Celery Beat
CELERY_BEAT_SCHEDULER = "django_celery_beat.schedulers:DatabaseScheduler"

# Vlog settings
MAX_VIDEO_SIZE = env.float("MAX_VIDEO_SIZE", default=200 * 1024 * 1024)
MAX_VIDEO_DURATION = env.float("MAX_VIDEO_DURATION", default=15)
