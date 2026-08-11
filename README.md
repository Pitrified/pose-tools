# Pose Tools

An installable Python library for pose tracking and analysis. Provides common utilities for working with pose data, including MediaPipe integration (hand and pose landmarkers), video frame loading, OpenCV/matplotlib display helpers, numpy-based landmark arrays with visibility masking, homography utilities, and landmark distance computation.

It exists to hold code shared across the pose projects. `abyss` consumes it today, pinned by git tag; `climbing-wire` and `holo-table` still carry their own copies and are the intended next consumers.

## Installation

### Setup `uv`

Install [`uv`](https://docs.astral.sh/uv/getting-started/installation/).

### Install the package

```bash
make sync
```

## Docs

Docs are available at [https://pitrified.github.io/pose-tools/](https://pitrified.github.io/pose-tools/).

## Setup

### Pre-commit

```bash
pre-commit install
```

### Checks

```bash
make check        # lint, typecheck and test
make lint         # ruff
make typecheck    # pyright
make test         # pytest
```

`make help` lists every target. Targets run project code through `uv run --no-sync`; a bare `uv run`
re-syncs the environment first, which undoes any local editable install. See
[`docs/guides/makefile.md`](docs/guides/makefile.md).
