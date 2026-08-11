# implementation tracking

Cleanup pass over pose-tools: drop the `load_env` import side effect, delete the one shim, and act
on an audit of the repo's general state. Audit and open questions in [`00_start.md`](00_start.md).

## Key decisions

- **No shims.** Consumers import from where a symbol actually lives. New code lands where it
  belongs and is imported from there; nothing gets routed into a namespace to justify the
  namespace's existence.
- **abyss is the only consumer.** `climbing-wire` and `holo-table` do not depend on pose-tools yet.
  The "would climbing-wire want it?" boundary test states intent, not current fact.
- **Scope held to side effect only** on the env question, per the answer given. The wider scaffold
  removal is Q1, decided separately.

## Phases

| #  | Phase                          | Plan | Status |
| -- | ------------------------------ | ---- | ------ |
| 1  | remove the shim                | -    | draft |
| 2  | remove the import side effect  | -    | draft, shaped by Q2 |
| 3  | docs vs reality                | -    | draft, shaped by Q4 |
| 4  | scaffold removal               | -    | draft, conditional on Q1 |
| 5  | landmarker tests               | -    | draft, conditional on Q3 |

Status values: draft / planned / in progress / done / superseded / discarded.

Sketch of each, to be replaced by real sub-plans once the questions land:

- **1 - remove the shim.** Delete `geometry/landmark_geometry.py` and
  `tests/geometry/test_landmark_geometry.py`. Fix the CHANGELOG v0.1.0 line and the
  `abyss/docs/library/pose_tools_boundary.md` row that names it. Nothing imports it, so this is
  a clean delete.
- **2 - remove the import side effect.** `__init__.py` back to a docstring. `load_env` stays
  callable for a caller that wants it. Settle `test_env_vars.py`, which currently passes only
  because this box happens to have `~/cred/pose-tools/.env`.
- **3 - docs vs reality.** The missing `guides/webapp_setup.md` in the mkdocs nav, the README claim
  about climbing-wire and holo-table, the `~/cred` setup section, and the bare `uv run` commands.
- **4 - scaffold removal.** Only if Q1 says yes: `env_type`, `sample_params`, `sample_config`,
  `basemodel_kwargs`, `nokeys.env`, flatten `pose_tools_paths`, drop `pydantic` and
  `python-dotenv`.
- **5 - landmarker tests.** `pose.py` and `hand.py` against a faked MediaPipe task, following the
  `FakeTask` / `FakeLandmarker` pattern already in `tests/landmark/test_base.py`.

## Log

Append-only. Newest at the bottom.

- 2026-08-11 : branched `chore/cleanup` off `main` at `d4e5c82` (v0.2.1) and ran the audit.
  Baseline green: ruff clean, pyright 0/0/0, 90 tests passing. Found exactly one shim
  (`geometry/landmark_geometry.py`, zero definitions, the only module with `__all__`). Found that
  `tests/config/test_env_vars.py` passes only because `~/cred/pose-tools/.env` exists on this box -
  `conftest.py` does not set `POSE_TOOLS_SAMPLE_ENV_VAR`, so the suite is not reproducible on a
  fresh clone. Confirmed abyss is the sole consumer, importing 7 symbols; `climbing-wire` and
  `holo-table` carry no pose-tools dependency. Coverage is inverted: 90 tests, none over
  `landmark/{pose,hand,drawing}.py` or `utils/plt.py`. Docs drift: mkdocs nav points at a
  nonexistent `guides/webapp_setup.md`, README credits two consumers that do not exist and
  prescribes bare `uv run`, and there is no Makefile.
