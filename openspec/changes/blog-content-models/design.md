# Design

## Context

The project has a user, image and document model and nothing else. The
Wagtail welcome page is removed by a migration, and a test asserts that the
root page has no children after migrations. There are no public pages: the
websites will read content through an API added later.

Facts from the WordPress API that shape the models (counts as of
2026-11-26):

- About 4,800 posts are in both the ubuntu.com and canonical.com
  categories. Which site shows a post is a property of the post, not of its
  place in the page tree.
- 10 categories, 1,965 tags, 83 groups. Groups nest up to 3 levels. Two
  groups are both named "Networking", told apart only by slug.
- The API returns a post's terms sorted by name. Sites use the "first
  group" for labels, canonical URLs and noindex.
- In a 400-post sample: rich text and lists in about 100%, images 49%,
  code 15%, inline styles 13%, iframes 8%, tables 5%, Vanilla buttons 4%
  (98 of 100 written by hand in a "Custom HTML" block).
- Chinese and Japanese posts are told apart by category, not by language
  settings.

## Goals / Non-Goals

**Goals:**

- Every field the websites read today has a place, so the importer can
  write it.
- Non-technical editors can write and edit posts without HTML, except for
  legacy content.
- Reviewers can try everything locally with `make setup`.

**Non-Goals:**

- Wagtail localisation. Chinese and Japanese stay as categories, as today.
- A delivery API, templates or front-end.
- Workflows, moderation or a review label. WordPress pending posts are
  not imported as posts (see `wordpress-blog-import`).
- Per-site "featured". WordPress's sticky flag is global; so is ours.

## Decisions

### A `blog` app with one index page

`BlogIndexPage` (at most one, child of the root) and `BlogPage` (only under
the index, no children). Wagtail already enforces unique slugs among
siblings, so one index gives unique post slugs for free.

The index is not created by a migration: that would break the "root has no
children" test and run on every fresh database. `make seed` and, later, the
importer create it if it is missing, through one shared helper.

Alternative: one index per site. Rejected because most posts are on two
sites, and a page can only have one parent.

### Body: three built-in blocks

```
body = StreamField([
    rich_text  RichTextBlock(features=[h2 h3 h4 bold italic link ol ul
                                       blockquote hr code superscript
                                       subscript image embed])
    table      TableBlock            (wagtail.contrib.table_block)
    html       RawHTMLBlock          label "HTML (advanced)"
])
```

Every block renders itself with Wagtail's own code, so a later API can send
ready-made HTML and the websites need no new front-end work.

Alternatives: one raw HTML field (rejected: editors are not technical); one
rich text field (rejected: drops tables, code, embeds); custom blocks for
code, captions and buttons (rejected: each needs front-end work on every
site). Code blocks and image captions go in the HTML block or as text for
now; see Risks.

### Shared fields in an abstract class

Two ordinary abstract models, as AGENTS.md requires:

| Model | Fields | Used by |
|---|---|---|
| `NamedWithSlug` | `name`, `slug`, search on both | `Author` and every term |
| `BlogTerm` | adds `description` and the admin form | `Category`, `Group`, `Tag` |

Slugs are `SlugField(unique=True, allow_unicode=True)`. A blank slug is
filled from the name on first save only, so renaming keeps the slug.

`Group.parent` is a self foreign key, `on_delete=SET_NULL`. `clean()` walks
up the parents and refuses a loop. `clean()` runs only through
`full_clean()`, which the admin calls; code that saves groups directly must
call it too.

All three, and `Author`, are registered as snippets with search on name
and slug, under one "Blog" menu with the post listing.

### How posts link to terms

| Relation | Model | Admin widget | Why |
|---|---|---|---|
| Categories (10) | `ParentalManyToManyField` | Checkboxes | Few, no order needed |
| Groups (83) | Orderable through model `BlogPageGroup` | `MultipleChooserPanel` | Order kept; searchable chooser |
| Tags (1,965) | Orderable through model `BlogPageTag` | `MultipleChooserPanel` | Order kept; 1,965 checkboxes would be unusable |

