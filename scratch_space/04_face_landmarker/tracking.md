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
- **~~The model file is absent on this box.~~** True when this was planned, and the reason every
  phase was written to be developable without it. Q1 resolved it by building the downloader first,
  so `ensure_model("face_landmarker")` now supplies the model and `~/data/pose/face01.mp4` supplies
  a face. The constraint still holds for a fresh clone, so `make check` remains model-free and a
  real detection remains a manual check.

## Phases

| #  | Phase                          | Plan                                                        | Status  |
| -- | ------------------------------ | ----------------------------------------------------------- | ------- |
| 1  | the wrapper                    | [`01_face_wrapper.md`](01_face_wrapper.md)                   | done    |
| 2  | result helpers and constants   | [`02_result_helpers.md`](02_result_helpers.md)               | done    |
| 3  | drawing                        | [`03_drawing.md`](03_drawing.md)                             | done    |
| 4  | tests                          | [`04_tests.md`](04_tests.md)                                 | done    |
| 5  | release                        | [`05_release.md`](05_release.md)                             | done    |

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
- 2026-08-14 : Q1 answered by building the downloader first (`../01_model_downloader/`), which
  removed the "no model on this box" constraint before implementation started. Q2 keeps the
  transformation matrix off by default, Q3 draws contours plus irises, Q4 widens the test phase to
  all three wrappers and supersedes `../03_landmarker_tests/`.
- 2026-08-14 : phases 1-4 done on `feat/face-landmarker`. `landmark/face.py` mirrors `hand.py`;
  `utils/mediapipe.py` gains a face overload, `get_facial_transformation_matrix()`, three connection
  accessors and the iris constants; `drawing.py` gains `draw_face_landmarks`. Tests went from 82 to
  127, covering the three wrappers from one parametrised fixture plus the drawing helpers, none of
  them needing a model file. `make check` green.
  Findings worth keeping. The iris **centres**, 468 and 473, appear in no MediaPipe connection
  table - only the four-point rings do - so they are unreachable unless named, which is exactly what
  abyss needs for an eye position. Writing the wrapper tests through a recording factory rather than
  reading `_landmarker` off the instance avoided six `SLF001` findings and pins public behaviour
  instead of internals. The pose branch's bare `ValueError` became `UnsupportedLandmarkInfoError`,
  which my own phase-2 plan had put out of scope: it sits inside the function being changed and
  subclasses `ValueError`, so it is a one-line consistency fix rather than a separate cleanup.
  **Ceiling, named:** `FACE_LANDMARK_COUNT = 478` is still derived from the connection tables (max
  index 477, plus the two centres no table mentions), not from a live detection. A blank frame
  yields no face, and the only clip on this box (`yoga01.mp4`, 299 frames) contains no detectable
  face anywhere in it - checked across the whole clip, including at
  `min_face_detection_confidence=0.2`. One webcam frame on g7 closes this.
- 2026-08-14 : **ceiling closed, no webcam needed.** Fetched a second sample clip the same way
  `yoga01.mp4` was made: a CC BY 3.0 Royal Society interview from Wikimedia Commons, first 25 MB by
  HTTP range request, first 10 seconds re-encoded to mp4 with OpenCV, saved as
  `~/data/pose/face01.mp4` and documented in that folder's README (attribution required if it is
  ever redistributed). Measured against it: a face in **250 of 250** frames, **478 landmarks in
  every one**, and a 4x4 transformation matrix in every frame with the option on. So
  `FACE_LANDMARK_COUNT` is now confirmed by detection rather than inferred from the connection
  tables. The iris centres land where they should - x=0.468 and x=0.530 on a centred face, one per
  eye. Both drawing modes were rendered and inspected: contours plus irises reads clearly, the
  tesselation buries the iris markers in the mesh, which is the case for the default Q3 chose.
  The clip stays out of git; it is a local asset like `yoga01.mp4`, and no test depends on it.
- 2026-08-14 : phase 5, released as `v0.4.0`. One release covering both the downloader and the face
  landmarker, since a landmarker nobody can fetch a model for is half a capability. Version bumped,
  the changelog's `Unreleased` section became `0.4.0`, `make check` green on the branch before the
  merge, and the annotated tag was created on `main` and verified to dereference to the merge commit
  before being handed over for pushing - the v0.3.0 near-miss was a tag on the wrong branch.
