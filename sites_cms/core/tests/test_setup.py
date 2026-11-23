import json
import logging
from io import StringIO

import pytest
from django.contrib.auth import get_user_model
from django.core.mail import EmailMessage
from django.core.management import CommandError, call_command
from wagtail.models import Page, Site

from core.email import LogAndDropBackend
from core.log import JsonFormatter


@pytest.mark.django_db
def test_the_wagtail_welcome_page_is_gone():
    assert not Page.objects.filter(depth__gt=1).exists()
    assert not Site.objects.exists()
    assert Page.objects.get(depth=1).numchild == 0


@pytest.mark.django_db
def test_create_local_admin_refuses_outside_debug(settings):
    settings.DEBUG = False
    with pytest.raises(CommandError):
        call_command("create_local_admin")
    assert not get_user_model().objects.exists()


@pytest.mark.django_db
def test_create_local_admin_is_safe_to_run_twice(settings):
    settings.DEBUG = True
    call_command("create_local_admin", stdout=StringIO())
    call_command("create_local_admin", stdout=StringIO())
    admin = get_user_model().objects.get()
    assert admin.is_superuser
    assert admin.check_password("admin")


def test_seed_runs():
    out = StringIO()
    call_command("seed", stdout=out)
    assert out.getvalue().strip()


def test_json_log_line_carries_the_request_fields():
    record = logging.LogRecord(
        "sites_cms.request", logging.INFO, __file__, 1, "request", (), None
    )
    record.path = "/admin/"
    record.status = 200
    entry = json.loads(JsonFormatter().format(record))
    assert entry["level"] == "INFO"
    assert entry["logger"] == "sites_cms.request"
    assert entry["message"] == "request"
    assert entry["path"] == "/admin/"
    assert entry["status"] == 200
    assert entry["time"].endswith("+00:00")


def test_json_log_line_is_one_line_even_with_a_traceback():
    try:
        raise ValueError("boom")
    except ValueError:
        import sys

        record = logging.LogRecord(
            "x", logging.ERROR, __file__, 1, "failed", (), sys.exc_info()
        )
    line = JsonFormatter().format(record)
    assert "\n" not in line
    assert "ValueError: boom" in json.loads(line)["exception"]


def test_email_is_dropped_without_error_when_no_server_is_set(caplog):
    message = EmailMessage("Review needed", "body", to=["a@example.com"])
    with caplog.at_level(logging.WARNING):
        assert LogAndDropBackend().send_messages([message]) == 1
    assert "Review needed" in caplog.text
    assert "a@example.com" not in caplog.text
