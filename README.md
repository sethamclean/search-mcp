# search_mcp

My personal MCP server for searching with SearXNG and converting urls to markdown
with MarkItDown. This server is minimal and these packages do the heavy lifting.

## Recommended Development Workflow

This project uses [uv](https://github.com/astral-sh/uv) for fast, reproducible dependency management and [Hatch](https://hatch.pypa.io/) for project automation (scripts, builds, tests). All dependencies and scripts are defined in `pyproject.toml`.

### Prerequisites

- Python 3.12 or newer
- [uv](https://docs.astral.sh/uv/getting-started/installation/)
- [Hatch](https://hatch.pypa.io/latest/install/) (for scripting/automation only)

Install uv:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Install hatch (if not already installed):

```bash
uv pip install --user hatch
```

### Setup & Development

1. **Create a virtual environment and install all dependencies (including dev):**

   ```bash
   uv venv
   uv pip install .[dev]
   ```

   - This will install all main and dev dependencies as defined in `[project.optional-dependencies]` in `pyproject.toml`.

2. **Activate the environment:**

   - On Linux/macOS:
     ```bash
     source .venv/bin/activate
     ```
   - On Windows:
     ```cmd
     .venv\Scripts\activate
     ```

3. **Run quality checks and tests using Hatch scripts:**
   - Lint: `hatch run lint`
   - Type check: `hatch run typecheck`
   - Security audit: `hatch run audit`
   - Format code: `hatch run format`
   - Build: `hatch run build`
   - Run tests: `hatch run test`
   - Run all quality checks:
     ```bash
     hatch run quality
     ```

### Notes

- Use uv for all dependency management and locking. This ensures reproducible installs via `uv.lock`.
- Use Hatch only for scripting and automation. It does not manage dependencies or create a lock file.
- If you update dependencies in `pyproject.toml`, re-run `uv pip install .[dev]` to update your environment and lock file.

## Project Setup

This project uses [uv](https://github.com/astral-sh/uv) for fast Python environment and dependency management, and [hatch](https://hatch.pypa.io/) for project scripts and automation.

### 1. Install uv

If you don’t have uv installed, run:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Or see [uv installation docs](https://docs.astral.sh/uv/getting-started/installation/) for other methods.

### 2. Bootstrap the Project

Create and activate a virtual environment, and install all dependencies in one step:

```bash
uv venv
uv pip install -e .
# For editable installs (-e .), ensure the `editables` package is installed.
# If you encounter a `ModuleNotFoundError: No module named 'editables'`, run:
uv pip install editables
```

- `uv venv` creates a `.venv` virtual environment in your project directory (using Python 3.12 by default, or the version in your `pyproject.toml`).
- `uv pip install -e .` installs your project and all dependencies in editable mode.

To activate the environment:

- On Linux/macOS:
  ```bash
  source .venv/bin/activate
  ```
- On Windows:
  ```cmd
  .venv\Scripts\activate
  ```

### 3. Development Workflow

This project uses [hatch](https://hatch.pypa.io/) for common development tasks. All scripts are defined in `pyproject.toml`.

**Install hatch (if not already installed):**

```bash
uv pip install hatch
```

**Common commands:**

- **Run all quality checks (lint, typecheck, audit, format, build, test):**

  ```bash
  hatch run quality
  ```

- **Lint:**

  ```bash
  hatch run lint
  ```

- **Type check:**

  ```bash
  hatch run typecheck
  ```

- **Security audit:**

  ```bash
  hatch run audit
  ```

- **Format code:**

  ```bash
  hatch run format
  ```

- **Build package:**

  ```bash
  hatch run build
  ```

- **Run tests:**
  ```bash
  hatch run test
  ```

---

## Pre-commit Hooks

This project uses [pre-commit](https://pre-commit.com/) to automate quality checks and builds before each commit.

### Setup

1. Install pre-commit (already included in dev dependencies):
   ```bash
   uv pip install .[dev]
   ```
2. Install the git hooks:
   ```bash
   pre-commit install
   ```

### What the hooks do

- On every commit, pre-commit will automatically run:
  - `hatch quality` (runs all quality checks: lint, typecheck, audit, format, build, test)
  - `hatch build` (builds the package)

You can also run all hooks manually on all files:

```bash
pre-commit run --all-files
```

---

## Summary

- Use `uv venv` and `uv pip install -e .` to bootstrap your environment.
- Use `hatch run quality` for a full quality assurance workflow.
- All other development scripts are available via `hatch run <script>`.
