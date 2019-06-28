import sys
import os
from reversion.middleware import RevisionMiddleware
import django_heroku
from dotenv import load_dotenv
load_dotenv()

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv("SECRET_KEY")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

ALLOWED_HOSTS = ["boatsproject-eu.herokuapp.com", '127.0.0.1']


# Application definition

INSTALLED_APPS = [
    #'whitenoise.runserver_nostatic',  # new http://whitenoise.evans.io/en/stable/django.html
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    "django.forms",  # for a custom widgets
    # custom
    "boats.apps.BoatsConfig",
    "articles.apps.ArticlesConfig",
    "testapp.apps.TestappConfig",
    # 3rd party
    "captcha",
    "bootstrap4",
    "django_cleanup",
    "easy_thumbnails",
    "social_django",
    "extra_views",
    "debug_toolbar",
    "reversion",
    "dynamic_validator",
    "django_countries",
    "xhtml2pdf",
    "file_resubmit",
    "django_extensions",
    'fancy_cache',


]


FORM_RENDERER = 'django.forms.renderers.TemplatesSetting'  # for django.forms


MIDDLEWARE = [

    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware', # new
    'debug_toolbar.middleware.DebugToolbarMiddleware',  # перенесенос первой позиции на третью
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',  # new (для переводчика)
    "django.middleware.http.ConditionalGetMiddleware",  # new
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'social_django.middleware.SocialAuthExceptionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'reversion.middleware.RevisionMiddleware',  # for django reversion
]

RevisionMiddleware.atomic = True  # new  Для reversion middleware https://django-reversion.readthedocs.io/en/stable/middleware.html

ROOT_URLCONF = 'myproject.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')]
        ,
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                "social_django.context_processors.backends",
                "social_django.context_processors.login_redirect",
                "articles.middlewares.articles_context_processor",  # для articles

            ],
        },
    },
]

WSGI_APPLICATION = 'myproject.wsgi.application'


# Database
# https://docs.djangoproject.com/en/2.1/ref/settings/#databases

DATABASES = {
    'default': {
        "ENGINE": "django.db.backends.postgresql",
        "HOST": "localhost",
        "USER": "postgres",
        "PASSWORD": "1q2w3e",
        "NAME": "postgres_work_1"},
    " test_test": {  # тестовая БД
        "ENGINE": "django.db.backends.postgresql",
        "HOST": "localhost",
        "USER": "postgres",
        "PASSWORD": "1q2w3e",
        "NAME": "testdb",
        'TEST': {
        'NAME': 'auto_tests', }
    },
}

#Postgree:   по ходу это юзернейм
#password - 1q2w3e
#port- 5432

#if 'test' in sys.argv or 'test_coverage' in sys.argv: #Covers regular testing and django-coverage
    #DATABASES['default']['ENGINE'] = 'django.db.backends.sqlite3'

# Password validation
# https://docs.djangoproject.com/en/2.1/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/2.1/topics/i18n/

LANGUAGE_CODE = "en-us"
LANGUAGES = (
    ('ru', 'Russian'),
    ('en-us', 'English'),
)
LOCALE_PATHS = (
    'locale',
    #os.path.join(BASE_DIR, 'locale'),
)


USE_I18N = True

USE_L10N = True

USE_TZ = False  # new

TIME_ZONE = 'Europe/Moscow'

SHORT_DATE_FORMAT = "j.m.Y"


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.1/howto/static-files/
STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")
STATIC_URL = '/static/'


#  Настройка подсистемы обработки выгруженных файлов
MEDIA_ROOT = os.path.join(BASE_DIR, "media")
MEDIA_URL = "/media/"

# кастомная модель пользователя
AUTH_USER_MODEL = "boats.ExtraUser"

# система разграничения доступа
LOGIN_URL = "boats:login"
LOGIN_REDIRECT_URL = "boats:user_profile"  # works
LOGOUT_REDIRECT_URL = None  # см. стр 289
PASSWORD_RESET_TIMEOUT_DAYS = 1

