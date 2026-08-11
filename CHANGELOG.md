# Changelog

All notable changes to this project are documented here.

Format: [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
Versioning: [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [0.3.0] - 2026-08-11

Cleanup pass. Everything removed here was template scaffold or indirection that no code used;
`abyss`, the only consumer, imports none of it.

### Removed

- **The `load_env()` import side effect.** `import pose_tools` no longer reads
  `~/cred/pose-tools/.env`. `params/load_env.py` is gone with it, along with the `python-dotenv`
  dependency - it had no other user.
- **`geometry/landmark_geometry.py`.** It defined nothing: a re-export of
  `normalized_to_pixel_coordinates` and `are_valid_normalized_points`, both canonical in
  `utils/mediapipe.py`. Import them from there. It was announced in 0.1.0 as "geometric measures
  over landmark sets"; those measures were never written.
- **The environment and config scaffold** carried over from `python-project-template`:
  `params/env_type.py` (`EnvType`, `EnvStageType`, `EnvLocationType`, and their errors),
  `params/sample_params.py`, `config/`, `data_models/`, and `nokeys.env`. The `pydantic`
  dependency went with them.
- `tests/config/test_env_vars.py`, which asserted an environment variable set by `load_env()` and
  therefore passed or failed depending on whether the machine happened to have the cred file.

### Changed

- `PoseToolsPaths` takes no arguments and no longer dispatches on environment location. It resolves
  `src_fol`, `root_fol`, `cache_fol` and `data_fol` and nothing else. `PoseToolsParams` aggregates
  only the paths; `set_env_type()` is gone.
- Added a `Makefile`. Run project code through `make` or `uv run --no-sync`; a bare `uv run`
  re-syncs from `uv.lock` and reverts a local editable install.
- Docs updated to match: new `docs/guides/makefile.md` and `docs/guides/params.md`, replacing
  `docs/guides/params_config.md`. The mkdocs nav no longer points at a `guides/webapp_setup.md`
  that never existed.

### Migration

Anything importing `pose_tools.geometry.landmark_geometry` should import from
`pose_tools.utils.mediapipe` instead. Anything relying on `import pose_tools` to load a `.env` must
now load it itself. Within the fleet, nothing does either.

## [0.2.1] - 2026-08-10

### Added

- `BaseLandmarkerFrame.close()` and context manager support, so `PoseLandmarkerFrame` and
  `HandLandmarkerFrame` release their MediaPipe task deterministically:

  ```python
  with PoseLandmarkerFrame(model_path) as plf:
      result = plf.detect(frame)
  ```

  Without it the task was only released by the garbage collector, and under mediapipe 1.0.0 that
  surfaced at interpreter shutdown as `TypeError: 'NoneType' object is not callable` raised from
  MediaPipe's own `PoseLandmarker.__del__`. Measured: one such traceback per process before,
  none after. `close()` is idempotent.

- `LandmarkerClosedError`, raised by `detect()` on a closed landmarker rather than letting the
  call reach a released native object.

  Not calling `close()` still works exactly as before - this is opt-in.

---

## [0.2.0] - 2026-08-10

### Changed

- Require `mediapipe>=1.0` (was `>=0.10`), and lock 1.0.0.

  1.0.0 removes `mediapipe.python.solutions.*` and
  `mediapipe.framework.formats.landmark_pb2`. pose-tools never used either - it draws through
  `mediapipe.tasks.python.vision` - so no source change was needed. The old floor was misleading:
  it advertised support for 0.10.x while only 1.0.0 was ever tested, and it let consumers silently
  resolve across the major boundary.

  Consumers on 0.10.x must move to 1.0.0. Code that touches `mediapipe.python.solutions` or the
  protobuf landmark types will not survive that jump.

### Notes

- Verified on Python 3.14.4 with mediapipe 1.0.0: ruff clean, pyright 0 errors, 81 tests pass.
  The suite covers imports and pure-python logic; it does not run inference, which needs
  `.task` model files that are not in the repository.

---

## [0.1.0] - 2026-08-10

Initial release. Extracts and unifies the pose tracking code shared by `climbing-wire`,
`holo-table` and `abyss`, so consumers pin one implementation instead of keeping their own copies.

### Added

**Landmarks**

- `PoseLandmarkerFrame` / `HandLandmarkerFrame` - MediaPipe landmarkers that accept `Frame`
  objects, over a shared `base` implementation.
- `LandmarkArray` - numpy-backed landmark container with visibility masking.
- `ModelManager` - resolves and caches the MediaPipe `.task` model files.
- `distance` and `drawing` helpers for landmark sets.

**Video**

- `Frame` - a single frame with RGB/BGR conversions.
- `VideoFrameIterator` and loading helpers in `video/load.py`.

**Geometry**

- `homography` - projective transforms between planes.
- `landmark_geometry` - geometric measures over landmark sets.
- `SignalTracker` - smoothing and tracking of noisy per-frame signals.

**Utilities**

- `utils/cv.py`, `utils/plt.py` - OpenCV and matplotlib display helpers.
- `utils/mediapipe.py` - conversions between MediaPipe results and plain data.
- `utils/np_signal.py` - numpy signal helpers.

**Params / config**

- `PoseToolsParams` singleton + `PoseToolsPaths` - project-wide config and filesystem paths.
- `EnvType` enums and `load_env()`, reading `~/cred/pose-tools/.env`.
- `SampleParams` / `SampleConfig` - reference implementations of the pattern.
- `BaseModelKwargs`, `Singleton` - shared building blocks.

### Notes

- Requires Python 3.14. MediaPipe ships `py3-none` wheels, so no ABI-specific build is needed.
- Inference runs on the CPU delegate; no GPU code paths are provided.
