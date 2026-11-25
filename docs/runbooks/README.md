# Runbooks

Step-by-step guides for operating the service. Each is written by the task
that builds the thing it describes, so this list starts empty.

| Runbook | Status |
|---|---|
| Deploy to staging and production | To be written with the rock and charm |
| [Admin accounts in a deployment](admin-accounts.md) | Ready |
| Back up and restore the database | To be written with the backups task. Backups are taken by the PostgreSQL charm, outside this repository |
| Emergency login when company sign-in is down | To be written with the sign-in task |
| Switch a website to this CMS, and back | To be written with the cutover |

## What exists today

- **Health check:** `GET /_status/check` answers 200 with the running
  commit when the database is reachable, and 503 when it is not.
- **Logs:** production writes one JSON object per line to standard output.
