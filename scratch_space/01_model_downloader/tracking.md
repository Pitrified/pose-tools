# implementation tracking

Teaching `ModelManager` to fetch the MediaPipe `.task` files it currently only names. Analysis,
trigger and resolved decisions in [`00_start.md`](00_start.md).

## Key decisions

- **Explicit downloads only.** `ensure_model()` reaches the network, `get_model_path()` never does.
  A library that downloads on a path lookup is a surprise in someone else's test suite.
- **Normalised filenames, with a named ceiling.** Files land as `<model_type>.task` regardless of
  variant, because `abyss` already resolves that name. The cost is that the installed variant cannot
  be read back; a sidecar file is the upgrade path if variant comparison ever matters.
- **No checksums, atomic writes instead.** There is no published manifest to verify against. Writing
  to `.part` and renaming on success gives the property that matters: a failed download leaves no
  file, rather than a truncated one.
- **`face_landmarker` is registered here**, ahead of the wrapper that uses it. It is two dictionary
  entries, and registering it here is what lets the face initiative fetch its model on day one.

## Phases

| #  | Phase                     | Plan                                       | Status  |
| -- | ------------------------- | ------------------------------------------ | ------- |
| 1  | registry and ensure_model | [`01_ensure_model.md`](01_ensure_model.md) | done    |
| 2  | docs and changelog        | [`02_docs.md`](02_docs.md)                 | done    |

Status values: draft / planned / in progress / done / superseded / discarded.

## Log

Append-only. Newest at the bottom.

- 2026-08-14 : picked up four days after being deferred, on its own stated trigger: the face
  landmarker initiative needs a model this box does not have. Renamed the folder from
  `01-model-downloader` to snake_case. Probed the CDN before planning and corrected the sketch on
  two points: `float32` does not exist for the face model, so precision is not a dimension worth
  encoding, and only pose ships multiple variants. Recorded the resolved decisions in `00_start.md`.
- 2026-08-14 : phase 1 done. `ensure_model()` on `ModelManager`, plus `MODEL_URLS`,
  `DEFAULT_VARIANTS`, `UnknownModelVariantError` and `ModelDownloadError`, and `face_landmarker`
  registered as a model type. 11 new tests, all offline: the "already present" and "unknown variant"
  cases patch in an opener that fails the test if it is called, which is what actually pins the
  no-implicit-network promise. Verified for real against the CDN: the face model downloaded to
  3758596 bytes, matching the CDN's reported length exactly, and MediaPipe built a `FaceLandmarker`
  from it with `output_facial_transformation_matrixes=True`. The face initiative now has its model.
  Two ruff findings worth recording. The URL table tripped `E501`; rather than wrapping strings I
  added a `_model_url(family, asset)` helper, which also removed the repetition of the asset name.
  `urlopen` on a non-literal URL trips `S310` (audit URL open for permitted schemes), which a
  scheme check does not satisfy - the rule wants a literal. The repo rule is to fix rather than
  `noqa`, so this is the deliberate exception: one targeted `# noqa: S310` naming why the URL is
  trusted. The alternative was an `httpx` / `requests` dependency, rejected in the original sketch.
- 2026-08-14 : phase 2 done. A "Model files" section in `docs/getting-started.md` with the variant
  table and measured sizes, and an `Unreleased` changelog entry recording both the normalised
  filename ceiling and the absence of checksums. `README.md` and `docs/index.md` turned out to
  mention models nowhere at all, so the planned README edit had nothing to attach to and was
  dropped. `make docs-build` passes under `--strict`, `make check` green, 82 tests.
