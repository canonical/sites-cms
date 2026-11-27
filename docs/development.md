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
| `make seed` | Loads sample content. Does nothing until the first content models exist |
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

### Build the production image

The production image is a rock, built by `rockcraft.yaml` at the
repository root with the `django-framework` extension. You need the
`rockcraft` snap and LXD.

```bash
rockcraft pack                # writes sites-cms_<version>_amd64.rock
rockcraft.skopeo --insecure-policy copy \
  oci-archive:sites-cms_0.1.0_amd64.rock docker-daemon:sites-cms:0.1.0
```

In the image:

- Gunicorn serves the app on port 8000 with the production settings.
- The application code is in `/django/app`.
- Static files are collected at build time into `/django/static-collected`
  and served by WhiteNoise.
- `DJANGO_SETTINGS_MODULE` defaults to the production settings, so
  `python3 manage.py migrate` in the container needs only the production
  environment variables.

Run it with the production variables from the table above, for example
`docker run -p 8000:8000 -e DJANGO_SECRET_KEY=... sites-cms:0.1.0`.
`rockcraft clean` removes the build container.

### Build and try the charm

The charm is in `charm/`. It uses the `django-framework` extension of
Charmcraft and runs the rock above. You need the `charmcraft` snap, and Juju
with a Kubernetes cloud (MicroK8s with the `registry` add-on works) to try
it.

Run these from the repository root:

```bash
(cd charm && charmcraft pack) # writes charm/sites-cms_amd64.charm
```

`charmcraft pack` downloads the charm libraries into `charm/lib/`. They are
not committed.

To try it, push the rock to the MicroK8s registry and deploy:

```bash
rockcraft.skopeo --insecure-policy copy --dest-tls-verify=false \
  oci-archive:sites-cms_0.1.0_amd64.rock \
  docker://localhost:32000/sites-cms:0.1.0
juju add-model sites-cms
juju deploy postgresql-k8s --channel 16/stable --trust
juju deploy ./charm/sites-cms_amd64.charm \
  --resource django-app-image=localhost:32000/sites-cms:0.1.0
juju integrate sites-cms postgresql-k8s
juju run sites-cms/0 create-superuser username=admin email=admin@example.com
```

The charm stays blocked until PostgreSQL is integrated. It sets
`DJANGO_SECRET_KEY`, `DJANGO_ALLOWED_HOSTS`, `DJANGO_BASE_URL` and
`POSTGRESQL_DB_CONNECT_STRING`, and runs `manage.py migrate` on start. Add
host names with `juju config sites-cms django-allowed-hosts=<host>`. Admin
login needs HTTPS, so sign in through an ingress with TLS. The charm creates
no default admin: `create-superuser` returns a random password. See
[the admin accounts runbook](runbooks/admin-accounts.md) for changing
passwords.
`juju destroy-model sites-cms --destroy-storage` removes it all.

### Test the charm

The charm adds no code to paas-charm, so its tests cover only what joins
it to this project. Run them from `charm/` with `uvx tox`. Both need
`charmcraft fetch-libs` first.

- **Unit** (`uvx tox -e unit`, seconds): checks that PostgreSQL is the only
  required integration, and loads the production settings with the
  environment the charm generates. A renamed or new required setting fails
  here. Needs the `charmcraft` and `uv` commands.
- **Integration** (about 4 minutes): deploys the packed charm and the rock
  into a temporary model, with PostgreSQL. Checks blocked and active
  status, the health check, both actions, `django-allowed-hosts` and
  removing the database. Push the rock as above, then:

```bash
uvx tox -e integration -- --controller microk8s-controller \
  --charm-file ./sites-cms_amd64.charm \
  --rock-image localhost:32000/sites-cms:0.1.0
```

Always pass `--controller`. Without it the model is added to whichever
controller is current. `--keep-models` keeps the model for debugging.

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
