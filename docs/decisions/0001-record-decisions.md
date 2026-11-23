# 1. Record project-wide decisions here

Date: 2026-11-23 · Status: accepted

## Decision

Each project-wide choice gets one short file in this folder, numbered in
order: `NNNN-short-title.md`.

A project-wide choice is a tool, a version, or a rule that is not the
behaviour of one feature. "We use PostgreSQL only" belongs here. "Writers
cannot publish" does not: that is how a feature behaves, and it is recorded
with that feature's spec.

A decision is recorded in one place only.

## Format

```
# N. Title that states the decision

Date: YYYY-MM-DD · Status: accepted | superseded by NNNN

## Decision
What we chose, in a few sentences.

## Why
The reasons, and what we chose not to do.

## Consequences
What this makes easier or harder. Optional.
```

Keep it short. Do not edit an accepted decision to change it: add a new
file and mark the old one superseded.

## Why

Six months from now someone will ask "why don't we just use SQLite for
tests?". The answer should take one minute to find and should not depend on
who is still on the team.
