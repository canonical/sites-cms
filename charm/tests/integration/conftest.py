# Copyright 2026 Canonical Ltd.
# See LICENSE.md at the repository root for licensing details.

"""Fixtures for the charm integration tests."""

import pathlib

import jubilant
import pytest


def pytest_addoption(parser: pytest.Parser) -> None:
    """Add the options that point the tests at the built artefacts."""
    parser.addoption(
        "--charm-file",
        help="Path to the packed charm, e.g. ./sites-cms_amd64.charm",
    )
    parser.addoption(
        "--rock-image",
        help="Rock image the cluster can pull, e.g. localhost:32000/sites-cms:0.1.0",
    )
    parser.addoption(
        "--controller",
        help="Juju controller for the test model; defaults to the current one",
    )
    parser.addoption(
        "--keep-models",
        action="store_true",
        help="Keep the test model after the run, for debugging",
    )


@pytest.fixture(name="charm_file", scope="session")
def charm_file_fixture(request: pytest.FixtureRequest) -> pathlib.Path:
    """Return the packed charm."""
    value = request.config.getoption("--charm-file")
    if not value:
        pytest.fail("--charm-file is required")
    path = pathlib.Path(value).resolve()
    if not path.exists():
        pytest.fail(f"charm file {path} does not exist")
    return path


@pytest.fixture(name="rock_image", scope="session")
def rock_image_fixture(request: pytest.FixtureRequest) -> str:
    """Return the rock image reference."""
    value = request.config.getoption("--rock-image")
    if not value:
        pytest.fail("--rock-image is required")
    return value


@pytest.fixture(name="juju", scope="module")
def juju_fixture(request: pytest.FixtureRequest):
    """Return a Juju client for a temporary model, removed afterwards."""
    keep = request.config.getoption("--keep-models")
    controller = request.config.getoption("--controller")
    with jubilant.temp_model(keep=keep, controller=controller) as juju:
        juju.wait_timeout = 20 * 60
        yield juju
        if request.session.testsfailed:
            print(juju.debug_log(limit=200), end="")
