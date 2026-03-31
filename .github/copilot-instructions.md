# pose-tools - Copilot Instructions

## Project overview

`pose-tools` is an installable Python library for pose tracking and analysis. It provides common utilities for working with pose data, including MediaPipe integration (hand and pose landmarkers), video frame loading, OpenCV/matplotlib display helpers, numpy-based landmark arrays with visibility masking, homography utilities, and landmark distance computation. It extracts and unifies shared code from `climbing-wire`, `holo-table`, and `abyss`. Python 3.13, managed with **uv**.

The package name is `pose_tools` throughout the source.

## Running & tooling

```bash
uv run pytest                        # run tests
uv run ruff check .                  # lint (ruff, ALL rules enabled)
uv run pyright                       # type-check (src/ and tests/ only)

uv run mkdocs serve                  # MkDocs local docs server
```

Credentials live at `~/cred/pose-tools/.env` (loaded by `load_env()` in `src/pose_tools/params/load_env.py`).

## Architecture layers

| Layer       | Path                                               | Role                                                                |
| ----------- | -------------------------------------------------- | ------------------------------------------------------------------- |
| Params      | `src/pose_tools/params/pose_tools_params.py`       | Singleton `PoseToolsParams`; aggregates paths and sample params     |
| Paths       | `src/pose_tools/params/pose_tools_paths.py`        | `PoseToolsPaths`; env-aware filesystem references                   |
| Config      | `src/pose_tools/config/`                           | Pydantic `BaseModelKwargs` models for typed settings                |
| Data models | `src/pose_tools/data_models/basemodel_kwargs.py`   | `BaseModelKwargs` - Pydantic base with `to_kw()` kwargs flattening  |
| Metaclasses | `src/pose_tools/metaclasses/singleton.py`          | `Singleton` metaclass                                               |
| Env type    | `src/pose_tools/params/env_type.py`                | `EnvStageType` (dev/prod) and `EnvLocationType` (local/render)      |

## Key patterns

**`PoseToolsParams` singleton**  
Access project-wide config via `get_pose_tools_params()` from `src/pose_tools/params/pose_tools_params.py`. It aggregates `PoseToolsPaths` and `SampleParams`. Environment is controlled by `ENV_STAGE_TYPE` (`dev`/`prod`) and `ENV_LOCATION_TYPE` (`local`/`render`) env vars.

```python
from pose_tools.params.pose_tools_params import get_pose_tools_params

params = get_pose_tools_params()
paths = params.paths          # PoseToolsPaths
```

**`BaseModelKwargs`**  
Extend `BaseModelKwargs` (not plain `BaseModel`) for any config that needs to be forwarded as `**kwargs` to a third-party constructor. `to_kw(exclude_none=True)` flattens a nested `kwargs` dict at the top level.

```python
class SampleConfig(BaseModelKwargs):
    some_int: int
    nested_model: NestedModel
    kwargs: dict = Field(default_factory=dict)

cfg = SampleConfig(some_int=1, nested_model=NestedModel(some_str="hi"), kwargs={"extra": True})
cfg.to_kw(exclude_none=True)  # {"some_int": 1, "nested_model": ..., "extra": True}
```

**Config / Params separation**

- `src/pose_tools/config/` holds Pydantic `BaseModelKwargs` models that define the _shape_ of settings. Use `SecretStr` for every sensitive field. Never read env vars inside config models.
- `src/pose_tools/params/` holds plain classes that load _actual values_ and instantiate config models. Non-secret values are written as Python literals; env-switching is achieved via `match` on `env_type.stage` / `env_type.location`. Secrets are the only values loaded from `os.environ[VAR]` (raises `KeyError` naturally when missing).
- Every Params class accepts `env_type: EnvType | None = None` as its sole constructor argument. `__init__` only stores it and calls `_load_params()`. Loading is orchestrated via `_load_common_params()` then stage/location dispatch.
- Expose the assembled settings through `to_config()` returning the corresponding Pydantic model. Always mask secret fields in `__str__` using `[REDACTED]`.
- See `docs/guides/params_config.md` for the full reference with examples and common mistakes.

