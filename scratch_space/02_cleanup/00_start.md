---
status: draft
---

# pose-tools cleanup - audit and trim

Requested while planning the abyss expansion
(`abyss/plans/01_abyss_expansion/00_start.md`), after the shim in
`geometry/landmark_geometry.py` surfaced. abyss is the only consumer, and it should be able to
import from where things actually live rather than through indirection.

Three asks: remove the `load_env` import side effect, remove the shims, and audit the general state
of the code before deciding what else to do.

## Audit

Taken on branch `chore/cleanup` at `d4e5c82` (v0.2.1). Baseline is green: ruff `All checks
passed!`, pyright `0 errors, 0 warnings, 0 informations`, pytest `90 passed`.

### Consumers

`abyss` is the **only** repo that depends on pose-tools. `climbing-wire` and `holo-table` have no
pose-tools entry in their `pyproject.toml`, so they still carry their own copies of this code.
abyss imports 7 symbols in total:

```text
video.load          VideoFrameIterator, list_video_frames
utils.plt           show_frame
utils.mediapipe     get_landmarks_from_result
landmark.pose       PoseLandmarkerFrame
landmark.model_manager  ModelManager
landmark.drawing    draw_pose_landmarks
```

This matters for the "would climbing-wire want it?" test used in both repos: it is a statement of
intent, not of current fact. Nothing enforces it today.

### Shims

One, repo-wide. `geometry/landmark_geometry.py`: 15 non-blank lines, zero definitions, the only
module in the package with `__all__`. It re-exports `normalized_to_pixel_coordinates` and
`are_valid_normalized_points` from `utils.mediapipe`, both of which are canonical there. Its own
docstring says it exists to "add higher-level geometric helpers as needed" - a namespace reserved
for code never written. Its test is `test_reexports_are_callable`. Nothing imports it, in this repo
or in abyss.

Every other intra-package import is genuine consumption (`landmark_array` uses `utils.mediapipe`,
`signal_tracker` uses `np_signal`, `plt` uses `cv` and `video.frame`).

### Import side effect

`src/pose_tools/__init__.py` is three lines: import `load_env`, then call it. So `import
pose_tools` reads `~/cred/pose-tools/.env` off the user's home folder.

This has a concrete consequence. `tests/config/test_env_vars.py` asserts
`POSE_TOOLS_SAMPLE_ENV_VAR` is in `os.environ`, and it passes on this box **only** because that
cred file happens to exist here. `tests/conftest.py` does not set the variable (it sets
`SAMPLE_API_KEY` only). On a fresh clone with no `~/cred/pose-tools/.env`, that test fails. The
suite is not reproducible.

### Template scaffold still present

pose-tools has no secrets and runs in one place, the same situation abyss was in before its reboot.
Carried over from `python-project-template` and used by nothing but their own tests:

| File | Lines | Used by |
| ---- | ----- | ------- |
| `params/env_type.py` | 78 | `pose_tools_paths`, `sample_params`, `sample_config` |
| `params/sample_params.py` | 172 | its own test |
| `config/sample_config.py` | 62 | `sample_params`, its own test |
| `data_models/basemodel_kwargs.py` | 34 | `sample_config`, its own test |
| `nokeys.env` | 1 var | `test_env_vars` |

`params/pose_tools_paths.py` dispatches on `EnvLocationType.LOCAL / RENDER`; nothing runs on
Render. The `pydantic` and `python-dotenv` dependencies exist only for this scaffold.

The user's answer on scope was **side effect only** for now: drop the `load_env()` call from
`__init__.py`, keep the module callable. The rest of the scaffold is reported here for a separate
decision (Q7).

### Test coverage

90 tests, but concentrated on the parts that need them least. The MediaPipe layer - the reason the
library exists - has **no tests at all**:

| Module | Tests |
| ------ | ----- |
| `landmark/pose.py` (`create_pose_landmarker`, `PoseLandmarkerFrame`) | none |
| `landmark/hand.py` (`create_hand_landmarker`, `HandLandmarkerFrame`) | none |
| `landmark/drawing.py` (`draw_pose_landmarks`, `draw_hand_landmarks`) | none |
| `utils/plt.py` (`show_frame`) | none |
| `params/load_env.py` | none |

`utils/mediapipe.get_landmarks_from_result` carries six `@overload` signatures and has no direct
test either, though `test_mediapipe.py` covers its neighbours. `utils/cv.cv_imshow` and
`cv_imshow_rgb` are untested, which is defensible - they need a display.

`tests/` mirrors `src/` unevenly: `tests/config/`, `geometry/`, `landmark/`, `utils/`, `video/` and
the root have `__init__.py`; `tests/data_models/`, `metaclasses/` and `params/` do not.

The reachable gap is `landmark/pose.py` and `hand.py`. `test_base.py` already fakes the MediaPipe
task with `FakeTask`/`FakeLandmarker`, so the same approach extends to the subclasses without a
model file or a GPU.

### Docs vs reality

- `mkdocs.yml` nav points at `guides/webapp_setup.md`, which **does not exist**. `docs/` holds
  `index.md`, `getting-started.md`, `contributing.md`, and `guides/{uv,pre_commit,params_config}.md`.
- The `README.md` opening claims the library "Extracts and unifies shared code from
  `climbing-wire`, `holo-table`, and `abyss`". Only abyss consumes it; the other two are aspiration.
- `README.md` documents `~/cred/pose-tools/.env` as setup. If the side effect goes, this needs to
  say who calls `load_env` instead.
- `README.md` gives bare `uv run pyright` / `uv run ruff check .` / `uv run pytest`. Bare `uv run`
  re-syncs from `uv.lock` first, which silently reverts a local editable install - the exact trap
  documented in abyss. pose-tools has **no Makefile**; abyss and the template both got one.
- `CHANGELOG.md` v0.1.0 lists `landmark_geometry - geometric measures over landmark sets`, which
  describes capability that was never written.

## Open questions

Numbering continues from the abyss expansion plan is *not* shared - this is a separate initiative,
so it starts at Q1.

- Q1: **Does the rest of the template scaffold go?** `env_type`, `sample_params`, `sample_config`,
  `basemodel_kwargs`, `nokeys.env`, plus flattening `pose_tools_paths` to no env dispatch, and
  dropping the `pydantic` / `python-dotenv` deps. This is what abyss did in its reboot. It is
  breaking for anything importing them - nothing does. Answered "side effect only" for the
  narrower question; this is the wider one, asked separately.
  ANS: ...
- Q2: **What happens to `test_env_vars.py`?** It is machine-dependent and fails on a fresh clone.
  Delete it, or move the variable into `conftest.py` so it tests nothing external?
  ANS: ...
- Q3: **Do the landmarker tests land in this cleanup, or as their own feature?** Faking the
  MediaPipe task for `pose.py` and `hand.py` is real work, not a trim.
  ANS: ...
- Q4: **Makefile now, or later?** The abyss and template Makefile exists and would port with the
  name changed. It is the cure for the bare `uv run` in the README, but it is scope growth on a
  cleanup.
  ANS: ...
- Q5: **Version number for the release.** Removing the import side effect changes observable
  behaviour for anyone relying on it (nobody does, on the evidence). v0.2.2, or v0.3.0?
  ANS: ...

## Out of scope

- The face landmarker for the abyss expansion. That is `abyss/plans/01_abyss_expansion` phase 0,
  and it waits on abyss's own Q1.
- The model downloader helper, already parked on `feat/model-downloader`.
