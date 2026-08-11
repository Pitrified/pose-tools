.PHONY: help sync lint format typecheck test check docs docs-build nbstrip

MAKEFLAGS += --no-print-directory
.DEFAULT_GOAL := help

# Every target that runs project code goes through UV_RUN. The --no-sync matters:
# a plain `uv run` re-syncs the environment from uv.lock first, which silently
# undoes any `uv pip install -e`. pose-tools has no internal git dependencies of
# its own, so there are no dev-<lib> targets here - but a consumer that installs
# pose-tools editable (abyss `make dev-pose-tools`) is undone by a bare `uv run`
# in this repo just the same.
UV_RUN := uv run --no-sync

help:  ## Show this help (list targets and their descriptions)
	@grep -hE '^[a-zA-Z0-9_-]+:.*?## .*$$' $(MAKEFILE_LIST) \
		| sort \
		| awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-16s\033[0m %s\n", $$1, $$2}'

#########
# SETUP #
#########

sync:  ## Install all dependencies (extras and groups) - the only target that syncs
	uv sync --all-extras --all-groups

########
# LINT #
########

lint:  ## Lint with ruff
	$(UV_RUN) ruff check .

format:  ## Format with ruff
	$(UV_RUN) ruff format .

typecheck:  ## Type-check with pyright
	$(UV_RUN) pyright

test:  ## Run the test suite
	$(UV_RUN) pytest

check: lint typecheck test  ## Run lint, typecheck and test

nbstrip:  ## Strip notebook outputs (pre-commit only verifies, this fixes)
	@files=$$(git ls-files '*.ipynb'); \
	if [ -n "$$files" ]; then $(UV_RUN) nbstripout $$files; else echo "no tracked notebooks"; fi

########
# DOCS #
########

docs:  ## Serve the docs locally with MkDocs
	$(UV_RUN) mkdocs serve

docs-build:  ## Build the docs, failing on any warning
	$(UV_RUN) mkdocs build --strict
