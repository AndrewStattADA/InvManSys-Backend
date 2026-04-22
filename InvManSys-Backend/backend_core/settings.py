import os
from pathlib import Path
from datetime import timedelta
from dotenv import load_dotenv

# --- ENVIRONMENT LOADING ---
# Load variables from a .env file (useful for local development)
load_dotenv()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# --- SECURITY ---
# Secret key is pulled from environment variables for security; uses a fallback for local dev
SECRET_KEY = os.environ.get("SECRET_KEY", "django-insecure-j(9u-k*y_^szd423t%81=9p2kyoz1@vv56&1*l992($%2f5af9")

# Automatically toggle DEBUG mode based on the environment (Off on Render, On elsewhere)
DEBUG = 'RENDER' not in os.environ

# Defines which domain names this Django site can serve
ALLOWED_HOSTS = ['.github.dev', '.app.github.dev', 'localhost', '127.0.0.1']

# Dynamically add Render's URL to allowed hosts if running in that environment
render_external_hostname = os.environ.get('RENDER_EXTERNAL_HOSTNAME')
if render_external_hostname:
    ALLOWED_HOSTS.append(render_external_hostname)


# --- APPLICATION DEFINITION ---
INSTALLED_APPS = [
    "django.contrib.admin",
    "corsheaders",  # Handles Cross-Origin Resource Sharing
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",           # Django REST Framework core
    "rest_framework_simplejwt",  # JWT Authentication plugin
    "inventory_api",             # Your custom application
]

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware", # Must be at the top to handle CORS requests
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",  # Optimizes static file serving for production
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


# --- DATABASE ---
# Currently using SQLite. Note: Data is volatile on Render's free tier.
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}


# --- PASSWORD VALIDATION ---
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]


# --- INTERNATIONALIZATION ---
LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True


# --- STATIC FILES ---
STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

# Use WhiteNoise to serve compressed/cached static files in production
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"


# --- CORS & CSRF SETTINGS ---
# Explicitly allowed origins for frontend communication
CORS_ALLOWED_ORIGINS = [
    "https://fluffy-chainsaw-x5pw9x6r6r64hvgvq-5173.app.github.dev",
    "https://invmansys-frontend.onrender.com",
]

# Trusted origins for CSRF protection (required for POST requests from specific domains)
CSRF_TRUSTED_ORIGINS = [
    "https://fluffy-chainsaw-x5pw9x6r6r64hvgvq-5173.app.github.dev",
]

# In production (non-DEBUG), allow all origins to prevent connectivity issues during testing
if not DEBUG:
    CORS_ALLOW_ALL_ORIGINS = True

# Allows dynamic hostnames from GitHub Codespaces
CORS_ALLOWED_ORIGIN_REGEXES = [
    r"^https:\/\/.*-3000\.app\.github\.dev$",
]


# --- DJANGO REST FRAMEWORK SETTINGS ---
REST_FRAMEWORK = {
    # Sets JWT as the primary method for identifying users
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    # By default, all API endpoints require a valid login
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
}


# --- JWT (JSON WEB TOKEN) CONFIGURATION ---
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60), # Access expires in 1 hour
    'SLIDING_TOKEN_REFRESH_LIFETIME': timedelta(days=1),
    'ROTATE_REFRESH_TOKENS': False,
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
    'AUTH_HEADER_TYPES': ('Bearer',), # Format: "Authorization: Bearer <token>"
    'UPDATE_LAST_LOGIN': False, 
}

# --- EMAIL & EXTERNAL SERVICES ---
SENDGRID_API_KEY = os.environ.get('SENDGRID_API_KEY')
DEFAULT_FROM_EMAIL = 'mydogisollie@gmail.com'
# The URL used for password reset links sent to users
FRONTEND_URL = os.environ.get('FRONTEND_URL', 'https://fluffy-chainsaw-x5pw9x6r6r64hvgvq-5173.app.github.dev')

# Default primary key field type
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"