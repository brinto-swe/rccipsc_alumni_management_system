"""Base Django settings shared by all environments."""

from datetime import timedelta
from pathlib import Path

from decouple import Csv, config
from django.core.exceptions import ImproperlyConfigured


BASE_DIR = Path(__file__).resolve().parents[2]


def env_bool(name: str, default: bool = False) -> bool:
    value = config(name, default=str(default))
    if isinstance(value, bool):
        return value
    normalized = str(value).strip().lower()
    truthy = {"1", "true", "t", "yes", "y", "on", "debug", "local", "development"}
    falsy = {"0", "false", "f", "no", "n", "off", "release", "prod", "production"}
    if normalized in truthy:
        return True
    if normalized in falsy:
        return False
    return default


SECRET_KEY = config("SECRET_KEY")
DEBUG = env_bool("DEBUG", default=False)

ALLOWED_HOSTS = config("ALLOWED_HOSTS", default="127.0.0.1,localhost,.vercel.app", cast=Csv())
CSRF_TRUSTED_ORIGINS = config("CSRF_TRUSTED_ORIGINS", default="", cast=Csv())
CORS_ALLOWED_ORIGINS = config("CORS_ALLOWED_ORIGINS", default="", cast=Csv())
CORS_ALLOW_ALL_ORIGINS = env_bool("CORS_ALLOW_ALL_ORIGINS", default=DEBUG)
USE_CLOUDINARY = env_bool("USE_CLOUDINARY", default=False)

DJANGO_APPS = [
    "whitenoise.runserver_nostatic",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.humanize",
    "django.contrib.postgres",
]

THIRD_PARTY_APPS = [
    "corsheaders",
    "rest_framework",
    "rest_framework.authtoken",
    "rest_framework_simplejwt.token_blacklist",
    "drf_spectacular",
    "django_filters",
    "djoser",
    "cloudinary",
]

if USE_CLOUDINARY:
    THIRD_PARTY_APPS.append("cloudinary_storage")

LOCAL_APPS = [
    "common",
    "accounts",
    "users",
    "profiles",
    "professions",
    "directory",
    "events",
    "posts",
    "clubs",
    "teams",
    "announcements",
    "mentorships",
    "notifications",
    "analytics",
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"
WSGI_APPLICATION = "config.wsgi.app"
ASGI_APPLICATION = "config.asgi.application"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    }
]

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": config("DB_NAME"),
        "USER": config("DB_USER"),
        "PASSWORD": config("DB_PASSWORD"),
        "HOST": config("DB_HOST", default="127.0.0.1"),
        "PORT": config("DB_PORT", default="5432"),
        "CONN_MAX_AGE": config("DB_CONN_MAX_AGE", default=60, cast=int),
        "OPTIONS": {
            "sslmode": config("DB_SSL_MODE", default="prefer"),
        },
    }
}


AUTH_USER_MODEL = "users.User"
AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
]

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
        "OPTIONS": {"min_length": 8},
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

LANGUAGE_CODE = "en-us"
TIME_ZONE = config("TIME_ZONE", default="UTC")
USE_I18N = True
USE_TZ = True

STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
STATICFILES_STORAGE = "whitenoise.storage.CompressedStaticFilesStorage"

CLOUDINARY_STORAGE = {}

if USE_CLOUDINARY:
    cloudinary_url = config("CLOUDINARY_URL", default="")
    cloudinary_cloud_name = config("CLOUDINARY_CLOUD_NAME", default="")
    cloudinary_api_key = config("CLOUDINARY_API_KEY", default="")
    cloudinary_api_secret = config("CLOUDINARY_API_SECRET", default="")

    if not cloudinary_url and not all(
        [cloudinary_cloud_name, cloudinary_api_key, cloudinary_api_secret]
    ):
        raise ImproperlyConfigured(
            "Cloudinary is enabled but credentials are missing. Set CLOUDINARY_URL or "
            "CLOUDINARY_CLOUD_NAME, CLOUDINARY_API_KEY, and CLOUDINARY_API_SECRET."
        )

    CLOUDINARY_STORAGE = {
        "SECURE": env_bool("CLOUDINARY_SECURE", default=True),
        "MEDIA_TAG": config("CLOUDINARY_MEDIA_TAG", default="media"),
        "PREFIX": config("CLOUDINARY_PREFIX", default="media/"),
    }
    if all([cloudinary_cloud_name, cloudinary_api_key, cloudinary_api_secret]):
        CLOUDINARY_STORAGE.update(
            {
                "CLOUD_NAME": cloudinary_cloud_name,
                "API_KEY": cloudinary_api_key,
                "API_SECRET": cloudinary_api_secret,
            }
        )

    STORAGES = {
        "default": {
            "BACKEND": "cloudinary_storage.storage.MediaCloudinaryStorage",
        },
        "staticfiles": {
            "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
        },
    }
