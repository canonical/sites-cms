"""Used by pytest locally and in CI."""

import tempfile

from sites_cms.env import database_from_url, env_str

from .base import *

DEBUG = False
SECRET_KEY = "test-only-not-a-secret"
ALLOWED_HOSTS = ["testserver", "localhost"]

DATABASES = {
    "default": database_from_url(env_str("DATABASE_URL", LOCAL_DATABASE_URL))
}

# The slow, safe password hasher makes every test that logs in slow.
PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]

EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"

MEDIA_ROOT = tempfile.mkdtemp(prefix="sites-cms-test-media-")
