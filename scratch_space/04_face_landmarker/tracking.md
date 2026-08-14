# implementation tracking

Adding a face landmarker wrapper to pose-tools, so `abyss` can get eye positions and a head-pose
matrix out of a webcam. Analysis and decisions in [`00_start.md`](00_start.md).

## Key decisions

- **Third instance of an existing pattern.** `landmark/pose.py` and `landmark/hand.py` are
  near-identical; face copies their shape rather than introducing a new one. No refactor of the two
  existing wrappers is in scope - three near-identical files is the honest cost of a thin API.
- **Landmarks out, no interpretation.** pose-tools returns what MediaPipe produces. Eye midpoints,
  metric depth and smoothing are abyss's work. This is the boundary that the whole split exists to
  hold.
- **Face has no world landmarks.** Verified against MediaPipe 1.0.0: pose and hand both expose
  world landmarks, face does not. The `get_landmarks_from_result` overloads must not pretend
  otherwise, and metric information comes from `facial_transformation_matrixes` instead.
- **The model file is absent on this box.** Only the pose models are in `~/.mediapipe/models/`.
  Every phase below is written so it can be developed and tested without it; a real detection is a
  manual check, not part of `make check`.

## Phases

| #  | Phase                          | Plan                                                        | Status  |
| -- | ------------------------------ | ----------------------------------------------------------- | ------- |
| 1  | the wrapper                    | [`01_face_wrapper.md`](01_face_wrapper.md)                   | planned |
| 2  | result helpers and constants   | [`02_result_helpers.md`](02_result_helpers.md)               | planned |
| 3  | drawing                        | [`03_drawing.md`](03_drawing.md)                             | planned |
| 4  | tests                          | [`04_tests.md`](04_tests.md)                                 | planned |
| 5  | release                        | [`05_release.md`](05_release.md)                             | planned |

Status values: draft / planned / in progress / done / superseded / discarded.

Sequencing note: phases 1-3 are independent enough to reorder, but 1 comes first because it settles
the naming that 2 and 3 follow. Phase 4 could be interleaved; it is separate because Q4 may widen it
to cover the pose and hand wrappers too. Phase 5 needs all of them.

## Log

Append-only. Newest at the bottom.

- 2026-08-14 : bootstrapped from abyss's expansion plan (its Q1 chose the face landmarker, its Q14
  ruled that upstream work is tracked in its own repo). Read `landmark/base.py`, `pose.py`,
  `hand.py`, `model_manager.py`, `drawing.py` and `utils/mediapipe.py` before planning, and
  inspected the installed MediaPipe 1.0.0 rather than trusting the docs. Two findings shaped the
  phases: `FaceLandmarkerResult` has no world landmarks, unlike pose and hand, so the
  `get_landmarks_from_result` overload set is asymmetric by necessity; and `face_landmarker.task`
  is not on this box, so no phase may depend on running a real detection. Raised Q1-Q4.
- 2026-08-14 : corrected Q1. I had called the `feat/model-downloader` branch badly diverged, reading
  `git diff main..branch` as branch content when it is really main's v0.3.0 cleanup shown in
  reverse - the branch is based on v0.2.1. It is one commit, one 63-line planning file, no code,
  and `git merge-tree` reports no conflicts against `main`. Its plan already carries the CDN URL
  pattern and the `pose_landmarker_full.task` rename trap, so option 2 in Q1 is cheaper than stated.
