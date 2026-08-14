---
status: draft
---

# Landmarker tests

Spun off from the cleanup audit, [`../02_cleanup/00_start.md`](../02_cleanup/00_start.md), per its
Q3: writing these is real work, not a trim, so it does not belong in that cleanup.

## What it is

pose-tools has 90 tests and none of them touch the MediaPipe layer the library exists for:

| Module | Public surface | Tests |
| ------ | -------------- | ----- |
| `landmark/pose.py` | `create_pose_landmarker`, `PoseLandmarkerFrame` | none |
| `landmark/hand.py` | `create_hand_landmarker`, `HandLandmarkerFrame` | none |
| `landmark/drawing.py` | `draw_pose_landmarks`, `draw_hand_landmarks` | none |
| `utils/mediapipe.py` | `get_landmarks_from_result` (6 overloads) | none direct |

`utils/cv.py`'s `cv_imshow` / `cv_imshow_rgb` and `utils/plt.py`'s `show_frame` are also untested,
but they need a display and this box is headless - a separate problem, not obviously worth solving.

## Why it is tractable

`tests/landmark/test_base.py` already fakes the native task with `FakeTask` / `FakeLandmarker` and
gets 9 tests out of `BaseLandmarkerFrame` without a `.task` model file or a GPU. `PoseLandmarkerFrame`
and `HandLandmarkerFrame` are thin subclasses of it, so the same fixture approach reaches them.

`create_pose_landmarker` / `create_hand_landmarker` do touch real MediaPipe options objects, so they
need either a real model file (present on this box via `ModelManager`, absent on a fresh clone) or a
patched constructor. That choice is the first thing to settle when this is picked up.

## Open questions

- Q1: **Do the tests that need a real `.task` file get skipped, or is everything faked?** A skip
  marker keyed on `ModelManager` finding the model keeps a real integration path available where the
  models exist. Full faking keeps CI honest but tests less.
  ANS: ...

## Possibly superseded

[`../04_face_landmarker/`](../04_face_landmarker/) asks the same question as its own Q4: its test
phase builds exactly the fixtures this initiative needs, and covering the pose and hand wrappers at
the same time is barely more work. If that answer says yes, this folder becomes `superseded` and the
work happens there.
