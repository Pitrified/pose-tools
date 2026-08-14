---
status: planned
---

# Phase 2 - result helpers and constants

## Overview

Make a `FaceLandmarkerResult` usable without every consumer reaching into MediaPipe's containers by
hand. Context: [`00_start.md`](00_start.md), depends on
[`01_face_wrapper.md`](01_face_wrapper.md) for naming.

This is the phase where the asymmetry with pose and hand has to be handled honestly rather than
papered over.

## Goals

1. Face landmarks reachable through the same `get_landmarks_from_result` entry point.
2. Iris and eye landmark groups reachable by name, not by magic index.
3. The transformation matrix reachable without knowing it is a list.

## Plan

- `utils/mediapipe.py` gains a face overload of `get_landmarks_from_result`:
  - `Literal["normalized"]` only, returning `list[NormalizedLandmark] | None`
  - **no** `"world"` overload: `FaceLandmarkerResult` has no world landmarks, verified against the
    installed MediaPipe. Asking for `"world"` on a face result must raise, in the same shape as the
    existing `"handedness"`-on-a-pose-result error, with a named exception rather than a bare
    `ValueError` (repo rule; the existing pose branch predates it and is not in scope to fix here).
  - the runtime body currently branches on `isinstance(result, HandLandmarkerResult)` with pose as
    the `else`. Adding a third type means an explicit `isinstance` per type and no implicit else -
    otherwise a face result silently takes the pose path and fails on a missing attribute.
- `get_default_face_connections()` next to the existing pose and hand accessors, returning
  `FaceLandmarksConnections.FACE_LANDMARKS_CONTOURS`. Tesselation and the per-feature groups get
  their own accessors rather than a mode argument, matching the flat style of the module.
- Constants: `FACE_LANDMARK_COUNT` (478) and named index groups for the irises and eyes, derived
  from `FaceLandmarksConnections` rather than hardcoded. abyss needs the irises specifically, and a
  consumer should not have to look up an iris index in a blog post. One trap, measured rather than
  assumed: the tesselation table only spans 0-467, so deriving the count from it alone gives 468.
  The irises are 468-477 and appear only in `FACE_LANDMARKS_LEFT_IRIS` / `_RIGHT_IRIS`, four points
  each. The count has to come from the union of the groups, or be asserted against a real result.
- A small accessor for `facial_transformation_matrixes[idx]` returning a `(4, 4)` numpy array or
  `None`, since the field is an empty list when the option is off. That empty-list-versus-missing
  distinction is exactly the sharp edge worth wrapping once.

## Out of scope

- Blendshapes. Nothing in the fleet consumes expressions today; add an accessor when something does.
- Any interpretation of the matrix: decomposing it into rotation and translation, or deriving a
  viewer position from it. That is abyss's phase 1, and drawing that line is the point of the split.
- Refactoring the existing overload set beyond adding to it.

## Done when

- `get_landmarks_from_result(face_result, "normalized")` returns the landmark list, and `"world"`
  raises a named, descriptive error.
- Iris landmarks are reachable by name from `pose_tools.utils.mediapipe`.
- The matrix accessor returns `None` rather than raising when the option was off.
- `make check` is green, and pyright accepts the widened overload set (the most likely place this
  phase fails).
