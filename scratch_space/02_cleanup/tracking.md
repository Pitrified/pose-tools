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

All questions answered, so the phases were executed in one pass rather than written up as separate
sub-plans - each is a delete or a rewrite with nothing to sequence around.

| #  | Phase                          | Plan | Status |
| -- | ------------------------------ | ---- | ------ |
| 1  | remove the shim                | -    | done |
| 2  | remove the import side effect  | -    | done |
| 3  | scaffold removal               | -    | done |
| 4  | Makefile                       | -    | done |
| 5  | docs vs reality                | -    | done |
| 6  | release v0.3.0                 | -    | in progress |
| -  | landmarker tests               | [`../03_landmarker_tests/00_start.md`](../03_landmarker_tests/00_start.md) | spun off, per Q3 |

Status values: draft / planned / in progress / done / superseded / discarded.

What each covered:

- **1 - remove the shim.** Deleted `geometry/landmark_geometry.py` and its test. The CHANGELOG
  v0.1.0 line that announced it was **not** edited: that section records what actually shipped, so
  the removal is recorded under v0.3.0 instead.
- **2 - remove the import side effect.** `__init__.py` is a docstring. `load_env.py` went too
  (Q1), and `python-dotenv` with it - it had no other user. `test_env_vars.py` deleted (Q2).
- **3 - scaffold removal.** `env_type`, `sample_params`, `config/`, `data_models/`, `nokeys.env`,
  their tests, and `tests/conftest.py` (which existed only to stub `SAMPLE_API_KEY`). Dropped
  `pydantic`. `PoseToolsPaths` takes no arguments; `PoseToolsParams.set_env_type()` is gone.
- **4 - Makefile.** Ported from the template minus `dev-<lib>` / `undev`, keeping `docs` and
  `docs-build`.
- **5 - docs vs reality.** README, `docs/index.md`, `docs/getting-started.md`, `AGENTS.md`,
  `.github/copilot-instructions.md`, mkdocs nav. Replaced the 284-line `guides/params_config.md`
  with `guides/params.md`; added `guides/makefile.md`; added a `CLAUDE.md` importing the copilot
  instructions, which the repo lacked.
- **6 - release v0.3.0.** Version bumped and CHANGELOG written. The tag and the abyss repin are
  the remaining steps.

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
- 2026-08-11 : Q1-Q5 answered, and executed phases 1-5 in one pass. Removed the shim, the
  `load_env` side effect and module, and the whole template scaffold; dropped `pydantic` and
  `python-dotenv`; flattened `PoseToolsPaths`; added the Makefile and `CLAUDE.md`; rewrote the
  docs. Suite went 90 -> 71 tests, all passing, with ruff and pyright clean and
  `mkdocs build --strict` succeeding. Landmarker tests spun off to `../03_landmarker_tests/`.
- 2026-08-11 : tried raising `ruff.toml` `target-version` from `py313` to `py314`, to match
  `requires-python = "==3.14.*"`. It surfaces 28 `TC001`/`TC002`/`TC003` findings
  (typing-only imports) needing unsafe fixes across the codebase. Reverted - that is a lint
  migration, not a cleanup. Recorded in `.github/copilot-instructions.md` so the mismatch is not
  rediscovered as a surprise.
