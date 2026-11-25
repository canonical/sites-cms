# 3. The production image is a rock built with the django-framework extension

Date: 2026-11-24 · Status: accepted

## Decision

The production image is a rock, defined in `rockcraft.yaml` at the
repository root. It uses Rockcraft's `django-framework` extension on the
`ubuntu@24.04` base. Dependencies are installed from `requirements.txt`.

## Why

The extension produces the image layout a 12-factor Django charm expects:
Gunicorn on port 8000, Pebble services, and logs and metrics in the
standard places. We do not maintain that by hand.

`ubuntu@24.04` ships Python 3.12, the version this project pins. The
extension's version for `ubuntu@26.04` is still marked experimental.

## Consequences

`rockcraft.yaml` adds three things the extension does not do for us:

- It collects static files at build time, because WhiteNoise needs them.
- It sets `DJANGO_SETTINGS_MODULE` to the production settings, because
  `manage.py` defaults to the development settings.
- It stops the build from installing the project itself as a package.

Moving to `ubuntu@26.04` means a newer Python and a change to
`.python-version` and `pyproject.toml`.
