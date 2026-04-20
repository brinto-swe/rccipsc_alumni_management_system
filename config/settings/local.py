"""Local development settings."""

from .base import *  # noqa: F403,F401


DEBUG = env_bool("DEBUG", default=True)  # noqa: F405

EMAIL_BACKEND = config(  # type: ignore[name-defined]  # noqa: F405
    "EMAIL_BACKEND",
    default="django.core.mail.backends.console.EmailBackend",
)
