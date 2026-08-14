---
status: done
---

# Phase 1 - the wrapper

## Overview

`landmark/face.py`, built to the shape `pose.py` and `hand.py` already share, plus the model
resolution entry that makes the `.task` file findable. Context: [`00_start.md`](00_start.md).

This is the phase that decides naming for everything after it, which is why it is first.

## Goals

1. `create_face_landmarker(model_path, **kwargs) -> FaceLandmarker`.
2. `FaceLandmarkerFrame(BaseLandmarkerFrame[FaceLandmarkerResult])`, accepting `Frame` objects.
3. `face_landmarker` resolvable through `ModelManager`.

## Plan

- ~~Add to `landmark/model_manager.py`: `"face_landmarker"` in the `ModelType` literal and
  `"face_landmarker.task"` in `MODEL_FILENAMES`.~~ **Done upstream** by
  [`../01_model_downloader/`](../01_model_downloader/), which needed the entry to fetch the file.
  `ModelManager().ensure_model("face_landmarker")` already works.
- Write `landmark/face.py` mirroring `hand.py` line for line, substituting the face task:
  - imports from `mediapipe.tasks.python.vision.face_landmarker`
  - `create_face_landmarker` builds `BaseOptions(model_asset_path=str(model_path))` then
    `FaceLandmarkerOptions(base_options=..., **kwargs)`
  - `FaceLandmarkerFrame.__init__(model_path, landmarker_kwargs=None)` reads `running_mode` from the
    kwargs with `VisionRunningMode.IMAGE` as the default, then builds the task
  - `detect(frame)` overrides only to narrow the return type, as the other two do
- Docstrings name the useful options explicitly, since they are the reason the class exists:
  `num_faces`, `output_facial_transformation_matrixes`, `output_face_blendshapes`.
- Q2 decides whether the transformation matrix option is defaulted on. Until it is answered, write
  the faithful pass-through (MediaPipe's own default) and leave the alternative to the answer -
  changing it later is a one-line change plus a changelog note.

## Out of scope

- Extracting anything from the result: phase 2.
- Drawing: phase 3.
- Tests: phase 4, though the code must be written so the existing `FakeTask` approach reaches it,
  which it will by construction if the pattern is followed.
- Refactoring `pose.py` / `hand.py` to share the duplicated body. Tempting with a third copy in
  front of us, and still wrong: the duplication is six lines of constructor, and a shared factory
  would have to be generic over three different options types for no gain.

## Done when

- `from pose_tools.landmark.face import FaceLandmarkerFrame` works.
- `make check` is green: ruff with `select = ["ALL"]`, pyright, pytest.
- A real `FaceLandmarkerFrame` is constructed against the downloaded model and closes cleanly. This
  **is** an exit criterion now that Q1 is settled and the model is present; the earlier version of
  this plan deferred it for want of a file.
