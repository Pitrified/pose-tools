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
