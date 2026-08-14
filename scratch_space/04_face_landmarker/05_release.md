---
status: planned
---

# Phase 5 - release

## Overview

Cut the tag abyss is waiting on. Context: [`00_start.md`](00_start.md), depends on phases 1-4.

Nothing new is built here. It exists as a phase because the v0.3.0 release had a near-miss worth not
repeating: a tag was created on the wrong branch and had to be undone.

## Goals

1. `v0.4.0` on `main`, pushed, dereferencing to the merge commit.
2. abyss repinned and verified against it.

## Plan

- Documentation first, while the code is fresh: `README.md` and `docs/` list the wrapped
  landmarkers, and a third one changes those lists. `docs/getting-started.md` documents where model
  files come from, which is where Q1's answer lands.
- `CHANGELOG.md`: a new `## [0.4.0]` section, `Added` only. Released sections above it are not
  rewritten.
- Version bump in `pyproject.toml`. Minor, not patch: new public API, no removals.
- Release sequence, in this order, checking the branch before each step:
  1. `make check` green on the feature branch
  2. merge to `main`, confirm `main` and `origin/main` agree
  3. annotated tag **on main**, verified with `git rev-parse v0.4.0^{}` before pushing
  4. hand the push over - this box has no GitHub credentials and cannot push
- Then in abyss: bump the pin to `v0.4.0`, `make sync`, `make check`, confirm the new imports
  resolve, commit on the abyss branch. Unblocks phase 1 there.

## Out of scope

- Any API addition that shows up late. It goes in the next tag; a release phase that grows features
  is how a release slips.

## Done when

- `git ls-remote --tags origin` shows `v0.4.0` pointing at the merge commit on `main`.
- abyss is pinned to it with `make check` green.
- The changelog entry says what shipped, not what was planned.
