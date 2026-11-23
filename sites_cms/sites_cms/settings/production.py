"""Staging and production. Both use this file and differ only by environment.

Every deployment value comes from an environment variable. The app refuses
to start when a required one is missing.
"""

from urllib.parse import urlsplit

from sites_cms.env import database_from_url, env_list, env_str

from .base import *

DEBUG = False
SECRET_KEY = env_str("DJANGO_SECRET_KEY", required=True)
ALLOWED_HOSTS = env_list("DJANGO_ALLOWED_HOSTS")
if not ALLOWED_HOSTS:
    env_str("DJANGO_ALLOWED_HOSTS", required=True)

BASE_URL = env_str("DJANGO_BASE_URL", required=True).rstrip("/")
WAGTAILADMIN_BASE_URL = BASE_URL

# The charm provides POSTGRESQL_DB_CONNECT_STRING. DATABASE_URL also works.
DATABASES = {
    "default": database_from_url(
        env_str("POSTGRESQL_DB_CONNECT_STRING")
        or env_str("DATABASE_URL", required=True)
    )
}

# HTTPS ends at the ingress, which also redirects HTTP to HTTPS. Django does
# not redirect, so the health check keeps working over plain HTTP inside the
# cluster.
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = 60 * 60 * 24 * 365
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
_origin = urlsplit(BASE_URL)
CSRF_TRUSTED_ORIGINS = [f"{_origin.scheme}://{_origin.netloc}"]
SILENCED_SYSTEM_CHECKS = [
    "security.W008",  # SECURE_SSL_REDIRECT: done by the ingress.
    "security.W021",  # HSTS preload: decided per domain, not per service.
]

# Static files are collected at build time and served by WhiteNoise.
MIDDLEWARE.insert(
    MIDDLEWARE.index("django.middleware.security.SecurityMiddleware") + 1,
    "whitenoise.middleware.WhiteNoiseMiddleware",
)
MIDDLEWARE.append("core.middleware.RequestLogMiddleware")
STORAGES["staticfiles"] = {
    "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
}

# Uploads stay on local disk until the object storage task (A4) lands.

# Email is only used for workflow notices. Without a mail server, messages
# are logged and dropped so a missing server never blocks publishing.
SMTP_HOST = env_str("SMTP_HOST")
if SMTP_HOST:
    EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
    EMAIL_HOST = SMTP_HOST
    EMAIL_PORT = int(env_str("SMTP_PORT", "587"))
    EMAIL_HOST_USER = env_str("SMTP_USER", "")
    EMAIL_HOST_PASSWORD = env_str("SMTP_PASSWORD", "")
    EMAIL_USE_TLS = True
else:
    EMAIL_BACKEND = "core.email.LogAndDropBackend"
DEFAULT_FROM_EMAIL = env_str("EMAIL_FROM", "noreply@canonical.com")
SERVER_EMAIL = DEFAULT_FROM_EMAIL

# One JSON object per line on standard output.
LOGGING["handlers"]["console"]["formatter"] = "json"

SENTRY_DSN = env_str("SENTRY_DSN")
if SENTRY_DSN:
    import sentry_sdk

    sentry_sdk.init(
        dsn=SENTRY_DSN,
        release=COMMIT_ID,
        send_default_pii=False,
    )
