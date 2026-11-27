# AGENTS.md

Instructions for AI coding tools working in this repository. People may
find it a useful summary too. Details are in
[docs/development.md](docs/development.md).

## What this is

A Wagtail 8.1 project on Django 5.2 and Python 3.12. Editors use the Wagtail
admin; websites read content through an API. There are no public pages and
no front-end build.

## Layout

```
sites_cms/
  manage.py  conftest.py
  sites_cms/   settings/{base,dev,test,production}.py, env.py, urls.py
  accounts/    the user model
  assets/      the image and document models
  core/        health check, logging, middleware, local commands
docs/          development.md, decisions/, runbooks/, user/
```

A new feature gets its own app, created by the task that first needs it.
Tests live in a `tests/` folder inside each app.

## Commands

| Command | Use |
|---|---|
| `make setup` | First-time setup |
| `make run` | Dev server on port 8000 |
| `make test` | Tests (`uv run pytest path/to/test.py` for one file) |
| `make lint` / `make format` | ruff check, ruff fix |
| `make check-migrations` | Fails if a model change has no migration |
| `make check-deploy` | Django's deployment checks on production settings |
| `make lock` | After editing dependencies in `pyproject.toml` |

Run `make lint`, `make test` and `make check-migrations` before saying work
is done.

## Rules

- **PostgreSQL only.** No SQLite, in development, tests or CI.
- **79 columns**, formatted by ruff. Do not hand-format.
- **Dependencies** are edited in `pyproject.toml`, then `make lock`. Never
  edit `uv.lock` or `requirements.txt` by hand.
- **Settings** come from environment variables through `sites_cms/env.py`.
  A new variable is added to `.env.example` and `docs/development.md`.
- **Content models carry nothing from another CMS.** No WordPress IDs or
  import fields on posts, terms, authors or images. Anything like that
  belongs in the compatibility or importer apps.
- **Do not use Wagtail's custom base page model.** It is experimental.
  Share fields with an ordinary abstract class.
- **Do not change `AUTH_USER_MODEL`, `WAGTAILIMAGES_IMAGE_MODEL` or
  `WAGTAILDOCS_DOCUMENT_MODEL`.** Add fields to the existing models.
- **No front-end build step.** Admin styling, if ever needed, is plain CSS.
- **Check Wagtail guidance against the installed version.** Older docs
  pages and blog posts describe settings and imports that have changed.
  Prefer the 8.1 docs and the code in `.venv`. Tests turn deprecation
  warnings from our own code into failures.
- **Commits** are one line. No AI attribution in commits or pull requests.

## Docs to keep current

- A change an editor can see updates `docs/user/` in the same pull request.
- A change a developer can see updates `docs/development.md`.

## Where a decision is recorded

| Kind of decision | Where |
|---|---|
| A project-wide choice or rule (a tool, a version, a rule like the ones above) | `docs/decisions/`, one short file |
| How a feature behaves, and why | With the feature's OpenSpec change in `openspec/changes/`, then in `openspec/specs/` once archived. See [0003](docs/decisions/0003-use-openspec-for-feature-specs.md) |

Record a decision in one place only.
