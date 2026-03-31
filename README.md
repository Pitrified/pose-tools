# Pose Tools

An installable Python library for pose tracking and analysis. Provides common utilities for working with pose data, including MediaPipe integration (hand and pose landmarkers), video frame loading, OpenCV/matplotlib display helpers, numpy-based landmark arrays with visibility masking, homography utilities, and landmark distance computation. Extracts and unifies shared code from `climbing-wire`, `holo-table`, and `abyss`.

## Installation

### Setup `uv`

Install [`uv`](https://docs.astral.sh/uv/getting-started/installation/).

### Install the package

```bash
uv sync --all-extras --all-groups
```

## Docs

Docs are available at [https://pitrified.github.io/pose-tools/](https://pitrified.github.io/pose-tools/).

## Setup

### Environment Variables

Create a `.env` file in `~/cred/pose-tools/.env`. See `nokeys.env` for the required keys.

### Pre-commit

```bash
pre-commit install
```

### Linting

```bash
uv run pyright
uv run ruff check .
```

### Testing

```bash
uv run pytest
```
