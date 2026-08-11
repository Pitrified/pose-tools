# Params

`pose_tools.params` holds the filesystem references the library needs, and nothing else.

```python
from pose_tools.params.pose_tools_params import get_pose_tools_paths

paths = get_pose_tools_paths()
print(paths.data_fol)
```

Two classes:

- `PoseToolsPaths` - resolves `src_fol`, `root_fol`, `cache_fol` and `data_fol` from the package
  location. No arguments.
- `PoseToolsParams` - a `Singleton` that aggregates the paths. Reach it through
  `get_pose_tools_params()`, or `get_pose_tools_paths()` for the paths alone. Never construct
  `PoseToolsPaths()` directly.

## What is deliberately absent

Earlier versions carried the full `python-project-template` config layer: `EnvType` with stage
(dev/prod) and location (local/render) dispatch, Pydantic config models, a `SampleParams` /
`SampleConfig` reference pair, and a `load_env()` call fired from `pose_tools/__init__.py` that read
`~/cred/pose-tools/.env` on import.

All of it was removed in v0.3.0. pose-tools is a library with no secrets, no deployment target and
no environment to switch on, so the machinery only added an import side effect and a test that
passed or failed depending on whose machine it ran on.

Add it back when something needs it, not before. The same applies to new entries in
`PoseToolsPaths`: a path goes in when code reads it.
