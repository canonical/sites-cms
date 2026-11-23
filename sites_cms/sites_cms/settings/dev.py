"""Local development. Safe defaults, so no .env file is needed."""

from sites_cms.env import database_from_url, env_str

from .base import *

DEBUG = True
SECRET_KEY = "local-development-only-not-a-secret"
ALLOWED_HOSTS = ["*"]

DATABASES = {
    "default": database_from_url(env_str("DATABASE_URL", LOCAL_DATABASE_URL))
}

# Emails are printed in the terminal that runs the server.
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

# `admin` / `admin` is fine on a laptop.
AUTH_PASSWORD_VALIDATORS = []
