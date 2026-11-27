# Spec Delta

## Purpose

Keeps bylines for everyone who has written a post, including people who will
never have an account, and links each byline to the right user account
without anyone running a command.

## ADDED Requirements

### Requirement: Authors are separate from user accounts
The system SHALL keep authors as their own records with a name, a unique
slug, a job title, a bio, a photo from the image library and an email. An
author SHALL NOT need a user account. A blog post SHALL have at most one
author.

#### Scenario: Author without an account
- **WHEN** an admin creates the author "Canonical" with no email
- **THEN** the author is saved and can be chosen as a post's author

### Requirement: Authors in use cannot be deleted
Deleting an author SHALL be refused while any blog post uses that author.

#### Scenario: Delete a used author
- **GIVEN** an author with 3 posts
- **WHEN** an admin tries to delete the author
- **THEN** the deletion is refused, and the screen says the author is used
  3 times, with a link to the list of those posts

### Requirement: Author emails are private
An author's email SHALL be visible only to users who can edit authors.

#### Scenario: Editor without author permissions
- **WHEN** a user without permission to edit authors opens a blog post
- **THEN** they see the author's name but not the author's email

### Requirement: Link on author save
When an author with an email and no linked account is saved, the system
SHALL link it to the user whose email matches, ignoring case.

#### Scenario: Account exists first
- **GIVEN** a user with email `Jane.Doe@canonical.com`
- **WHEN** an author with email `jane.doe@canonical.com` is saved
- **THEN** the author is linked to that user

### Requirement: Link on account creation
When a user account is created, the system SHALL link it to every unlinked
author whose email matches the user's email, ignoring case.

#### Scenario: Author exists first
- **GIVEN** two unlinked authors with email `jane.doe@canonical.com`
- **WHEN** a user with email `jane.doe@canonical.com` is created
- **THEN** both authors are linked to that user

### Requirement: Link on sign-in
When a user signs in, the system SHALL link them to every unlinked author
whose email matches the user's email, ignoring case.

#### Scenario: Email changed after account creation
- **GIVEN** a user whose email was changed to `jane.doe@canonical.com`
  after their account was created
- **WHEN** the user signs in
- **THEN** unlinked authors with that email are linked to them

### Requirement: Automatic linking never replaces a link
Automatic linking SHALL only fill an empty link. It SHALL NOT change an
author already linked to an account.

#### Scenario: Already linked by hand
- **GIVEN** an author linked by hand to user A
- **WHEN** user B with the same email as the author signs in
- **THEN** the author is still linked to user A

### Requirement: Admins can link by hand
An admin SHALL be able to link an author to any user, or remove the link,
from the author's edit screen.

#### Scenario: Personal email in the old system
- **GIVEN** an author whose email does not match any account
- **WHEN** an admin picks user A in "Linked account" and saves
- **THEN** the author is linked to user A

### Requirement: Linking gives the user ownership of unowned posts
When an author is linked to a user, the system SHALL make that user the
owner of the author's blog posts that have no owner. Posts that already have
an owner SHALL keep it.

#### Scenario: Imported posts get an owner
- **GIVEN** an author with 5 posts that have no owner
- **WHEN** the author is linked to user A
- **THEN** user A owns the 5 posts

### Requirement: Byline does not depend on the link
A post's byline SHALL come from the author record whether or not the author
is linked to an account.

#### Scenario: Linked user renamed
- **GIVEN** an author "Jane Doe" linked to a user named "J. Doe"
- **WHEN** a post by that author is opened
- **THEN** the byline is "Jane Doe"
