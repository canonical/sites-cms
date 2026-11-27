# Spec Delta

## Purpose

Lets posts be sorted by category, group and tag, the three ways the websites
choose which posts to show, with stable slugs that sites can filter on.

## ADDED Requirements

### Requirement: Categories, groups and tags are managed in the admin
Editors SHALL be able to create, edit and delete categories, groups and tags
in the admin. Each SHALL have a name, a slug and an optional description.

#### Scenario: Create a tag
- **WHEN** an editor creates a tag named "Data platform"
- **THEN** the tag is saved with the slug `data-platform` unless the editor
  entered another slug

### Requirement: Slugs are unique per kind
Each category, group and tag SHALL have a slug unique among terms of the
same kind. Slugs SHALL accept non-ASCII characters. Names need not be
unique.

#### Scenario: Two groups with the same name
- **WHEN** an editor creates two groups named "Networking" with slugs
  `networking` and `networking-2`
- **THEN** both are saved

#### Scenario: Duplicate tag slug
- **GIVEN** a tag with slug `maas`
- **WHEN** an editor saves another tag with slug `maas`
- **THEN** the save is refused with a message that the slug is in use

#### Scenario: Same slug in different kinds
- **WHEN** a category and a group both use the slug `community`
- **THEN** both are saved

### Requirement: Slugs do not change on their own
A term's slug SHALL change only when someone edits the slug itself.
Renaming a term SHALL NOT change its slug.

#### Scenario: Rename a tag
- **GIVEN** a tag "MAAS" with slug `maas`
- **WHEN** an editor renames it to "Metal as a Service"
- **THEN** its slug is still `maas`

### Requirement: Groups can have a parent
A group SHALL optionally have one parent group. A group SHALL NOT be its own
ancestor.

#### Scenario: Nested group
- **WHEN** an editor sets the parent of "Kubeflow" to "AI"
- **THEN** "Kubeflow" is saved with parent "AI"

#### Scenario: Cycle refused
- **GIVEN** "Kubeflow" has parent "AI"
- **WHEN** an editor sets the parent of "AI" to "Kubeflow"
- **THEN** the save is refused with a message that it would create a loop

### Requirement: Posts are tagged with any number of terms
A blog post SHALL have any number of categories, groups and tags, including
none. Editors SHALL pick existing terms from a searchable list.

#### Scenario: Post on two sites
- **WHEN** an editor puts a post in the categories "Ubuntu tech blog" and
  "Canonical blog"
- **THEN** the post is stored with both categories

#### Scenario: Pick from many tags
- **GIVEN** 2,000 tags exist
- **WHEN** an editor adds a tag to a post
- **THEN** they can search tags by name and pick one, without scrolling a
  list of every tag

### Requirement: Order of groups and tags on a post is kept
The order of a post's groups and tags SHALL be stored and returned in the
order they were set.

#### Scenario: First group
- **WHEN** an editor sets a post's groups to "Security", then "AI"
- **THEN** the post's first group is "Security"

### Requirement: Terms in use cannot be deleted silently
Deleting a category, group or tag that is used by posts SHALL remove it from
those posts and SHALL NOT delete the posts. The admin SHALL show how many
posts use a term before it is deleted.

#### Scenario: Delete a used tag
- **GIVEN** a tag used by 12 posts
- **WHEN** an editor deletes it
- **THEN** the confirmation mentions the 12 posts, and after deleting, the
  12 posts still exist without that tag
