# sites-cms

Canonical's content management system, built on
[Wagtail](https://wagtail.org). Editors write here; the websites read the
content through an API. This service has no public pages of its own.

## Run it

You need [Docker](https://docs.docker.com/get-docker/) and
[uv](https://docs.astral.sh/uv/getting-started/installation/).

```bash
make setup   # once: dependencies, database, admin user
make run     # http://localhost:8000/admin/  (admin / admin)
```

`make` on its own lists every command.

## Find your way around

| | |
|---|---|
| [docs/development.md](docs/development.md) | Setup in detail, commands, settings, how to add things |
| [docs/user/](docs/user/README.md) | The guide for editors |
| [docs/decisions/](docs/decisions/) | Project-wide choices and why we made them |
| [docs/runbooks/](docs/runbooks/README.md) | How to operate the service |
| [AGENTS.md](AGENTS.md) | Rules for AI coding tools (and a quick summary for people) |

## Licence

[LGPL v3](LICENSE.md)
