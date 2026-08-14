---
status: done
---

# Phase 3 - drawing

## Overview

`draw_face_landmarks` in `landmark/drawing.py`, alongside the pose and hand versions. Context:
[`00_start.md`](00_start.md), depends on [`02_result_helpers.md`](02_result_helpers.md) for the
connection accessors.

Small phase, and the one that makes every other phase checkable by eye once a model file exists.

## Goals

1. Annotate a `Frame` with face landmarks and return an RGB array, matching the signature style of
   `draw_pose_landmarks` and `draw_hand_landmarks`.
2. Make the mesh readable rather than dense by default.

## Plan

- `draw_face_landmarks(frame, detection_result, face_idx=0) -> np.ndarray`, copying the image and
  delegating to `mp_drawing_utils.draw_landmarks`, exactly as the existing two do.
- Default style comes from Q3: contours plus irises unless the answer says tesselation. Whichever it
  is, the other must be reachable - a keyword argument selecting among the three MediaPipe styles is
  enough, and is less machinery than exposing raw `DrawingSpec` objects.
- Follow `draw_pose_landmarks` on the empty case: log a warning and return the unannotated copy
  rather than raising. A frame with no face is normal input, not an error.
- The iris connections style is only meaningful when the model produced iris landmarks; with the
  face mesh model it always does, so no special-casing.

## Out of scope

- Drawing the transformation matrix as an axis triad. Useful for debugging head pose, and it needs
  camera intrinsics to project - which pose-tools does not have and abyss does. If it is wanted, it
  is an abyss debug view.
- Any change to the existing pose and hand drawing functions.

## Done when

- A face result renders onto a frame and the annotated array comes back with the same shape and
  dtype as the input.
- No face in the result produces a warning and an unannotated copy, not an exception.
- `make check` is green.
- Visual confirmation is deferred: it needs the model file and a sample clip with a face in it,
  which this box has neither of.
