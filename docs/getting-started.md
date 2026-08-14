# Getting Started

This guide will help you set up your development environment and get started with `pose-tools`.

## Prerequisites

- Python 3.14 (pinned by `.python-version` and `requires-python`)
- [uv](https://docs.astral.sh/uv/) package manager

## Installation

### 1. Clone the Repository

```bash
git clone git@github.com:Pitrified/pose-tools.git
cd pose-tools
```

### 2. Install Dependencies

```bash
make sync
```

### 3. Verify Installation

```bash
make check
```

## Development Workflow

### Running Tests

```bash
make test
uv run --no-sync pytest -v                # Verbose output
uv run --no-sync pytest tests/landmark/   # Run specific test directory
```

`make help` lists every target. Run project code through `make` or `uv run --no-sync`; a bare
`uv run` re-syncs the environment first. See [Makefile](guides/makefile.md).

### Code Quality

```bash
make lint
make format
make typecheck
```

### Pre-commit Hooks

Pre-commit hooks are configured to run automatically on each commit:

```bash
# Install hooks (first time only)
uv run --no-sync pre-commit install

# Run manually on all files
uv run --no-sync pre-commit run --all-files
```

## Model files

MediaPipe needs a `.task` file per landmarker. They are not in the repository and not in the
wheel; they live in `~/.mediapipe/models/` and are fetched on request:

```python
from pose_tools.landmark.model_manager import ModelManager

path = ModelManager().ensure_model("face_landmarker")
```

`ensure_model()` returns immediately if the file is already there, and is the only method that
touches the network. `get_model_path()` resolves and validates a path and never downloads, so
importing or testing against pose-tools stays offline.

Available models, with the sizes the CDN currently serves:

| Model type         | Variants                | Size                       |
| ------------------ | ----------------------- | -------------------------- |
| `pose_landmarker`  | `lite`, `full`, `heavy` | 5.8 MB / 9.4 MB / 30.7 MB  |
| `hand_landmarker`  | single                  | 7.8 MB                     |
| `face_landmarker`  | single                  | 3.8 MB                     |

`full` is the default for pose. Pass a variant explicitly to get another:

```python
ModelManager().ensure_model("pose_landmarker", "heavy")
```

Files are stored under the model type's canonical name, so `pose_landmarker.task` regardless of
which variant produced it. That means the installed variant cannot be read back from disk - if you
need to be certain which one you have, download it again with `force=True`.

## Configuration

There is none to set up. pose-tools reads no environment variables and holds no secrets; see
[Params](guides/params.md) for what the `params` layer does and what was deliberately left out.

## Building Documentation

```bash
# Start local server with hot reload
make docs

# Build static site, failing on any warning
make docs-build
```
