# Makefile

The `Makefile` is the task runner: one place to find every command, discoverable with `make help`.

This copy is trimmed from the one in `python-project-template`: pose-tools has no internal git
dependencies of its own, so the `dev-<lib>` and `undev` targets are not here. The `docs` targets
are, because pose-tools does publish a site.

```bash
make help        # list every target with its description
make sync        # install all dependencies (extras and groups)
make check       # lint, typecheck and test
make docs        # serve the docs locally
make nbstrip     # strip notebook outputs
```

## Adding a target

The `##` comment after the target name is the help text - there is no separate list to maintain:

```makefile
my-target:  ## What this does, in one line
	$(UV_RUN) python -m pose_tools.thing
```

Run project code through `$(UV_RUN)`, not a bare `uv run`. The reason is below.

## Why `UV_RUN := uv run --no-sync`

`uv run` syncs the environment against `uv.lock` before it runs anything. That is usually what you
want, and it is exactly wrong when something else has been deliberately installed into the venv.

pose-tools is consumed by `abyss`, pinned there by git tag. When you work on both at once, abyss's
`make dev-pose-tools` runs `uv pip install -e ../pose-tools`. That install exists only in abyss's
`.venv` - it is not in its `uv.lock` - so the next plain `uv run` over there reinstalls the pinned
tag over it, with no warning:

| step                              | what resolves      |
| --------------------------------- | ------------------ |
| `uv sync`                         | the pinned tag     |
| `uv pip install -e ../pose-tools` | the local checkout |
| one plain `uv run` anything       | the pinned tag     |

Passing `--no-sync` keeps the editable install in place, which is why every target that runs
project code goes through `$(UV_RUN)` - in this repo too, so that working here does not undo the
override set up next door.

`UV_FROZEN=1` / `--frozen` does **not** help: it only stops `uv.lock` from being updated, and the
environment is still synced.

## What this does not protect

Only `make` targets pass `--no-sync`. These still revert an editable install:

- a bare `uv run ...` in a terminal,
- the editor's test runner or language server, if it invokes `uv run`,
- `pre-commit`, and any `uv sync`.
