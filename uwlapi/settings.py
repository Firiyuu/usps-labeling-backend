import os
from core.utils.utils import glob_list
from corsheaders.defaults import default_headers
from dotenv import load_dotenv

from smartystreets_python_sdk import (
    StaticCredentials,
    ClientBuilder
)

from core.utils.teaplixAPI import TeaplixAPI
from square.client import Client as SqClient

load_dotenv()

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "SECRET_KEY=hbbyg+k11a)4&@i7t*c1lan(wuk5a+d9kc24=wjg7i^u^rh_97"
SECURE_CONTENT_TYPE_NOSNIFF = True

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['*']
INTERNAL_IPS = glob_list(['127.0.0.1', '192.168.*.*', '172.*.*.*', '10.*.*.*'])

REDIS_URL = os.getenv('REDIS_URL', 'redis://locahost:6379')

CELERY_BROKER_URL = REDIS_URL
CELERY_RESULT_BACKEND = REDIS_URL
CELERY_ACCEPT_CONTENT = ['application/json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'corsheaders',
    'rest_framework',
    'rest_framework.authtoken',
    'rest_auth',
    'core',
    'accounts',
    'marketplaces',
    'addresses',
    'django.contrib.sites',
    'allauth',
    'allauth.account',
    'rest_auth.registration',
    'drf_yasg',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

CORS_ORIGIN_ALLOW_ALL = True

# CORS_ORIGIN_WHITELIST = (
#     "http://localhost:8080",
#     "http://localhost:3000",
#     "http://localhost:8000",
#     "http://3.16.147.166:8000",
#     "http://3.16.147.166:8080",
#     "http://3.16.147.166:3000",
#     "http://0.0.0.0:8080",
#     "http://0.0.0.0:3000",
#     "http://0.0.0.0:8000",
# )

CORS_ALLOW_HEADERS = default_headers + (
   'Validation', 'tzinfo', 'language'
)

ROOT_URLCONF = 'uwlapi.urls'
WSGI_APPLICATION = 'uwlapi.wsgi.application'

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



# Database
# https://docs.djangoproject.com/en/3.0/ref/settings/#databases

# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.sqlite3',
#         'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
#     }
# }

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('DATABASE_NAME'),
        'USER': os.environ.get('DATABASE_USER'),
        'PASSWORD': os.environ.get('DATABASE_PASSWORD'),
        'HOST': os.environ.get('DATABASE_HOST', '127.0.0.1'),
        'PORT': os.environ.get('DATABASE_PORT', '5432'),
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


# Internationalization
# https://docs.djangoproject.com/en/3.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.0/howto/static-files/

STATIC_URL = '/static/'

PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_ROOT = os.path.join(PROJECT_DIR, 'static')
#
# Django REST Framework
# =================================================================================================
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
        'rest_framework.authentication.BasicAuthentication',
        # 'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.LimitOffsetPagination',
    'PAGE_SIZE': 100
}

AUTH_USER_MODEL = 'accounts.User'

#
# Square Client Credentials
# =================================================================================================
SQUARE_CLIENT = SqClient(
    access_token=os.environ.get('SQUARE_ACCESS_TOKEN'),
    environment=os.environ.get('SQUARE_ENVIRONMENT', 'sandbox'),
)

#
# Smarty Streets Credentials
# =================================================================================================
smarty_credentials = StaticCredentials(
    os.environ.get('SMARTYSTREETS_AUTH_ID'),
    os.environ.get('SMARTYSTREETS_AUTH_TOKEN'),
)

SMARTYSTREETS_ZIP_CLIENT = ClientBuilder(smarty_credentials).build_us_zipcode_api_client()
SMARTYSTREETS_AUTO_COMPLETE_CLIENT = ClientBuilder(smarty_credentials).build_us_autocomplete_api_client()

USE_S3 = (os.getenv("USE_S3", False) == 'true')
if USE_S3:
    # aws settings
    AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
    AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')
    AWS_STORAGE_BUCKET_NAME = os.environ.get('AWS_STORAGE_BUCKET_NAME')

    AWS_DEFAULT_ACL = None
    AWS_S3_CUSTOM_DOMAIN = f'{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com'
    AWS_S3_OBJECT_PARAMETERS = {'CacheControl': 'max-age=86400'}
    # s3 static settings
    STATIC_LOCATION = 'static'
    STATIC_URL = f'https://{AWS_S3_CUSTOM_DOMAIN}/{STATIC_LOCATION}/'
    STATICFILES_STORAGE = 'core.storage_backends.StaticStorage'
    # s3 public media settings
    PUBLIC_MEDIA_LOCATION = 'media'
    MEDIA_URL = f'https://{AWS_S3_CUSTOM_DOMAIN}/{PUBLIC_MEDIA_LOCATION}/'
    DEFAULT_FILE_STORAGE = 'core.storage_backends.PublicMediaStorage'
    # s3 private media settings
    PRIVATE_MEDIA_LOCATION = 'private'
    PRIVATE_FILE_STORAGE = 'core.storage_backends.PrivateMediaStorage'
    AWS_S3_SIGNATURE_VERSION = "s3v4"
    AWS_S3_REGION_NAME = "us-east-2"


STATICFILES_DIRS = (os.path.join(BASE_DIR, 'static'),)
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_UNIQUE_EMAIL = True
ACCOUNT_EMAIL_VERIFICATION = 'optional'
ACCOUNT_CONFIRM_EMAIL_ON_GET = True
ACCOUNT_EMAIL_CONFIRMATION_ANONYMOUS_REDIRECT_URL = '/signin'
ACCOUNT_EMAIL_CONFIRMATION_AUTHENTICATED_REDIRECT_URL = '/'
ACCOUNT_ADAPTER = 'accounts.adapter.CustomAllauthAdapter'

SITE_ID = 1

if (os.getenv("ENV", False) == 'production'):
    EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
    EMAIL_HOST = os.environ.get('EMAIL_HOST')
    EMAIL_PORT = 587
    EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER')
    EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD')
    EMAIL_USE_TLS = True
else:
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

REST_AUTH_REGISTER_SERIALIZERS = {
    'REGISTER_SERIALIZER': 'accounts.serializers.RegisterSerializer',
}

REST_AUTH_SERIALIZERS = {
    'LOGIN_SERIALIZER': 'accounts.serializers.UWLoginSerializer',
}

DEFAULT_FROM_EMAIL = 'info@unitedworldlogistics.com'

TEAPLIX_API = TeaplixAPI(
    token=os.environ.get('TEAPPLIX_API_TOKEN'),
    api_url="https://api.teapplix.com/api2/",
)
