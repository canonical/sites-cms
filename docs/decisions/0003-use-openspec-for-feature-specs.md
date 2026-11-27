# 3. Feature specs are written with OpenSpec

Date: 2026-11-26 · Status: accepted

## Decision

How a feature behaves, and why, is recorded with OpenSpec, set up in this
repository with the `spec-driven` schema.

Each feature starts as a change in `openspec/changes/<name>/` with a
proposal, specs, a design and a task list, reviewed in the same pull request
as the code. When the change is merged and archived, its specs move into
`openspec/specs/`, which describes how the CMS behaves today.

Project-wide choices still go in this folder (see
[0001](0001-record-decisions.md)). A decision is recorded in one place only.

## Why

Feature decisions written only in pull request descriptions are hard to find
later and are never updated. OpenSpec keeps them in the repository, next to
the code, in a fixed shape that people and AI coding tools can both follow.

We did not use free-form design documents: without a fixed shape they drift
from the code and are rarely kept current.

## Consequences

- A feature pull request includes its OpenSpec change.
- The OpenSpec CLI and agent skills (`.agents/skills/openspec-*`) are needed
  to create, apply and archive changes.
