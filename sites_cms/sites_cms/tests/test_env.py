import pytest
from django.core.exceptions import ImproperlyConfigured

from sites_cms.env import database_from_url, env_bool, env_list, env_str


def test_env_str_returns_the_default_when_unset_or_empty(monkeypatch):
    monkeypatch.delenv("X", raising=False)
    assert env_str("X", "fallback") == "fallback"
    monkeypatch.setenv("X", "  ")
    assert env_str("X", "fallback") == "fallback"
    monkeypatch.setenv("X", " value ")
    assert env_str("X") == "value"


def test_env_str_required_names_the_missing_variable(monkeypatch):
    monkeypatch.delenv("X", raising=False)
    with pytest.raises(ImproperlyConfigured, match="X"):
        env_str("X", required=True)


@pytest.mark.parametrize("value", ["1", "true", "True", "YES", "on"])
def test_env_bool_true_values(monkeypatch, value):
    monkeypatch.setenv("X", value)
    assert env_bool("X") is True


@pytest.mark.parametrize("value", ["0", "false", "no", "off", "anything"])
def test_env_bool_false_values(monkeypatch, value):
    monkeypatch.setenv("X", value)
    assert env_bool("X", default=True) is False


def test_env_bool_default_when_unset(monkeypatch):
    monkeypatch.delenv("X", raising=False)
    assert env_bool("X") is False
    assert env_bool("X", default=True) is True


def test_env_list_reads_a_json_list_as_the_charm_sends_it(monkeypatch):
    monkeypatch.setenv("X", '["cms.example.com", "10.1.2.3"]')
    assert env_list("X") == ["cms.example.com", "10.1.2.3"]


def test_env_list_reads_a_comma_list(monkeypatch):
    monkeypatch.setenv("X", "cms.example.com, localhost ,")
    assert env_list("X") == ["cms.example.com", "localhost"]


def test_env_list_default_when_unset(monkeypatch):
    monkeypatch.delenv("X", raising=False)
    assert env_list("X") == []
    assert env_list("X", ["a"]) == ["a"]


@pytest.mark.parametrize("value", ['["unclosed"', '[{"a": 1}', "[1, 2"])
def test_env_list_rejects_broken_json(monkeypatch, value):
    monkeypatch.setenv("X", value)
    with pytest.raises(ImproperlyConfigured, match="X"):
        env_list("X")


def test_database_from_url_reads_a_postgres_url():
    config = database_from_url("postgresql://u:p@db.internal:5433/cms")
    assert config["ENGINE"] == "django.db.backends.postgresql"
    assert config["HOST"] == "db.internal"
    assert config["PORT"] == 5433
    assert config["NAME"] == "cms"
    assert config["CONN_HEALTH_CHECKS"] is True


def test_database_from_url_refuses_other_databases():
    with pytest.raises(ImproperlyConfigured, match="PostgreSQL"):
        database_from_url("sqlite:///db.sqlite3")
