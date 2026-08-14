---
status: done
---

# Phase 2 - docs and changelog

## Overview

Write down that the manual curl step is gone. Context: [`00_start.md`](00_start.md), depends on
phase 1.

The original plan noted the manual step was "written down in `abyss`'s README and in
`~/data/pose/README.md` on the dev box". Those instructions become wrong the moment phase 1 lands,
which is the actual reason this phase exists.

## Plan

- `docs/getting-started.md`: a "Model files" section. Where they live (`~/.mediapipe/models`), how
  to get them (`ensure_model`), and which variants exist with their sizes, since a 30 MB heavy pose
  model is worth knowing about before downloading it.
- `README.md`: mention that models can be fetched, if it lists capabilities at that level.
- `CHANGELOG.md`: an `Unreleased` section with the additions. It becomes the version section when
  the face work releases, rather than tagging twice for two halves of one capability.
- The abyss README still documents the curl command. Left alone deliberately: it is a different
  repo, it is not wrong until abyss pins a version with `ensure_model` in it, and that pin happens
  in the face initiative's release phase. Recorded here so it is not forgotten.

## Out of scope

- A docs page of its own for model management. One section in getting-started is proportionate to
  one method.

## Done when

- Someone setting up a fresh box can find the model instructions without reading source.
- `make docs-build` passes, which fails on any warning including a broken link.
- The changelog says what shipped.