else:
    STORAGES = {
        "default": {
            "BACKEND": "django.core.files.storage.FileSystemStorage",
        },
        "staticfiles": {
            "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
        },
    }

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": (
        "rest_framework.permissions.IsAuthenticated",
    ),
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    "DEFAULT_FILTER_BACKENDS": (
        "django_filters.rest_framework.DjangoFilterBackend",
        "rest_framework.filters.SearchFilter",
        "rest_framework.filters.OrderingFilter",
    ),
    "DEFAULT_PAGINATION_CLASS": "common.pagination.DefaultPageNumberPagination",
    "PAGE_SIZE": config("API_PAGE_SIZE", default=20, cast=int),
    "DEFAULT_THROTTLE_CLASSES": (
        "rest_framework.throttling.AnonRateThrottle",
        "rest_framework.throttling.UserRateThrottle",
        "rest_framework.throttling.ScopedRateThrottle",
    ),
    "DEFAULT_THROTTLE_RATES": {
        "anon": config("THROTTLE_ANON", default="60/hour"),
        "user": config("THROTTLE_USER", default="600/hour"),
        "auth": config("THROTTLE_AUTH", default="10/minute"),
        "sensitive": config("THROTTLE_SENSITIVE", default="20/hour"),
    },
}

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(
        minutes=config("ACCESS_TOKEN_LIFETIME_MINUTES", cast=int, default=30)
    ),
    "REFRESH_TOKEN_LIFETIME": timedelta(
        days=config("REFRESH_TOKEN_LIFETIME_DAYS", cast=int, default=7)
    ),
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": True,
    "UPDATE_LAST_LOGIN": True,
    "ALGORITHM": "HS256",
    "SIGNING_KEY": SECRET_KEY,
    "AUTH_HEADER_TYPES": ("Bearer",),
    "AUTH_TOKEN_CLASSES": ("rest_framework_simplejwt.tokens.AccessToken",),
}

DJOSER = {
    "LOGIN_FIELD": "email",
    "USER_CREATE_PASSWORD_RETYPE": True,
    "SET_PASSWORD_RETYPE": True,
    "PASSWORD_RESET_CONFIRM_RETYPE": True,
    "PASSWORD_RESET_SHOW_EMAIL_NOT_FOUND": False,
    "SEND_ACTIVATION_EMAIL": env_bool("DJOSER_SEND_ACTIVATION_EMAIL", default=True),
    "SEND_CONFIRMATION_EMAIL": env_bool("DJOSER_SEND_CONFIRMATION_EMAIL", default=True),
    "ACTIVATION_URL": config(
        "DJOSER_ACTIVATION_URL",
        default="auth/activate/{uid}/{token}",
    ),
    "PASSWORD_RESET_CONFIRM_URL": config(
        "DJOSER_PASSWORD_RESET_CONFIRM_URL",
        default="auth/password/reset/confirm/{uid}/{token}",
    ),
    "USERNAME_CHANGED_EMAIL_CONFIRMATION": True,
    "TOKEN_MODEL": None,
    "SERIALIZERS": {
        "user_create": "accounts.serializers.AccountRegistrationSerializer",
        "user": "users.serializers.UserDetailSerializer",
        "current_user": "users.serializers.UserDetailSerializer",
    },
}

SPECTACULAR_SETTINGS = {
    "TITLE": "RCCIPSC Alumni Management API",
    "DESCRIPTION": (
        "Production-minded alumni management backend with role-aware APIs, "
        "JWT auth, profile privacy, events, social feed, mentorship, and notifications."
    ),
    "VERSION": "1.0.0",
    "SERVE_INCLUDE_SCHEMA": False,
    "COMPONENT_SPLIT_REQUEST": True,
    "SWAGGER_UI_SETTINGS": {"persistAuthorization": True},
    "TAGS": [
        {"name": "Auth", "description": "Authentication and account endpoints"},
        {"name": "Users", "description": "User administration"},
        {"name": "Profiles", "description": "Profile and profession management"},
        {"name": "Directory", "description": "Alumni directory and discovery"},
        {"name": "Events", "description": "Event lifecycle and registrations"},
        {"name": "Posts", "description": "Social feed and moderation"},
        {"name": "Clubs", "description": "Club management and memberships"},
        {"name": "Teams", "description": "Team management and sports participation"},
        {"name": "Announcements", "description": "News and notice publishing"},
        {"name": "Mentorship", "description": "Mentor workflows and sessions"},
        {"name": "Notifications", "description": "In-app and email notifications"},
        {"name": "Analytics", "description": "Operational analytics"},
        {"name": "System", "description": "Health and platform metadata"},
    ],
}

EMAIL_BACKEND = config(
    "EMAIL_BACKEND",
    default="django.core.mail.backends.console.EmailBackend",
)
EMAIL_HOST = config("EMAIL_HOST", default="")
EMAIL_PORT = config("EMAIL_PORT", default=587, cast=int)
EMAIL_USE_TLS = env_bool("EMAIL_USE_TLS", default=True)
EMAIL_HOST_USER = config("EMAIL_HOST_USER", default="")
EMAIL_HOST_PASSWORD = config("EMAIL_HOST_PASSWORD", default="")
DEFAULT_FROM_EMAIL = config("DEFAULT_FROM_EMAIL", default="no-reply@example.com")

FRONTEND_URL = config("FRONTEND_URL", default="http://localhost:3000")
DEFAULT_DOMAIN = config("DEFAULT_DOMAIN", default="localhost")
SITE_NAME = config("SITE_NAME", default="RCCIPSC Alumni")

SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = "DENY"
SESSION_COOKIE_HTTPONLY = True
CSRF_COOKIE_HTTPONLY = False
SESSION_COOKIE_SAMESITE = "Lax"
CSRF_COOKIE_SAMESITE = "Lax"

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "[{asctime}] {levelname} {name} {message}",
            "style": "{",
        },
        "simple": {
            "format": "{levelname} {message}",
            "style": "{",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "verbose",
        }
    },
    "root": {
        "handlers": ["console"],
        "level": config("LOG_LEVEL", default="INFO"),
    },
}
