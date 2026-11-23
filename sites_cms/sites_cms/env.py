"""Small helpers for reading settings from environment variables."""

import json
import os

import dj_database_url
from django.core.exceptions import ImproperlyConfigured

TRUE_VALUES = {"1", "true", "yes", "on"}


def env_str(name, default=None, *, required=False):
    """Return the variable, or the default when it is unset or empty."""
    value = os.environ.get(name, "").strip()
    if value:
        return value
    if required:
        raise ImproperlyConfigured(
            f"Environment variable {name} is required but is not set."
        )
    return default


def env_bool(name, default=False):
    value = env_str(name)
    if value is None:
        return default
    return value.lower() in TRUE_VALUES


def env_list(name, default=()):
    """Read a list written as JSON (`["a", "b"]`) or with commas (`a,b`).

    The charm sends JSON; a comma list is easier to type locally.
    """
    raw = env_str(name)
    if raw is None:
        return list(default)
    if raw.startswith("["):
        try:
            items = json.loads(raw)
        except json.JSONDecodeError as error:
            raise ImproperlyConfigured(
                f"Environment variable {name} is not a valid JSON list."
            ) from error
        if not isinstance(items, list):
            raise ImproperlyConfigured(
                f"Environment variable {name} must be a list."
            )
    else:
        items = raw.split(",")
    return [str(item).strip() for item in items if str(item).strip()]


def database_from_url(url):
    """Turn a PostgreSQL URL into a Django database setting."""
    config = dj_database_url.parse(
        url, conn_max_age=60, conn_health_checks=True
    )
    if config.get("ENGINE") != "django.db.backends.postgresql":
        raise ImproperlyConfigured(
            "Only PostgreSQL is supported. The database URL must start "
            "with postgresql://"
        )
    return config
