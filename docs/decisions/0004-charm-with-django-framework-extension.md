# 4. The charm uses Charmcraft's django-framework extension

Date: 2026-11-25 · Status: accepted

## Decision

The Juju charm lives in `charm/` in this repository. It is generated from
Charmcraft's `django-framework` profile and runs the rock from decision
0003. `src/charm.py` adds nothing to the `paas-charm` Django charm yet.

The charm libraries that `charmcraft pack` downloads into `charm/lib/` are
not committed.

## Why

The extension gives us, without our own charm code: database
integrations, migrations on start, ingress, the secret key, the
`create-superuser` action, and logs and metrics for the observability
stack. Keeping the charm next to the app keeps a settings change and the
charm change that needs it in one pull request.

The libraries are third-party code that the extension declares and
Charmcraft fetches on every pack. Committing them would add code we do not
review.

## Consequences

Only PostgreSQL is integrated. Other integrations the app may need are added to `charmcraft.yaml` when the app supports them.
