## Developer Support

This fork is set up for local Home Assistant integration development from a macOS checkout, without a devcontainer.

### Prerequisites

- Git
- Visual Studio Code
- Homebrew Python 3.11: `brew install python@3.11`
- A Home Assistant test instance where this custom component can be installed or symlinked

The checked-in VS Code settings expect a virtual environment at `.venv`.

### Local Setup

From VS Code, run these tasks in order:

1. `Create virtual environment`
2. `Install test dependencies`
3. Optional: `Install developer tools`
4. `Run tests` or `Run importer tests without coverage`

Equivalent terminal commands:

```bash
python3.11 -m venv .venv
.venv/bin/python -m pip install --upgrade pip
.venv/bin/python -m pip install -r tests/requirements.txt
.venv/bin/python -m pip install -r .vscode/requirements.dev.txt
.venv/bin/python -m pytest
```

If macOS blocks Python bytecode writes under `~/Library/Caches`, keep `PYTHONPYCACHEPREFIX=/tmp/wnsm_pycache`; the workspace already sets this for integrated terminals and compile tasks.

### Useful Tasks

| Task | Description |
| --- | --- |
| Create virtual environment | Creates `.venv` with Python 3.11. |
| Install test dependencies | Installs the pinned test and Home Assistant dependencies. |
| Install developer tools | Installs local formatter, linter, and pre-commit tooling. |
| Run tests | Runs the repository pytest suite with the project pytest config. |
| Run importer tests without coverage | Fast smoke test for importer helper behavior. |
| Lint integration | Runs flake8 against `custom_components/wnsm`. |
| Compile integration modules | Checks syntax for the main integration modules without writing cache into the repo. |

### Home Assistant Debugging

For step-by-step debugging inside Home Assistant, enable the `debugpy` integration in your Home Assistant test config and expose port `5678`. Then use the VS Code launch configuration `Attach Home Assistant custom component`.

The path mapping assumes the integration is installed at:

```text
/config/custom_components/wnsm
```

If your Home Assistant config path differs, update the `remoteRoot` in `.vscode/launch.json`.
