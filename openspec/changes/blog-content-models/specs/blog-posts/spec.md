# Spec Delta

## Purpose

Gives each blog post a home in the CMS with every field the websites read
today, so posts can be imported without losing information and then edited
by non-technical editors.

## ADDED Requirements

### Requirement: Blog posts live under one blog index
The system SHALL keep every blog post as a page directly under a single blog
index page. Blog posts SHALL NOT have child pages, and a blog index SHALL
accept only blog posts as children.

#### Scenario: Adding a post
- **WHEN** an editor adds a child page to the blog index
- **THEN** the only page type offered is "Blog post"

#### Scenario: No pages under a post
- **WHEN** an editor opens the "add child page" action on a blog post
- **THEN** no page type is offered

### Requirement: Blog post slugs are unique
The system SHALL refuse to save a blog post whose slug is already used by
another blog post.

#### Scenario: Duplicate slug
- **GIVEN** a blog post with slug `kubeflow-1-9`
- **WHEN** an editor saves a second blog post with slug `kubeflow-1-9`
- **THEN** the save is refused with a message that the slug is in use

### Requirement: Blog posts carry the fields the sites read
A blog post SHALL have a title, slug, excerpt, body, featured image, author,
publish date, featured flag, categories, groups, tags, SEO title and search
description. Only the title and slug SHALL be required.

#### Scenario: Minimal post
- **WHEN** an editor saves a blog post with only a title
- **THEN** the post is saved as a draft with a slug made from the title

#### Scenario: Full post
- **WHEN** an editor fills in every field and publishes
- **THEN** every value is stored and shown again when the post is reopened

### Requirement: Publish date is editable
A blog post SHALL have a publish date that editors can set to any date,
including the past, independent of when it was actually published in the
CMS. A new post SHALL default to the current date and time.

#### Scenario: Backdated post
- **WHEN** an editor sets the publish date to 3 March 2021 and publishes today
- **THEN** the post's publish date is 3 March 2021

### Requirement: Featured flag
A blog post SHALL have a "Featured" flag, off by default, that marks it for
featured panels on the websites.

#### Scenario: Marking a post featured
- **WHEN** an editor ticks "Featured" and publishes
- **THEN** the post is stored as featured

### Requirement: Body uses only built-in blocks
The body SHALL offer exactly three block types: rich text, table, and HTML.
Rich text SHALL support paragraphs, headings h2 to h4, bold, italic, links,
ordered and unordered lists, block quotes, horizontal rules, inline code,
superscript, subscript, images and embeds.

#### Scenario: Block choice
- **WHEN** an editor adds a block to the body
- **THEN** the choices are "Rich text", "Table" and "HTML (advanced)"

#### Scenario: Image in text
- **WHEN** an editor inserts an image from the image library into rich text
- **THEN** the image is stored as a reference to that library image, with
  its alignment

#### Scenario: Video embed
- **WHEN** an editor inserts a YouTube URL as an embed in rich text
- **THEN** the embed is stored and shown in preview

### Requirement: HTML block keeps markup as written
The HTML block SHALL store its content exactly as entered, without cleaning
or rewriting it. Its label SHALL mark it as advanced.

#### Scenario: Vanilla button
- **WHEN** an editor saves an HTML block containing
  `<a class="p-button--positive" href="https://ubuntu.com/download">Download</a>`
- **THEN** the same markup is returned when the post is reopened

### Requirement: Featured image comes from the image library
The featured image SHALL be chosen from the CMS image library. Removing a
featured image SHALL NOT delete the image from the library.

#### Scenario: Image deleted from library
- **GIVEN** a post whose featured image is image A
- **WHEN** an admin deletes image A from the library
- **THEN** the post remains, with no featured image

### Requirement: Blog post listing in the admin
The admin SHALL have a "Blog posts" listing of all blog posts showing title,
status, author and last updated date. It SHALL filter by category, group,
author and live status, and search by title.

#### Scenario: Find drafts
- **WHEN** an editor filters the listing by live status "Draft"
- **THEN** only posts that are not live are listed

#### Scenario: Filter by group
- **WHEN** an editor filters by the group "AI"
- **THEN** only posts in the group "AI" are listed

### Requirement: Sample blog content for local review
Loading sample content SHALL create a blog index and sample categories,
groups (one with a parent), tags, authors (one with the local admin's
email) and posts covering live, draft, scheduled, featured,
in two site categories, and using every body block type. Loading it twice
SHALL NOT create duplicates.

#### Scenario: Seed twice
- **WHEN** sample content is loaded twice
- **THEN** the number of blog posts, terms and authors is the same as after
  the first load
