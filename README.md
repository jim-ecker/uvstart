# uvstart

`uvstart` is a fast, zero-dependency Python project initializer for modern development workflows. It enables Python developers to create new projects with fully isolated environments, Makefile automation, and reusable code templates — all without relying on global Python installations or virtualenvs.

This project leverages the speed and simplicity of [`uv`](https://github.com/astral-sh/uv), while optionally supporting [`poetry`](https://python-poetry.org/). It integrates flexible project scaffolding and configuration via a lightweight CLI and Makefile backend.

---

## Features

- Lightweight CLI written in portable shell script
- Use `uv` with `__pypackages__` or `poetry` with `.venv`
- Language-version pinning per project (e.g., Python 3.12)
- Pluggable feature templates (notebook, CLI, PyTorch, etc.)
- Makefile-based automation (`make sync`, `make run`, `make notebook`, etc.)
- Git- and Jupyter-ready out of the box
- Requires no global Python environment or prior virtualenv setup

---

## Installation

Run the installer script to install `uvstart` into your local `~/.local/bin`:

```bash
curl -fsSL https://raw.githubusercontent.com/jim-ecker/uvstart/main/installer.sh | bash
```

Make sure `~/.local/bin` is in your shell’s `$PATH`.

---

## Getting Started

### Create a New Project

```bash
mkdir MyNewProject
cd MyNewProject
uvstart init 3.12 --backend uv --template notebook
```

This creates a fully structured project directory with:

```
MyNewProject/
├── Makefile
├── main.py
├── pyproject.toml
├── .gitignore
├── .gitattributes
├── notebooks/
├── README.md
└── __pypackages__/ (or .venv/)
```

You can also skip the `--template` argument during init and add feature templates later.

---

## CLI Commands

### Project Initialization

```bash
uvstart init <python-version> [--backend uv|poetry] [--template <template-name>]
```

Examples:

```bash
uvstart init 3.11
uvstart init 3.12 --backend poetry --template cli
```

### Template Management

List available templates:

```bash
uvstart template list
```

Apply a feature template:

```bash
uvstart template apply notebook
```

Or using Makefile interface:

```bash
make template TEMPLATE=notebook
```

---

## Makefile Targets

All `uvstart` projects include a Makefile that supports the following:

| Command                     | Description                          |
|----------------------------|--------------------------------------|
| `make sync`                | Install dependencies                 |
| `make run`                 | Run the default entry point          |
| `make notebook`            | Launch a Jupyter notebook            |
| `make template TEMPLATE=…` | Add a new feature template to project |

You may extend or override these rules in your local Makefile.

---

## Backends

`uvstart` supports two environment managers:

| Backend | Description                            | Output            |
|---------|----------------------------------------|-------------------|
| `uv`    | Fast, minimal, uses `__pypackages__`   | `__pypackages__/` |
| `poetry`| Full-featured, uses virtualenv         | `.venv/`          |

By default, `uv` is used.

---

## Templates

Templates are pluggable feature scaffolds under `templates/features/`.

Available templates include:

- `notebook` — Jupyter support with default notebook folder
- `cli` — Command-line parser using `argparse`
- `pytorch` — Training loop, data loading scaffolding
- `research` — Academic setup with BibTeX and LaTeX files
- `web` — Coming soon (FastAPI or Flask)

You can create your own templates and place them under `templates/features/`.

---

## Developer Setup

Clone the repository:

```bash
git clone git@github.com:jim-ecker/uvstart.git
cd uvstart
```

Run a local test:

```bash
./uvstart init 3.12 --backend uv --template cli
```

To add or modify templates:

- `templates/backends/*.makefile` – backend-specific logic
- `templates/features/<name>/` – feature scaffolds
- `scripts/*.sh` – CLI logic (`init`, `template`)

---

## Contributing

We welcome contributions! To contribute:

1. Fork the repo and create a new branch.
2. Add or improve a feature, backend, or template.
3. Submit a pull request with a clear description.

Issues and feature requests can be filed at:
[https://github.com/jim-ecker/uvstart/issues](https://github.com/jim-ecker/uvstart/issues)

---

## License

This project is licensed under the MIT License.  
Copyright © 2025 [Jim Ecker](https://github.com/jim-ecker)
