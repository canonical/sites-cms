# Tasks

## 1. App setup

- [x] 1.1 Create the `blog` app with `startapp`, delete `tests.py`, add a `tests/` folder, add `blog` and `wagtail.contrib.table_block` to `INSTALLED_APPS`, and add `blog` to the deprecation-warning filters in `pyproject.toml`; verify `make test` still passes
- [x] 1.2 Note the `blog` app in the layout section of `AGENTS.md` and in `docs/development.md`; verify the docs list it

## 2. Categories, groups and tags

- [x] 2.1 Add the abstract `BlogTerm` and the `Category`, `Group` (with parent) and `Tag` models with unique unicode slugs filled from the name on first save only; verify with tests for slug filling, slugs kept on rename, duplicate slugs refused, the same slug allowed across kinds, and non-ASCII slugs
- [x] 2.2 Refuse group parent loops in `Group.clean()`; verify with tests for self-parent and two-level loops
- [x] 2.3 Register the three models as snippets with search on name and slug; verify in a test that the admin index and create views return 200 for a superuser
- [x] 2.4 Make migrations and verify `make check-migrations` passes

## 3. Authors

- [x] 3.1 Add the `Author` snippet (name, unique slug, job title, bio, photo, email, user link); verify with model tests and a test that the snippet views return 200
- [x] 3.2 Add `link_authors(user)` and call it from `Author.save()`, user `post_save` on creation, and `user_logged_in`; verify with tests for each trigger, case-insensitive matching, several authors linked to one user, and that an existing link is never replaced
- [x] 3.3 Make linking set the owner of the author's unowned posts without creating revisions; verify with a test that unowned posts get the owner, owned posts keep theirs, and revision counts do not change
- [x] 3.4 Make migrations and verify `make check-migrations` passes

## 4. Blog pages

- [x] 4.1 Add `BlogIndexPage` (max one, parent root, children only blog posts) and a helper that returns the index, creating it if missing; verify with tests for allowed parent and child types and that calling the helper twice gives one index
- [x] 4.2 Add `BlogPage` with excerpt, body, featured image, author (`PROTECT`), publish date, featured flag, categories, ordered groups and ordered tags, and editor panels for all of them; verify with tests that a full post round-trips every field, group and tag order is kept, deleting a term keeps the post, deleting a used author is refused, and deleting the featured image keeps the post
- [x] 4.3 Define the body as rich text (with the feature list in design.md), table and "HTML (advanced)" blocks; verify with tests that only these three block types exist and that an HTML block returns its markup unchanged
- [x] 4.4 Add `excerpt` and `body` to search fields; verify with a test that searching a word from the body finds the post
- [x] 4.5 Make migrations and verify `make check-migrations` passes, and that the existing test that the root page has no children after migrations still passes

## 5. Admin listing

- [x] 5.1 Register a "Blog posts" `PageListingViewSet` with title, status, author and updated columns, and filters for category, group, author and live status; verify with tests that each filter returns only matching posts and that search by title works

## 6. Sample content and editor docs

- [x] 6.1 Extend `seed` to create the blog index, 3 categories, 4 groups (one nested), about 10 tags, 3 authors (one with the local admin's email), and 6 posts: live, draft, scheduled, in two site categories, featured, and one using every block type; verify with a test that running it twice gives the same counts and that the admin is linked to its author
- [x] 6.2 Write `docs/user/blog-posts.md`: creating a post, categories, groups and tags, authors and linked accounts (including the relinking note), the listing filters, and when to use the HTML block; link it from `docs/user/README.md`; verify every step in it against a seeded local site

## 7. Integration check

- [x] 7.1 Run `make lint`, `make test` and `make check-migrations` and verify all pass
- [x] 7.2 Run `make setup` on a fresh database and walk through the reviewer checklist in the pull request description (filters, admin linked, new user auto-linked, every block type saved and previewed, duplicate tag slug refused); verify each item

## Workflow follow-up

- Put the reviewer checklist from 7.2 in the pull request description.
- Archive the change after review and merge.
