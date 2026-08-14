---
status: done
---

# Phase 4 - tests

## Overview

Cover the face code without a `.task` file, a GPU, or a display. Context:
[`00_start.md`](00_start.md), depends on phases 1-3.

The scope of this phase is set by Q4: face only, or face plus the pose and hand wrappers that
[`../03_landmarker_tests/`](../03_landmarker_tests/) was spun off to cover.

## Goals

1. The face wrapper is tested to the same depth `BaseLandmarkerFrame` already is.
2. The result helpers are tested against a fake result, including the paths that must fail.
3. Nothing in the suite requires a model file, so a fresh clone runs it green.

## Plan

- Reuse the approach in `tests/landmark/test_base.py`: a `FakeTask` with `detect` /
  `detect_for_video` / `close`, and a concrete subclass over it. That file already proves the
  pattern gets nine tests out of the base class with no native dependency.
- `tests/landmark/test_face.py`: construction stores the running mode, `detect` dispatches on it,
  `close` is idempotent, use-after-close raises `LandmarkerClosedError`. Constructing the real task
  is the one thing not covered - `create_face_landmarker` needs a model file, so it is patched or
  left to a manual check.
- `tests/utils/test_mediapipe.py` gains face cases against a hand-built fake result object: a
  normalized lookup, an out-of-range index returning `None`, `"world"` raising, and the matrix
  accessor returning `None` when the field is an empty list. That last one is the real bug bait.
- Drawing tests assert shape and dtype of the returned array and that the source frame is not
  mutated, which is what `np.copy` in the existing functions is there to guarantee.
- If Q4 widens this, the same fixtures extend to `test_pose.py` and `test_hand.py` with the task
  type swapped, and `03_landmarker_tests` gets marked superseded rather than left dangling.

## Out of scope

- Integration tests that run a real detection. They need the model file (Q1) and a sample video
  with a face, and they belong behind a skip marker if they are ever added.
- `utils/cv.py` and `utils/plt.py`, which need a display. Still untested, still a separate problem.

## Done when

- `make test` passes on a machine with no MediaPipe models present, which is the honest test of this
  phase, and can be checked here by pointing `ModelManager` at an empty directory.
- The face code paths that raise are exercised, not just the happy ones.
- `make check` is green.