# настройки SMTP для отправки почты
EMAIL_HOST = 'smtp.mail.ru'
EMAIL_PORT = 465
EMAIL_USE_SSL = True
EMAIL_HOST_USER = 'hardcase@inbox.ru'
EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD")

#  https://vivazzi.pro/it/sender-address-must-match-authenticated-user/
# Error: SMTPRecipientsRefused 501  решение вопроса

SERVER_EMAIL = EMAIL_HOST_USER
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER
EMAIL_USE_LOCALTIME = True

THUMBNAIL_ALIASES = {
    "": {
        "default": {
            "size": (180, 180),
            "crop": "smart",
            "autocrop": True,
            "bw": False,
            "quality": 100,
            "subsampling": 1, },
        "small": {
            "size": (115, 0),
            "crop": "smart",
            "autocrop": True,
            "bw": False,
            "quality": 100,
            "subsampling": 1, },
        "medium": {
            "size": (135, 135),
            "crop": "smart",
            "autocrop": True,
            "bw": False,
            "quality": 100,
            "subsampling": 1, },

    },
}
# https://easy-thumbnails.readthedocs.io/en/2.1/ref/settings/#easy_thumbnails.conf.Settings.THUMBNAIL_CACHE_DIMENSIONS
THUMBNAIL_CACHE_DIMENSIONS = True

# аутентификация через соц. сети
AUTHENTICATION_BACKENDS = (
    'social_core.backends.facebook.FacebookOAuth2',
    "social_core.backends.vk.VKOAuth2",
    "django.contrib.auth.backends.ModelBackend"
)
SOCIAL_AUTH_URL_NAMESPACE = 'social'

SOCIAL_AUTH_PIPELINE = (
    'social_core.pipeline.social_auth.social_details',
    'social_core.pipeline.social_auth.social_uid',
    'social_core.pipeline.social_auth.auth_allowed',
    'social_core.pipeline.social_auth.social_user',
    'social_core.pipeline.user.get_username',
    'social_core.pipeline.social_auth.associate_by_email',  # <--- enable this one
    'social_core.pipeline.user.create_user',
    'social_core.pipeline.social_auth.associate_user',
    'social_core.pipeline.social_auth.load_extra_data',
    'social_core.pipeline.user.user_details',
)

SOCIAL_AUTH_STRATEGY = 'social_django.strategy.DjangoStrategy'
SOCIAL_AUTH_STORAGE = 'social_django.models.DjangoStorage'

# в контактике
SOCIAL_AUTH_VK_OAUTH2_KEY = os.getenv("SOCIAL_AUTH_VK_OAUTH2_KEY")
SOCIAL_AUTH_VK_OAUTH2_SECRET = os.getenv("SOCIAL_AUTH_VK_OAUTH2_SECRET")
SOCIAL_AUTH_VK_OAUTH2_SCOPE = ["email"]
SOCIAL_AUTH_VK_APP_USER_MODE = 2

# facebook
FACEBOOK_APP_ID = os.getenv("FACEBOOK_APP_ID")
FACEBOOK_API_SECRET = os.getenv("FACEBOOK_API_SECRET")
SOCIAL_AUTH_FACEBOOK_KEY = os.getenv("SOCIAL_AUTH_FACEBOOK_KEY")
SOCIAL_AUTH_FACEBOOK_SECRET = os.getenv("SOCIAL_AUTH_FACEBOOK_SECRET")
SOCIAL_AUTH_FACEBOOK_SCOPE = ['email']
SOCIAL_AUTH_FACEBOOK_PROFILE_EXTRA_PARAMS = {
            'fields': 'id,name,email',
            }

SOCIAL_AUTH_ADMIN_USER_SEARCH_FIELDS = ['username', 'first_name', 'email']


#   всплывающие сообщения django messaging framework
if DEBUG: MESSAGE_LEVEL = 0
else: MESSAGE_LEVEL = 20


