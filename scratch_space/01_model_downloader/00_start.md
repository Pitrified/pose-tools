---
status: draft
---

# ModelManager: fetch the models, do not just name them

Deferred, not scheduled. Recorded while setting up `abyss` on a fresh box, 2026-08-10, where the
missing model file was the last thing standing between a clean repo and a working notebook.

## The gap

`ModelManager` knows the filenames and the directory:

```python
DEFAULT_MODEL_DIR = Path.home() / ".mediapipe" / "models"
MODEL_FILENAMES: dict[ModelType, str] = {
    "pose_landmarker": "pose_landmarker.task",
    "hand_landmarker": "hand_landmarker.task",
}
```

It does not know where the files come from. `get_model_path()` raises `ModelNotFoundError` with a
link to the MediaPipe solutions page, which is honest but leaves every consumer to work out the
CDN URL, pick a variant, and rename the download by hand. That is a manual setup step repeated per
machine, per consumer repo (`abyss`, `climbing-wire`, `holo-table`), and it is undocumented apart
from prose in each README.

What that step actually is, from doing it once:

```bash
curl -sSL -o ~/.mediapipe/models/pose_landmarker_full.task \
  https://storage.googleapis.com/mediapipe-models/pose_landmarker/pose_landmarker_full/float16/latest/pose_landmarker_full.task
cp ~/.mediapipe/models/pose_landmarker_full.task ~/.mediapipe/models/pose_landmarker.task
```

Note the rename: the CDN ships `pose_landmarker_full.task`, `ModelManager` expects
`pose_landmarker.task`. That mismatch is its own small trap.

## Sketch

- A URL table beside `MODEL_FILENAMES`, keyed by `(ModelType, variant)`. Variants that exist today:
  `lite` / `full` / `heavy` for pose, `float16` / `float32` precision, under
  `https://storage.googleapis.com/mediapipe-models/<model>/<variant>/<precision>/latest/`.
- `ModelManager.ensure_model(model_type, variant="full")` - return the path if present, otherwise
  download to the model dir and return it. Explicit call, never an implicit download inside
  `get_model_path()`: a library that reaches for the network without being asked is a surprise in
  a test suite.
- Decide whether the stored filename keeps the variant (`pose_landmarker_full.task`) with a lookup
  that knows about variants, or normalises to `pose_landmarker.task` as today. The current scheme
  cannot tell which variant is installed, which matters the moment accuracy is compared.
- Checksum the download. The URLs are versioned by `latest/`, so what lands can change silently.
- No new runtime dependency: `urllib.request` is enough for a handful of files, and adding
  `httpx`/`requests` to a library for this would be disproportionate.

## Why it is deferred

The manual step is two commands and it is now written down in `abyss`'s README and in
`~/data/pose/README.md` on the dev box. Automating it is convenience, not capability, and it comes
with real decisions (variant naming, checksums, whether a library may touch the network at all)
that deserve their own pass rather than being smuggled into an unrelated change.

Pick it up when a second machine needs setting up, or when a consumer wants to choose a variant at
runtime - that is the point where the current design actually blocks something.

## Picked up, 2026-08-14

The trigger arrived from the other side: `abyss` needs a face landmarker
([`../04_face_landmarker/`](../04_face_landmarker/)), the box has no `face_landmarker.task`, and its
Q1 asked whether to fetch it by hand again or build this. Building it, so the face work can call
`ensure_model` instead of documenting a third curl command.

### Decisions

The open decisions from the sketch, resolved. Each was measured against the live CDN rather than
assumed:

- **Precision is not a dimension.** The sketch assumed `float16` / `float32` were both available.
  Probed: `face_landmarker/.../float32/...` is a 404, while every `float16` URL is a 200. So the
  table stores one URL per `(model type, variant)` and no precision axis. Adding one later is a
  table change, not an API change.
- **Variants, measured:** pose has `lite` (5.8 MB), `full` (9.4 MB), `heavy` (30.7 MB); hand
  (7.8 MB) and face (3.8 MB) ship a single variant each. Default is `full` for pose, matching what
  is already installed on the dev box, and the sole variant elsewhere.
- **Filenames stay normalised.** `pose_landmarker.task`, not `pose_landmarker_full.task`. The
  alternative breaks `abyss`, which already calls `get_model_path("pose_landmarker")`, for a benefit
  nothing needs yet. **Named ceiling:** the installed variant is not recoverable from the filename,
  so comparing accuracy across variants means re-downloading deliberately or tracking it outside the
  library. A sidecar metadata file is the upgrade path when that day comes.
- **No checksums.** MediaPipe publishes no per-file manifest to check against, so a checksum could
  only pin what was downloaded once here, which protects nobody on a fresh machine. The download is
  written to a `.part` file and renamed only on success, so the failure mode is "no file" rather
  than "half a file". That is the property that actually matters.
- **Network only when asked.** `ensure_model()` downloads, `get_model_path()` never does. Unchanged
  from the sketch, and the reason the test suite can stay offline.
- **No new dependency.** `urllib.request` from the standard library.

Planned in [`tracking.md`](tracking.md).
