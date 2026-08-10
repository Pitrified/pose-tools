# Changelog

All notable changes to this project are documented here.

Format: [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
Versioning: [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
