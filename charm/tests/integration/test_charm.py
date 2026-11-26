# Copyright 2026 Canonical Ltd.
# See LICENSE.md at the repository root for licensing details.

"""Integration tests: the charm running the sites-cms rock on Kubernetes.

The tests share one deployment and run in file order.
"""

import pathlib
import time

import jubilant
import pytest
import requests

APP = "sites-cms"
UNIT = f"{APP}/0"
POSTGRESQL = "postgresql-k8s"


def get(juju: jubilant.Juju, path: str, host: str | None = None) -> requests.Response:
    """Send a GET to the unit on port 8000 with the given Host header.

    Django checks the Host header against DJANGO_ALLOWED_HOSTS, which the
    charm fills with the service name, so that is the default.
    """
    address = juju.status().apps[APP].units[UNIT].address
    model = juju.model.rpartition(":")[2] if juju.model else ""
    return requests.get(
        f"http://{address}:8000{path}",
        headers={"Host": host or f"{APP}.{model}"},
        timeout=30,
        allow_redirects=False,
    )


def test_blocks_without_database(juju: jubilant.Juju, charm_file: pathlib.Path, rock_image: str):
    """Without PostgreSQL the charm is blocked.

    arrange: a new model.
    act: deploy the charm with the rock, without PostgreSQL.
    assert: the charm is blocked waiting for the postgresql integration.
    """
    juju.deploy(charm_file, APP, resources={"django-app-image": rock_image})

    status = juju.wait(lambda s: jubilant.all_blocked(s, APP))

    message = status.apps[APP].units[UNIT].workload_status.message
    assert message == "missing integrations: postgresql"


def test_active_with_database(juju: jubilant.Juju):
    """With PostgreSQL the charm is active and serves requests.

    arrange: the blocked charm.
    act: deploy PostgreSQL and integrate it.
    assert: the charm is active and the health check, which queries the
        database, and the admin sign-in page both answer 200.
    """
    juju.deploy(POSTGRESQL, channel="14/stable", trust=True)
    juju.integrate(APP, POSTGRESQL)

    juju.wait(lambda s: jubilant.all_active(s, APP, POSTGRESQL))

    health = get(juju, "/_status/check")
    assert health.status_code == 200
    assert health.json()["status"] == "ok"
    assert get(juju, "/admin/login/").status_code == 200


def test_create_superuser(juju: jubilant.Juju):
    """create-superuser creates a user once.

    arrange: the active charm.
    act: run create-superuser, then run it again with the same username.
    assert: the first run returns a password, which needs the migrations to
        have created the user tables; the second run fails.
    """
    params = {"username": "integration-admin", "email": "admin@example.com"}

    task = juju.run(UNIT, "create-superuser", params)

    assert task.results["password"]
    with pytest.raises(jubilant.TaskError):
        juju.run(UNIT, "create-superuser", params)


def test_rotate_secret_key(juju: jubilant.Juju):
    """rotate-secret-key keeps the app serving.

    arrange: the active charm.
    act: run rotate-secret-key.
    assert: the action succeeds and the app restarts and keeps serving.
    """
    task = juju.run(UNIT, "rotate-secret-key")

    assert task.results["status"] == "success"
    juju.wait(lambda s: jubilant.all_active(s, APP))
    assert get(juju, "/_status/check").status_code == 200


def test_allowed_hosts(juju: jubilant.Juju):
    """django-allowed-hosts controls which hosts Django answers.

    arrange: the active charm.
    act: set django-allowed-hosts to a public host name.
    assert: Django answers for that host and the service name, and rejects
        any other host.
    """
    juju.config(APP, {"django-allowed-hosts": "cms.example.com"})

    # juju.config returns before the restart, and the unit is already active,
    # so wait for the new host to be served instead of for a status.
    deadline = time.monotonic() + 300
    while True:
        try:
            if get(juju, "/_status/check", host="cms.example.com").status_code == 200:
                break
        except requests.RequestException:
            pass
        assert time.monotonic() < deadline, "cms.example.com was never allowed"
        time.sleep(5)
    juju.wait(lambda s: jubilant.all_active(s, APP))

    assert get(juju, "/_status/check").status_code == 200
    assert get(juju, "/_status/check", host="other.example.com").status_code == 400


def test_blocks_when_database_removed(juju: jubilant.Juju):
    """Removing PostgreSQL blocks the charm again.

    arrange: the active charm.
    act: remove the PostgreSQL integration.
    assert: the charm is blocked again.
    """
    juju.remove_relation(APP, POSTGRESQL)

    status = juju.wait(lambda s: jubilant.all_blocked(s, APP))

    message = status.apps[APP].units[UNIT].workload_status.message
    assert message == "missing integrations: postgresql"