# настройки для дебагера
# https://django-debug-toolbar.readthedocs.io/en/latest/installation.html
if DEBUG: INTERNAL_IPS = "127.0.0.1"

# for file resubmit


CACHES = {
    #'default': {
        #'BACKEND': 'django.core.cache.backends.locmem.LocMemCache', },
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": os.environ.get('REDIS_URL'),
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        }
    },
    "file_resubmit": {
        'BACKEND': 'django.core.cache.backends.filebased.FileBasedCache',
        "LOCATION": os.path.join(BASE_DIR, 'data/cache/file_resubmit')},
}

# REDIS related settings
REDIS_HOST = 'localhost'
REDIS_PORT = '6379'
BROKER_URL = 'redis://' + REDIS_HOST + ':' + REDIS_PORT + '/0'
BROKER_TRANSPORT_OPTIONS = {'visibility_timeout': 3600}
CELERY_RESULT_BACKEND = 'redis://' + REDIS_HOST + ':' + REDIS_PORT + '/0'
# время жизни кеша (15 минут)
CACHE_TTL = 60*15

# CELERY related settings
CELERY_BROKER_URL = os.environ.get('REDIS_URL')
CELERY_ACCEPT_CONTENT = ['application/json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = TIME_ZONE
# celery -A myproject worker --pool=solo -l info для запуска воркера под винду
# celery -A myproject beat -для запуска задач по рассписанию


#  whitenoise
#  http://whitenoise.evans.io/en/stable/index.html
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'


#  https://devcenter.heroku.com/articles/django-app-configuration
django_heroku.settings(locals()) #  new

ADMINS = ("hardcase@inbox.ru", )

#  https://webdevblog.ru/uluchshenie-bezopasnosti-sajta-django-s-pomoshhju-zagolovkov-zaprosov/
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True
X_FRAME_OPTIONS = "DENY"

# Heroku: Update database configuration from $DATABASE_URL.
import dj_database_url
db_from_env = dj_database_url.config(conn_max_age=500, ssl_require=True)
DATABASES['default'].update(db_from_env)


#  logging  heroku logs --source app --tail логи джанги в heroku
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': os.getenv('DJANGO_LOG_LEVEL', 'ERROR'),
        },
    },
}
#  настройки AWS, django-storages
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")

AWS_STORAGE_BUCKET_NAME = 'boatsprojectdevelopmentbucket'
AWS_S3_HOST = "s3.eu-central-1.amazonaws.com"
S3_USE_SIGV4 = True
AWS_S3_REGION_NAME = "eu-central-1"

AWS_QUERYSTRING_EXPIRE = 60*60*24  # new
AWS_IS_GZIPPED = True

#STATICFILES_STORAGE = 'storages.backends.s3boto.S3BotoStorage'
DEFAULT_FILE_STORAGE = 'storages.backends.s3boto.S3BotoStorage'

#STATIC_URL = 'http://' + AWS_STORAGE_BUCKET_NAME + '.s3.amazonaws.com/'
#ADMIN_MEDIA_PREFIX = STATIC_URL + 'admin/'
MEDIA_URL = 'http://' + AWS_STORAGE_BUCKET_NAME + AWS_S3_HOST + "/"

# django-BOTO settings https://github.com/qnub/django-boto
BOTO_S3_BUCKET = AWS_STORAGE_BUCKET_NAME
BOTO_S3_HOST = AWS_S3_HOST
BOTO_BUCKET_LOCATION = AWS_S3_REGION_NAME

#  настройки easy thumbnails для  работы с heroku
THUMBNAIL_DEFAULT_STORAGE = DEFAULT_FILE_STORAGE
THUMBNAIL_BASEDIR = "thumbnails"
THUMBNAIL_MEDIA_URL = MEDIA_URL

#  Django fancy cache
FANCY_REMEMBER_ALL_URLS = True
FANCY_REMEMBER_STATS_ALL_URLS = True
