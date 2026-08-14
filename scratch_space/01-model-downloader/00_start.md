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
