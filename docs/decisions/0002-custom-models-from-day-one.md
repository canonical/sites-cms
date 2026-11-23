# 2. Our own user, image and document models from the first migration

Date: 2026-11-23 · Status: accepted

## Decision

The project defines its own models and points Django and Wagtail at them
before any table is created:

| Setting | Model |
|---|---|
| `AUTH_USER_MODEL` | `accounts.User` |
| `WAGTAILIMAGES_IMAGE_MODEL` | `assets.CmsImage` |
| `WAGTAILDOCS_DOCUMENT_MODEL` | `assets.CmsDocument` |

`accounts.User` requires an email address and does not allow two accounts
to share one, because people will sign in with their company email.

The image and document models add nothing to Wagtail's yet.

## Why

Django cannot swap the user model cleanly once tables exist, and Wagtail's
image and document models cannot be swapped once files have been uploaded
without a data migration. Starting with our own costs a few lines now and
lets later work add fields with an ordinary migration.

We did not use Wagtail 8's custom base page model. It is marked
experimental. Shared page fields go in an ordinary abstract class.
