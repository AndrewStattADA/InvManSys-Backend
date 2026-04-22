import os
from pathlib import Path
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()
# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
# On Render, set the SECRET_KEY environment variable.
SECRET_KEY = os.environ.get("SECRET_KEY", "django-insecure-j(9u-k*y_^szd423t%81=9p2kyoz1@vv56&1*l992($%2f5af9")

# SECURITY WARNING: don't run with debug turned on in production!
# DEBUG will be True in Codespaces/Local, and False on Render.
DEBUG = 'RENDER' not in os.environ
# DEBUG = True

ALLOWED_HOSTS = ['.github.dev', '.app.github.dev', 'localhost', '127.0.0.1']

# Add Render's dynamic hostname to ALLOWED_HOSTS
render_external_hostname = os.environ.get('RENDER_EXTERNAL_HOSTNAME')
if render_external_hostname:
    ALLOWED_HOSTS.append(render_external_hostname)


# Application definition
INSTALLED_APPS = [
    "django.contrib.admin",
    "corsheaders",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "rest_framework_simplejwt", 
    "inventory_api",
]

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",  # Required for serving static files on Render
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "backend_core.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "backend_core.wsgi.application"


# Database
# https://docs.djangoproject.com/en/6.0/ref/settings/#databases
# Note: SQLite data resets on Render Free Tier every restart.
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}


# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]


# Internationalization
LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True


# Static files (CSS, JavaScript, Images)
STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

# Use WhiteNoise to serve compressed static files
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"


# CORS & CSRF Settings
# Keep your Codespace origins
CORS_ALLOWED_ORIGINS = [
    "https://fluffy-chainsaw-x5pw9x6r6r64hvgvq-5173.app.github.dev",
    "https://invmansys-frontend.onrender.com",
]

CSRF_TRUSTED_ORIGINS = [
    "https://fluffy-chainsaw-x5pw9x6r6r64hvgvq-5173.app.github.dev",
]

# Allow all origins on Render for easier testing between services
if not DEBUG:
    CORS_ALLOW_ALL_ORIGINS = True
    # Once you have your Render Frontend URL, it's better to add it to CORS_ALLOWED_ORIGINS 
    # and set CORS_ALLOW_ALL_ORIGINS = False


CORS_ALLOWED_ORIGIN_REGEXES = [
    r"^https:\/\/.*-3000\.app\.github\.dev$",
]


# Django Rest Framework
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
}


# JWT Settings

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),
    'SLIDING_TOKEN_REFRESH_LIFETIME': timedelta(days=1),
    'ROTATE_REFRESH_TOKENS': False,
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY, # This uses the key from line 10
    'AUTH_HEADER_TYPES': ('Bearer',),
    'UPDATE_LAST_LOGIN': False, 
}


SENDGRID_API_KEY = os.environ.get('SENDGRID_API_KEY')
DEFAULT_FROM_EMAIL = 'mydogisollie@gmail.com'
FRONTEND_URL = os.environ.get('FRONTEND_URL', 'https://fluffy-chainsaw-x5pw9x6r6r64hvgvq-5173.app.github.dev')


DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"