# Copyright 2026 Canonical Ltd.
# See LICENSE.md at the repository root for licensing details.

"""Fixtures for the charm unit tests."""

import pathlib
import subprocess

import pytest
import yaml
from ops import testing

from charm import SitesCmsCharm

CHARM_DIR = pathlib.Path(__file__).parents[2]

# The rock's Pebble plan, from ../rockcraft.yaml expanded by Rockcraft.
ROCK_PLAN = {
    "services": {
        "django": {
            "override": "replace",
            "startup": "enabled",
            "command": (
                "/bin/python3 -m gunicorn -c /django/gunicorn.conf.py "
                "'sites_cms.wsgi:application' -k [ sync ]"
            ),
            "after": ["statsd-exporter"],
            "user": "_daemon_",
        },
        "statsd-exporter": {
            "override": "merge",
            "startup": "enabled",
            "command": "/bin/statsd_exporter",
            "user": "_daemon_",
        },
    }
}


@pytest.fixture(name="charmcraft", scope="session")
def charmcraft_fixture() -> dict:
    """Return charmcraft.yaml with the django-framework extension expanded.

    Expanding at test time tests what `charmcraft pack` builds, not a copy.
    """
    expanded = subprocess.run(
        ["charmcraft", "expand-extensions"],
        cwd=CHARM_DIR,
        check=True,
        capture_output=True,
        text=True,
    ).stdout
    return yaml.safe_load(expanded)


@pytest.fixture(name="context")
def context_fixture(charmcraft: dict, tmp_path: pathlib.Path) -> testing.Context:
    """Return a Context for the charm built from the expanded metadata."""
    meta = dict(charmcraft)
    actions = meta.pop("actions")
    config = meta.pop("config")
    charm_root = tmp_path / "charm"
    charm_root.mkdir()
    return testing.Context(
        SitesCmsCharm,
        meta=meta,
        actions=actions,
        config=config,
        charm_root=charm_root,
        app_name="sites-cms",
    )


@pytest.fixture(name="ready_state")
def ready_state_fixture(tmp_path: pathlib.Path) -> testing.State:
    """Return a leader unit with the rock running and PostgreSQL integrated."""
    app_dir = tmp_path / "django" / "app"
    app_dir.mkdir(parents=True)
    (app_dir / "manage.py").touch()
    container = testing.Container(
        name="django-app",
        can_connect=True,
        mounts={
            "django": testing.Mount(location="/django", source=tmp_path / "django"),
        },
        # Gunicorn's --check-config and `manage.py migrate` succeed.
        execs={
            testing.Exec(["/bin/python3"]),
            testing.Exec(["python3", "manage.py", "migrate"]),
        },
        _base_plan=ROCK_PLAN,
    )
    postgresql = testing.Relation(
        endpoint="postgresql",
        interface="postgresql_client",
        remote_app_data={
            "database": "sites-cms",
            "endpoints": "pg-host:5432",
            "username": "cms-user",
            "password": "cms-pass",
        },
    )
    peer = testing.PeerRelation(
        endpoint="secret-storage",
        local_app_data={"django_secret_key": "test-secret-key"},
    )
    return testing.State(
        leader=True,
        model=testing.Model(name="test-model"),
        containers={container},
        relations={postgresql, peer},
    )
