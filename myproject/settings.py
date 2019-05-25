import sys
import os
from reversion.middleware import RevisionMiddleware

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'y-qmn=e5t89m7t4=^%hv+1x&21y)c2mjibrx!xsma9&(#7@duv'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ["127.0.0.1", 'localhost', 'testserver']  # new, old = []


# Application definition

INSTALLED_APPS = [
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

]


FORM_RENDERER = 'django.forms.renderers.TemplatesSetting'  # for django.forms


MIDDLEWARE = [
    'debug_toolbar.middleware.DebugToolbarMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',  # new
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'social_django.middleware.SocialAuthExceptionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'reversion.middleware.RevisionMiddleware',  # for django reversion # new
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
    "test": {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3')},
}

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
STATIC_ROOT = os.path.join(BASE_DIR, "static")  # new
STATIC_URL = '/static/'
#STATICFILES_DIRS = [
    #os.path.join(BASE_DIR, "static"), ]

#  Настройка подсистемы обработки выгруженных файлов
MEDIA_ROOT = os.path.join(BASE_DIR, "media")
MEDIA_URL = "/media/"

# кастомная модель пользователя
AUTH_USER_MODEL = "boats.ExtraUser"

# система разграничения доступа
LOGIN_URL = "boats:login"  # works
LOGIN_REDIRECT_URL = "boats:user_profile"  # works
LOGOUT_REDIRECT_URL = None  # см. стр 289
PASSWORD_RESET_TIMEOUT_DAYS = 1

# настройки SMTP для отправки почты
EMAIL_HOST = 'smtp.mail.ru'
EMAIL_PORT = 465
EMAIL_USE_SSL = True
EMAIL_HOST_USER = 'hardcase@inbox.ru'
EMAIL_HOST_PASSWORD = 'sosihui56842'

#  https://vivazzi.pro/it/sender-address-must-match-authenticated-user/
# Error: SMTPRecipientsRefused 501  решение вопроса

SERVER_EMAIL = EMAIL_HOST_USER
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER


THUMBNAIL_ALIASES = {
    "": {
        "default": {
            "size": (180, 180),  # 0, 180
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
THUMBNAIL_BASEDIR = "thumbnails"
THUMBNAIL_MEDIA_URL = MEDIA_URL
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
SOCIAL_AUTH_STRATEGY = 'social_django.strategy.DjangoStrategy'  # new
SOCIAL_AUTH_STORAGE = 'social_django.models.DjangoStorage'  # new

# в контактике
SOCIAL_AUTH_VK_OAUTH2_KEY = "6925818"
SOCIAL_AUTH_VK_OAUTH2_SECRET = "8Nw5zHZmFk8hwEFWwRDP"
SOCIAL_AUTH_VK_OAUTH2_SCOPE = ["email"]
SOCIAL_AUTH_VK_APP_USER_MODE = 2

# facebook
FACEBOOK_APP_ID = '2404075233157649'
FACEBOOK_API_SECRET = '2497d23a765f90fed8fab81c13ad2f9a'
SOCIAL_AUTH_FACEBOOK_KEY = '2404075233157649'  # new
SOCIAL_AUTH_FACEBOOK_SECRET = '2497d23a765f90fed8fab81c13ad2f9a' # new
SOCIAL_AUTH_FACEBOOK_SCOPE = ['email']
SOCIAL_AUTH_FACEBOOK_PROFILE_EXTRA_PARAMS = {
            'fields': 'id,name,email',
            }
SOCIAL_AUTH_ADMIN_USER_SEARCH_FIELDS = ['username', 'first_name', 'email']


#   всплывающие сообщения django messaging framework
if DEBUG: MESSAGE_LEVEL = 0
else: MESSAGE_LEVEL = 20

# crispy forms
CRISPY_TEMPLATE_PACK = 'bootstrap4'

# настройки для дебагера
# https://django-debug-toolbar.readthedocs.io/en/latest/installation.html
if DEBUG: INTERNAL_IPS = "127.0.0.1"

# for file resubmit


CACHES = {

    #'default': {
        #'BACKEND': 'django.core.cache.backends.locmem.LocMemCache', },
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://127.0.0.1:6379/1",
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
CELERY_BROKER_URL = 'redis://localhost:6379'
CELERY_ACCEPT_CONTENT = ['application/json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = TIME_ZONE
# celery -A myproject worker --pool=solo -l info для запуска воркера под винду
#celery -A myproject beat -для запуска задач по рассписанию



