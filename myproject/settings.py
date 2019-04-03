
import os

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'y-qmn=e5t89m7t4=^%hv+1x&21y)c2mjibrx!xsma9&(#7@duv'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # custom
    "boats.apps.BoatsConfig",
    "articles.apps.ArticlesConfig",
    #3rd party
    "bootstrap4",
    "django_cleanup",
    "easy_thumbnails",
    "captcha",
    "social_django"




]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

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

            ],
        },
    },
]

WSGI_APPLICATION = 'myproject.wsgi.application'


# Database
# https://docs.djangoproject.com/en/2.1/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}


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

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Europe/Moscow'

USE_I18N = True

USE_L10N = True

USE_TZ = True

SHORT_DATE_FORMAT = "j.m.Y"


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.1/howto/static-files/

STATIC_URL = '/static/'
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, "static"), ] #new
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
            "size": (96, 96),
            "crop": "scale",
        },
    },
}
THUMBNAIL_BASEDIR = "thumbnails"

# аутентификация через соц. сети

AUTHENTICATION_BACKENDS = (
    "social_core.backends.vk.VKOAuth2",
    "django.contrib.auth.backends.ModelBackend"
)
SOCIAL_AUTH_URL_NAMESPACE = 'social' #  new

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


# в контактике
SOCIAL_AUTH_VK_OAUTH2_KEY = "6925818"
SOCIAL_AUTH_VK_OAUTH2_SECRET = "8Nw5zHZmFk8hwEFWwRDP"
SOCIAL_AUTH_VK_OAUTH2_SCOPE = ["email"]
SOCIAL_AUTH_VK_APP_USER_MODE = 2