The canonical reference implementations are `src/pose_tools/config/sample_config.py` and `src/pose_tools/params/sample_params.py`.

**Env-aware paths**  
`PoseToolsPaths.load_config()` dispatches on `EnvLocationType` (`LOCAL` / `RENDER`) to set environment-specific paths. Common paths (`root_fol`, `cache_fol`, `data_fol`) are always set in `load_common_config_pre()`.

**`Singleton` metaclass**  
Use `metaclass=Singleton` for any class that must have exactly one instance per process (e.g., `PoseToolsParams`). Reset in tests by clearing `Singleton._instances`.

## Style rules

- Never use em dashes (`--` or `---` or Unicode `—`). Use a hyphen `-` or rewrite the sentence.
- Use `loguru` (`from loguru import logger as lg`) for all logging.
- Raise descriptive custom exceptions (e.g., `UnknownEnvLocationError`) rather than bare `ValueError`/`RuntimeError`.

## Documentation

Always keep the `docs/` folder updated at the end of a task.

### Docs folder

- `docs/` holds MkDocs source. `mkdocs.yml` configures the site with the Material theme, mkdocstrings for API reference.
- `docs/guides/` holds narrative guides related to tooling, setup, and project conventions. These are not part of the API reference and should not be written in docstring style.
- `docs/library/` holds description of the core library code. This is not an API reference; write in narrative style with custom headings as needed. Can create subfolders for different domains.
- `docs/reference/` is a virtual folder generated by `mkdocstrings` from docstrings in the source code. Do not write any files here; write docstrings in the source code instead. To reference a file inside this section, link using this structure: [`<some class/function name>`](,,/../reference/pose_tools/config/sample_config/) which would link to `src/pose_tools/config/sample_config.py`'s API reference page.

### Docstring style

Use **Google style** throughout. mkdocstrings is configured with `docstring_style: "google"`.

Standard sections use a label followed by a colon, with content indented by 4 spaces:

```python
def example(value: int) -> str:
    """One-line summary.

    Extended description as plain prose.

    Args:
        value: Description of the argument.

    Returns:
        Description of the return value.

    Raises:
        KeyError: If the key is missing.

    Example:
        Brief usage example::

            result = example(42)
    """
```

**Never use NumPy / Sphinx RST underline-style headers** (`Args\n----`, `Returns\n-------`, `Attributes\n----------`, etc.).

Rules:
- Section labels: `Args:`, `Returns:`, `Raises:`, `Attributes:`, `Note:`, `Warning:`, `See Also:`, `Example:`, `Examples:` - always with a trailing colon, never with an underline.
- `Attributes:` in class docstrings uses two levels of indentation: the attribute name at +4 spaces, its description at +8 spaces.
- Module docstrings are narrative prose. Custom topic headings (e.g., "Pattern rules") are written as plain labelled paragraphs (`Pattern rules:`) - no underline, no RST heading markup.
- `See Also:` lists items as bare lines indented under the section label, not as `*` bullets.

## Testing & scratch space

- Tests live in `tests/` mirroring `src/pose_tools/` structure.
- `scratch_space/` holds numbered exploratory notebooks and scripts. Not part of the package; ruff ignores `ERA001`/`F401`/`T20` there.

## Linting notes

- `ruff.toml` targets Python 3.13 with `select = ["ALL"]`. Key ignores: `COM812`, `D104`, `D203`, `D213`, `D413`, `FIX002`, `RET504`, `TD002`, `TD003`.
- Tests additionally allow `ARG001`, `INP001`, `PLR2004`, `S101`.
- Notebooks (`*.ipynb`) additionally allow `ERA001`, `F401`, `T20`.
- `meta/*` additionally allows `INP001`, `T20`.
- `max-args = 10` (pylint).

## End-of-task verification

After every code change, run the full verification suite before considering the task done:

```bash
uv run pytest && uv run ruff check . && uv run pyright
```

Then update the docs.
