---
status: draft
---

# Face landmarker

Requested by `abyss`, which needs a metric eye position to build a head-coupled projection. Its
plan (`abyss/plans/01_abyss_expansion/00_start.md`, Q1) settled on the face landmarker over the pose
one, and phase 1 there blocks on the tag this initiative produces. The work itself is pose-tools
work: MediaPipe wrangling that `climbing-wire` would want too, which is the boundary test.

## Why face and not pose

`PoseLandmarkerFrame` already exists and reports a nose, eyes and ears among its 33 body landmarks.
They are too coarse to build a projection from, and pose gives no head orientation. The face task
gives three things pose cannot:

- **478 landmarks** including irises. The iris is the closest thing to a directly observable eye
  position, and its apparent size is a usable scale reference. Counted from the connection tables
  rather than taken from the docs: the tesselation spans indices 0-467, and the two iris groups add
  468-477, four points each.
- **`facial_transformation_matrixes`** - a 4x4 head pose relative to the camera, off by default,
  enabled by an option.
- **`face_blendshapes`** - expression coefficients, off by default. Nothing here needs them; they
  are listed because the wrapper must not silently exclude them.

## What exists to build on

The pattern is fixed and this must not invent a new one. `landmark/pose.py` and `landmark/hand.py`
are near-identical: a module-level `create_*_landmarker(model_path, **kwargs)` that builds
`BaseOptions` then `*Options`, and a `*LandmarkerFrame` subclass of `BaseLandmarkerFrame[ResultT]`
that reads `running_mode` out of `landmarker_kwargs` and stores the task. `BaseLandmarkerFrame`
owns detect-dispatch, `close()`, and the context manager. Face is a third instance of that, nothing
more.

Verified against the installed MediaPipe (1.0.0), so the plan is not guessing:

| Thing | Reality |
| ----- | ------- |
| `FaceLandmarkerOptions` | `num_faces`, `min_face_detection_confidence`, `min_face_presence_confidence`, `min_tracking_confidence`, `output_face_blendshapes`, `output_facial_transformation_matrixes`, plus the usual `base_options` / `running_mode` / `result_callback` |
| `FaceLandmarkerResult` fields | `face_landmarks`, `face_blendshapes`, `facial_transformation_matrixes` |
| Connections | `FaceLandmarksConnections` has `FACE_LANDMARKS_TESSELATION`, `_CONTOURS`, `_FACE_OVAL`, `_LEFT_EYE`, `_RIGHT_EYE`, `_LEFT_IRIS`, `_RIGHT_IRIS`, `_LIPS`, `_NOSE`, eyebrows |
| Drawing styles | `get_default_face_mesh_tesselation_style`, `_contours_style`, `_iris_connections_style` |

Two consequences worth stating early, because they break the symmetry with pose and hand:

- **There are no face world landmarks.** Pose has `pose_world_landmarks`, hand has
  `hand_world_landmarks`, face has only `face_landmarks` (normalized). So a `"world"` overload of
  `get_landmarks_from_result` cannot exist for face, and the metric information lives in the
  transformation matrix instead.
- **The model file is not on this box.** `~/.mediapipe/models/` holds `pose_landmarker.task` and
  `pose_landmarker_full.task` only. Nothing can be run end to end here until
  `face_landmarker.task` is fetched - see Q1.

## Scope

In:

- `landmark/face.py`: `create_face_landmarker`, `FaceLandmarkerFrame`.
- `face_landmarker` in `ModelManager.MODEL_FILENAMES` and the `ModelType` literal.
- Face support in `utils/mediapipe.py`: landmark constants, connections accessor, a `get_landmarks_from_result` overload.
- `draw_face_landmarks` in `landmark/drawing.py`.
- Tests, following the existing fake-task pattern.
- A release: changelog, tag, so abyss can pin it.

Out:

- **Anything that turns landmarks into a viewer position.** Eye midpoint, metric depth from iris
  size, smoothing choices - that is abyss's phase 1. pose-tools hands over landmarks and matrices.
- Retrofitting tests for the pose and hand wrappers. That is
  [`../03_landmarker_tests/`](../03_landmarker_tests/), still unstarted - see Q4.
- A model downloader, unless Q1 says otherwise. It exists as a deferred plan in
  `scratch_space/01-model-downloader/`, which lives on the unmerged `feat/model-downloader` branch:
  one commit, one file, no code, and it merges into `main` with no conflicts. Nothing about it is
  stale except its base commit.

## Open questions

- Q1: **How does `face_landmarker.task` get onto a machine?** It is not here, and `ModelManager`
  only resolves and validates paths. Two options:

  1. Fetch it by hand with `curl` and document that, consistent with how the pose model arrived.
     The URL follows the pattern the downloader plan already recorded:
     `https://storage.googleapis.com/mediapipe-models/face_landmarker/face_landmarker/float16/latest/face_landmarker.task`.
     No rename needed here, unlike the pose model.
  2. Build the deferred downloader now. Its plan is written, it is one unmerged doc commit that
     rebases onto `main` cleanly, and it names its own open decisions: variant naming, checksums,
     and whether a library may touch the network at all.

  Worth noting that its own deferral criterion has arguably just been met - it says pick it up "when
  a second machine needs setting up, or when a consumer wants to choose a variant at runtime", and
  a third model type on a box that has none of it is the same class of problem. Against that: it
  brings three open decisions of its own into an initiative that already has four.
  ANS: ...
- Q2: **Should the wrapper default `output_facial_transformation_matrixes` to `True`?** MediaPipe
  defaults it off. abyss wants it on, and it is the reason face was chosen. Leaving it off keeps
  the wrapper a faithful pass-through and costs abyss one kwarg; turning it on makes the wrapper
  opinionated and imposes the compute on every consumer, including ones that only want landmarks.
  ANS: ...
- Q3: **What does `draw_face_landmarks` draw by default?** Tesselation is 2556 connections over the
  468 mesh points and is visually dense; contours plus irises is the more readable default and is
  what the eye work
  actually cares about. Either way the other styles stay reachable through an argument.
  ANS: ...
- Q4: **Does this absorb `03_landmarker_tests`?** Writing face tests means building exactly the
  fixtures that initiative needs, and the pose and hand wrappers are thin enough that covering all
  three at once is barely more work than covering one. Alternatively face tests are written here in
  isolation and `03` stays as it is for later.
  ANS: ...

## The boundary, restated

pose-tools exposes what MediaPipe produces, in the shapes the rest of the fleet can consume. abyss
turns that into a viewer position and a frustum. If a function needs to know about screens, eyes as
a viewpoint, or projection, it is in the wrong repo.

`pose-tools` must never import `abyss`.
