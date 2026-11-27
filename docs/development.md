# Development

## What you need

- [Docker](https://docs.docker.com/get-docker/), for the database only.
- [uv](https://docs.astral.sh/uv/getting-started/installation/). It installs
  the right Python and every dependency for you.

The app runs directly on your machine, not in a container. Your editor can
use `.venv` as it is.

## First run

```bash
make setup
make run
```

Open http://localhost:8000/admin/ and sign in as `admin` / `admin`.

`make setup` installs dependencies, starts PostgreSQL, creates the tables,
creates the local admin user and loads sample content. It is safe to run
again.

## Commands

| Command | What it does |
|---|---|
| `make setup` | Everything needed after a fresh clone |
| `make run` | Starts the server on port 8000. It restarts itself when you save a file |
| `make seed` | Loads sample content: a blog index, terms, authors and posts. Safe to run again |
| `make test` | Runs the tests |
| `make lint` | Checks code style |
| `make format` | Fixes code style |
| `make check-migrations` | Fails if you changed a model and forgot the migration |
| `make check-deploy` | Runs Django's deployment checks against production settings |
| `make lock` | Rebuilds `uv.lock` and `requirements.txt` after a dependency change |
| `make db` | Starts the database on its own |

`make run` only starts the server. It does not install anything or run
migrations. If Django says migrations are pending, run
`uv run python sites_cms/manage.py migrate`.

Any other Django command: `uv run python sites_cms/manage.py <command>`.

## Apps

The Django apps live in `sites_cms/`.

| App | Holds |
|---|---|
| `accounts` | The user model |
| `assets` | The image and document models |
| `blog` | Blog index and post pages, categories, groups, tags and authors, the "Blog posts" admin listing |
| `core` | Health check, logging, middleware, local commands |

The blog index is not created by a migration. `make seed` creates it, through
`blog.models.get_blog_index()`, and so will the WordPress importer.

## Versions

| | Version | Notes |
|---|---|---|
| Python | 3.12 | Set in `.python-version` |
| Django | 5.2 | Long-term support release, supported until April 2028 |
| Wagtail | 8.1 | Then 8.2, then 8.3 (long-term support, May 2027) |
| PostgreSQL | 16 | The only database, including for tests |

### A warning about Wagtail documentation

Search results often land on docs for an old Wagtail version, and many
tutorials are older still. Settings and import paths have changed over the
years. Before following a page:

- Check the version in the page address. Use
  `https://docs.wagtail.org/en/v8.1/...` or `/en/stable/`.
- When in doubt, read the installed code in `.venv/lib/python3.12/site-packages/wagtail/`.
  It is always right.
- Our tests fail if our own code uses something Django or Wagtail has
  deprecated, so `make test` will catch most out-of-date advice.

The settings in this project were checked against the project template that
Wagtail 8.1 itself generates (`wagtail start`), on 23 November 2026.

## Settings

Settings live in `sites_cms/sites_cms/settings/`.

| File | Used for | What differs |
|---|---|---|
| `base.py` | Shared by all | Apps, middleware, Wagtail options |
| `dev.py` | `make run` | Debug on, email printed in the terminal, any host allowed |
| `test.py` | `make test`, CI | Debug off, fast password hashing, email kept in memory, uploads in a temporary folder |
| `production.py` | Staging and production | Everything from environment variables |

Staging and production use the same file. They differ only by environment.

### Environment variables

Locally you need none. To override one, copy `.env.example` to `.env`.

| Variable | Where | Meaning |
|---|---|---|
| `DATABASE_URL` | Local, CI | PostgreSQL address. Default `postgresql://sites_cms:sites_cms@localhost:5434/sites_cms` |
| `DB_PORT` | Local | Port the database container uses on your machine. Default 5434, chosen to stay clear of a PostgreSQL you may already run on 5432 |
| `DJANGO_SECRET_KEY` | Production, required | Signing key |
| `DJANGO_ALLOWED_HOSTS` | Production, required | Host names, as a JSON list or separated by commas |
| `DJANGO_BASE_URL` | Production, required | Public address of the CMS, with `https://` |
| `POSTGRESQL_DB_CONNECT_STRING` | Production | Database address from the PostgreSQL charm. `DATABASE_URL` is used if this is unset |
| `SMTP_HOST`, `SMTP_PORT`, `SMTP_USER`, `SMTP_PASSWORD` | Production, optional | Mail server. Without `SMTP_HOST`, emails are logged and dropped |
| `EMAIL_FROM` | Production, optional | Sender address |
| `SENTRY_DSN` | Production, optional | Turns on error reporting |
| `COMMIT_ID` | Production, optional | Shown by the health check |

Production refuses to start if a required variable is missing, and the
error names the variable.

New variables are read through the helpers in `sites_cms/sites_cms/env.py`
(`env_str`, `env_bool`, `env_list`), and added to this table and to
`.env.example`.

## How to

### Add a dependency

1. Add it to `dependencies` in `pyproject.toml` (or the `dev` group for a
   tool only developers need).
2. Run `make lock`.
3. Commit `pyproject.toml`, `uv.lock` and `requirements.txt` together.

`requirements.txt` is generated for the production image. Never edit it or
`uv.lock` by hand. CI fails if either is out of date.

### Add an app

```bash
cd sites_cms
uv run python manage.py startapp blog
```

Then add `"blog"` to `INSTALLED_APPS` in `settings/base.py`, delete the
generated `tests.py`, and create a `tests/` folder with an `__init__.py`.

### Change a model

```bash
uv run python sites_cms/manage.py makemigrations
uv run python sites_cms/manage.py migrate
```

Commit the migration with the model change. `make check-migrations` and CI
fail if you forget.

### Run one test

```bash
uv run pytest sites_cms/core/tests/test_views.py -q
uv run pytest -k "status_check" -q
```

`make test` keeps the test database between runs to stay fast. After
switching branches with different migrations, run
`uv run pytest --create-db` once.

## What CI checks

Every pull request runs five jobs: `lint`, `test`, `migrations`, `lockfile`
and `audit` (known vulnerabilities in dependencies). All must pass.

## How fast it is

Measured on 23 November 2026.

| Moment | Target | macOS (Apple silicon) | Linux |
|---|---|---|---|
| `make run`, database already up, to the login page | under 5 s | 2.0 s | not measured yet |
| Save a file, to the server answering again | under 3 s | not measured yet | not measured yet |
| `make setup` on a fresh clone, images already pulled | under 1 min | not measured yet | not measured yet |
| `make test`, test database already created | under 15 s | 2.7 s | not measured yet |
| `make test`, creating the test database | under 15 s | 8.4 s | not measured yet |

Please fill in the gaps when you first set the project up.

## Troubleshooting

**"connection refused" on port 5434.** The database is not running. Run
`make db`.

**Port 5434 is already in use.** Put `DB_PORT=5435` and a matching
`DATABASE_URL` in `.env`.

**Tests fail with a missing table or column.** The kept test database is
out of date. Run `uv run pytest --create-db`.

**Start again from nothing.** `docker compose down -v` deletes the local
database. Then `make setup`.
