# Copyright 2026 Canonical Ltd.
# See LICENSE.md at the repository root for licensing details.

"""Unit tests for what is specific to this charm.

The charm adds no code to paas-charm's Django charm, so paas-charm's
behaviour (actions, migrations, ingress) is not retested here. These tests
check the parts that join it to this project: the metadata and the
environment that the production settings read.
"""

import json
import os
import pathlib
import subprocess

import ops

REPO_ROOT = pathlib.Path(__file__).parents[3]

# Loads the production settings and prints what they resolved to.
LOAD_SETTINGS = """
import json
from django.conf import settings
db = settings.DATABASES["default"]
print(json.dumps({
    "allowed_hosts": settings.ALLOWED_HOSTS,
    "base_url": settings.BASE_URL,
    "csrf_trusted_origins": settings.CSRF_TRUSTED_ORIGINS,
    "secret_key": settings.SECRET_KEY,
    "db": [db["HOST"], db["PORT"], db["NAME"], db["USER"]],
}))
"""


def test_postgresql_is_the_only_required_integration(charmcraft):
    """The charm blocks only on a missing database.

    arrange: expand the django-framework extension.
    act: read the integrations the charm requires.
    assert: PostgreSQL is required and every other integration is optional,
        so the charm blocks only on a missing database.
    """
    requires = charmcraft["requires"]

    assert requires["postgresql"] == {
        "interface": "postgresql_client",
        "optional": False,
        "limit": 1,
    }
    assert all(
        spec.get("optional", True) for name, spec in requires.items() if name != "postgresql"
    )


def test_charm_environment_loads_production_settings(context, ready_state):
    """The production settings load from the charm's environment.

    arrange: a ready unit with PostgreSQL integrated.
    act: run config-changed, then load the project's production settings
        with the environment the charm gives the django service.
    assert: the settings load and use the charm's values.
    """
    out = context.run(context.on.config_changed(), ready_state)
    assert out.unit_status == ops.ActiveStatus()
    container = out.get_container("django-app")
    env = container.plan.services["django"].environment

    result = subprocess.run(
        ["uv", "run", "--frozen", "python", "-c", LOAD_SETTINGS],
        cwd=REPO_ROOT / "sites_cms",
        env={
            "PATH": os.environ["PATH"],
            "HOME": os.environ.get("HOME", "/tmp"),
            "DJANGO_SETTINGS_MODULE": "sites_cms.settings.production",
            **env,
        },
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stderr
    settings = json.loads(result.stdout.splitlines()[-1])
    assert settings == {
        "allowed_hosts": ["sites-cms.test-model"],
        "base_url": "http://sites-cms.test-model:8000",
        "csrf_trusted_origins": ["http://sites-cms.test-model:8000"],
        "secret_key": "test-secret-key",
        "db": ["pg-host", 5432, "sites-cms", "cms-user"],
    }
