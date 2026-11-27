# Proposal

## Why

The 8,238 blog posts on admin.insights.ubuntu.com are to move to this CMS,
but it has no content models yet: no blog post, no categories, tags or
groups, no authors. The sites decide which posts to show by category, tag
and group, so those must exist, with their exact slugs, before anything can
be imported. This change builds the place the posts will live. Importing
them is the next change (`wordpress-blog-import`).

## What Changes

- A new `blog` app with a blog index page and a blog post page.
- Blog post fields for everything the sites read today: title, slug,
  excerpt, body, featured image, author, publish date, featured (sticky)
  flag, categories, groups and tags, SEO title and description.
- A body made only of Wagtail's built-in blocks: rich text (with images and
  embeds), table, and raw HTML. No custom blocks and no templates, so the
  websites need no new front-end work to show it.
- Categories, groups and tags as editor-managed snippets with unique slugs.
  Groups can have a parent group.
- An "Author" for each byline, separate from user accounts, linked to a
  user account automatically when the emails match (when the author is
  saved, when an account is created, and at every sign-in), or by hand.
- A "Blog posts" listing in the admin with filters for category, group,
  author and live status.
- Sample blog content in `make seed`, so reviewers can try it locally.
- `wagtail.contrib.table_block` is added to `INSTALLED_APPS`.

Not in this change: importing from WordPress, any API for the websites,
splitting categories into "site" and "content type", topics (no site uses
them), and Wagtail workflows.

## Capabilities

### New Capabilities

- `blog-posts`: the blog post page, its fields and body, its states
  (live, draft, scheduled) and the admin listing.
- `blog-taxonomy`: categories, groups (with parents) and tags, and how
  posts are tagged with them.
- `blog-authors`: authors as bylines and how they are linked to user
  accounts.

### Modified Capabilities

None. No specs exist yet.

## Impact

- New app `sites_cms/blog/` with models, migrations, admin registration
  and tests.
- `settings/base.py`: `blog` and `wagtail.contrib.table_block` in
  `INSTALLED_APPS`.
- `pyproject.toml`: the new app in the deprecation-warning filters.
- `core/management/commands/seed.py`: sample blog content.
- `accounts`: none. Linking lives in the `blog` app and listens to user
  signals, so the user model is unchanged.
- Docs: `docs/user/` gets a "Blog posts" guide; `docs/development.md` notes
  the new app.
- No new dependencies.
