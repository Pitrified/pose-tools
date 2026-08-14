---
status: done
---

# Phase 1 - registry and ensure_model

## Overview

The whole feature: a URL table, a download method, and the tests that keep both honest. Context:
[`00_start.md`](00_start.md).

Code and tests are one phase because the tests are the only way to exercise the code on a machine
where the models already exist.

## Goals

1. `ModelManager.ensure_model(model_type, variant=None)` returns a path to a present model file,
   downloading it if needed.
2. Every model type and variant the CDN serves is reachable by name.
3. The test suite still runs offline and touches no network.

## Plan

- `model_manager.py` gains, beside `MODEL_FILENAMES`:
  - `face_landmarker` in `ModelType` and `MODEL_FILENAMES`
  - `MODEL_URLS: dict[ModelType, dict[str, str]]`, variant name to full URL, all seven verified
  - `DEFAULT_VARIANTS: dict[ModelType, str]`, `full` for pose and the sole variant elsewhere
- `ensure_model(model_type, variant=None, *, force=False, timeout=...)`:
  - resolve the variant, raising `UnknownModelVariantError` naming the valid ones
  - return early if the file is present and `force` is false
  - create the model directory, download to `<name>.part`, rename on success
  - remove the partial file and raise `ModelDownloadError` on any network or write failure
- Errors are named and descriptive, matching `ModelNotFoundError`'s style in the same module.
- Tests in `tests/landmark/test_model_manager.py`, extending the existing class-per-concern layout:
  - the registry covers every `ModelType`, and every URL is https and ends in `.task`
  - `ensure_model` returns an existing file without opening the network - asserted by patching the
    opener with something that fails the test if called
  - a fake opener returning bytes produces the file, with the right content and name
  - `force=True` re-downloads over an existing file
  - an unknown variant raises before any network call
  - a failing opener leaves **no** file behind, not a partial one - the point of the `.part` dance
- A real download is verified once by hand against the live CDN, and that check is not in the suite.

## Out of scope

- Checksums, a variant-aware filename scheme, progress reporting, retries. Each is a real idea and
  none has a caller today; the ceilings are named in `00_start.md`.
- `landmark/face.py`. Registering the model type is not the same as wrapping the task, and the
  wrapper belongs to [`../04_face_landmarker/`](../04_face_landmarker/).

## Done when

- `make check` is green, and `make test` passes with no network access.
- `ensure_model("face_landmarker")` fetches the real file on this box, checked manually.
- `get_model_path()` still never touches the network.