Through-model foreign keys to the term use `on_delete=CASCADE`, so deleting
a term removes the link, not the post. Wagtail's reference index already
shows usage counts on the snippet delete screen.

Alternative: django-taggit's built-in tags. Rejected because they are free
text and make their own slugs, which would change slugs the sites filter on.

### Authors

`Author` snippet: `name`, `slug` (unique), `job_title`, `bio`, `photo`
(image, `SET_NULL`), `email` (blank, indexed, not unique), `user` (nullable
foreign key to the user model, `SET_NULL`, related name `authors`).
`BlogPage.author` is a foreign key with `on_delete=PROTECT`.

Email is not unique because one person may have had several WordPress
accounts. A foreign key, not a one-to-one, for the same reason.

Email privacy comes from snippet permissions: only users who can edit
authors open the author form. The post editor's chooser shows the name.

### Linking authors to users

One function, `link_authors(user)`, fills `user` on authors whose `user` is
empty and whose email matches the user's, ignoring case. It then sets
`owner` on that author's posts that have no owner, using a queryset update
so no revision is created. It runs from:

| Trigger | Hook |
|---|---|
| Author saved | `Author.save()`, if `user` is empty and `email` is set |
| Account created | `post_save` on the user model, `created=True` |
| Sign-in | Django's `user_logged_in` signal |

It never overwrites a link, so a hand-made link stays. Signals live in the
`blog` app, so `accounts` is untouched.

Alternative: a scheduled or manual command. Rejected; deployment makes
commands awkward to run.

### Other fields

| Field | Type | Note |
|---|---|---|
| `excerpt` | `TextField(blank=True)` | Plain text |
| `featured_image` | Foreign key to the image model, `SET_NULL` | |
| `publish_date` | `DateTimeField(default=now)` | Editable; WordPress posts are often backdated |
| `featured` | `BooleanField(default=False)` | WordPress "sticky" |
| SEO title and search description | Wagtail's own page fields | |

`search_fields` add `excerpt` and `body` to Wagtail's defaults.

### Admin listing

A `PageListingViewSet` for `BlogPage`, the first item in the "Blog" menu
group with the snippets, with columns for title, status, author and
updated, and a django-filter filter set (django-filter is already
installed). Wagtail's snippet group accepts any viewset with a menu item,
so one group holds both.

Wagtail drops its own page filters when a viewset has its own filter set,
so the filter set has all four: status (Live or Draft; a scheduled post
counts as Draft), category, group and author.

### Admin preview

A minimal template, `blog/blog_page.html`, renders the title, byline and
body so editors can preview a post. It is not a public page: no Wagtail
Site exists, so nothing serves posts at a URL. If a Site is ever added,
posts would be served with this template, so the change that adds the
delivery API must remove or guard it.

## Risks / Trade-offs

- [Code blocks (15% of posts) are HTML blocks] → Editors see `<pre>`
  markup. A code block can be added later as one more built-in block plus a
  tiny template.
- [Rich text images have no caption field] → The importer writes captions
  as an italic line under the image. A captioned image block can come later.
- [Editors can add new HTML blocks] → I found no Wagtail 8.1 option to
  hide one block type from the add-block menu while keeping it in existing
  posts. The label says "advanced", and the editor guide says when to use
  it.
- [An admin removes a link while the emails still match] → The author is
  linked again the next time it is saved or the user signs in. To stop
  that, the admin also clears or changes the author's email. This is
  documented in the editor guide.
- [Linking gives ownership only of posts that already exist] → Posts
  created after the link have no owner unless their creator sets one. The
  importer sets the owner from the linked author (`wordpress-blog-import`).
- [`MultipleChooserPanel` with 1,965 tags] → The chooser is searchable and
  paginated; the seed data and a test with many tags check it stays usable.

## Migration Plan

One initial schema migration for the new app; no data migrations. Deploying
creates empty tables. Rollback is reverting the code and migrating `blog` to
zero, which drops empty tables.
