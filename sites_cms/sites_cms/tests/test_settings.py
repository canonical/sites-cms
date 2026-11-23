"""Production settings are loaded in a fresh Python process, so the test
settings already loaded here cannot hide a mistake."""

import json
import os
import subprocess
import sys
from pathlib import Path

PROJECT = Path(__file__).resolve().parents[2]

GOOD_ENV = {
    "DJANGO_SECRET_KEY": "k" * 60,
    "DJANGO_ALLOWED_HOSTS": '["cms.example.com"]',
    "DJANGO_BASE_URL": "https://cms.example.com/",
    "POSTGRESQL_DB_CONNECT_STRING": "postgresql://u:p@db:5432/cms",
}

PRINT_SETTINGS = """
import json
from sites_cms.settings import production as s
print(json.dumps({
    "debug": s.DEBUG,
    "hosts": s.ALLOWED_HOSTS,
    "origins": s.CSRF_TRUSTED_ORIGINS,
    "admin_url": s.WAGTAILADMIN_BASE_URL,
    "db_host": s.DATABASES["default"]["HOST"],
    "email": s.EMAIL_BACKEND,
    "secure_cookies": s.SESSION_COOKIE_SECURE and s.CSRF_COOKIE_SECURE,
    "hsts": s.SECURE_HSTS_SECONDS,
    "formatter": s.LOGGING["handlers"]["console"]["formatter"],
}))
"""


def load_production(env):
    clean = {
        key: value
        for key, value in os.environ.items()
        if not key.startswith(("DJANGO_", "POSTGRESQL_", "SMTP_", "SENTRY_"))
        and key != "DATABASE_URL"
    }
    return subprocess.run(
        [sys.executable, "-c", PRINT_SETTINGS],
        cwd=PROJECT,
        env={**clean, **env},
        capture_output=True,
        text=True,
    )


def test_production_settings_load_from_the_environment():
    result = load_production(GOOD_ENV)
    assert result.returncode == 0, result.stderr
    loaded = json.loads(result.stdout)
    assert loaded == {
        "debug": False,
        "hosts": ["cms.example.com"],
        "origins": ["https://cms.example.com"],
        "admin_url": "https://cms.example.com",
        "db_host": "db",
        "email": "core.email.LogAndDropBackend",
        "secure_cookies": True,
        "hsts": 31536000,
        "formatter": "json",
    }


def test_production_uses_smtp_when_a_mail_server_is_set():
    result = load_production({**GOOD_ENV, "SMTP_HOST": "smtp.internal"})
    assert result.returncode == 0, result.stderr
    assert json.loads(result.stdout)["email"].endswith("smtp.EmailBackend")


def test_production_refuses_to_start_without_a_secret_key():
    env = {k: v for k, v in GOOD_ENV.items() if k != "DJANGO_SECRET_KEY"}
    result = load_production(env)
    assert result.returncode != 0
    assert "DJANGO_SECRET_KEY is required" in result.stderr


def test_production_refuses_to_start_without_allowed_hosts():
    env = {k: v for k, v in GOOD_ENV.items() if k != "DJANGO_ALLOWED_HOSTS"}
    result = load_production(env)
    assert result.returncode != 0
    assert "DJANGO_ALLOWED_HOSTS is required" in result.stderr


def test_production_refuses_to_start_without_a_database():
    env = {
        k: v
        for k, v in GOOD_ENV.items()
        if k != "POSTGRESQL_DB_CONNECT_STRING"
    }
    result = load_production(env)
    assert result.returncode != 0
    assert "DATABASE_URL is required" in result.stderr
