from unittest import mock

import pytest
from django.db import OperationalError


@pytest.mark.django_db
def test_status_check_reports_ok_and_the_commit(client, settings):
    settings.COMMIT_ID = "abc123"
    response = client.get("/_status/check")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "commit": "abc123"}
    assert "no-cache" in response["Cache-Control"]


def test_status_check_reports_503_when_the_database_is_down(client):
    with mock.patch(
        "core.views.connection.cursor",
        side_effect=OperationalError("connection refused"),
    ):
        response = client.get("/_status/check")
    assert response.status_code == 503
    assert response.json()["status"] == "error"


def test_status_check_needs_no_login(client):
    with mock.patch("core.views.connection.cursor"):
        assert client.get("/_status/check").status_code == 200


def test_robots_txt_disallows_everything(client):
    response = client.get("/robots.txt")
    assert response.status_code == 200
    assert response["Content-Type"].startswith("text/plain")
    assert response.content == b"User-agent: *\nDisallow: /\n"


def test_every_response_asks_not_to_be_indexed(client):
    assert client.get("/robots.txt")["X-Robots-Tag"] == "noindex"
    with mock.patch("core.views.connection.cursor"):
        assert client.get("/_status/check")["X-Robots-Tag"] == "noindex"


def test_root_sends_visitors_to_the_admin(client):
    response = client.get("/")
    assert response.status_code == 302
    assert response["Location"] == "/admin/"


@pytest.mark.django_db
def test_admin_login_page_loads(client):
    response = client.get("/admin/login/")
    assert response.status_code == 200
    assert b'name="username"' in response.content


@pytest.mark.django_db
def test_admin_dashboard_loads_for_an_admin(admin_client):
    assert admin_client.get("/admin/").status_code == 200
