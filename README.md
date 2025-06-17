# uvstart

`uvstart` is a fast, no-boilerplate Python project initializer that works seamlessly with modern tools like [`uv`](https://github.com/astral-sh/uv) or [`poetry`](https://python-poetry.org/). It helps you create new Python projects with isolated environments, templated features, and automation-ready Makefiles — all without relying on global Python environments or Anaconda.

---

## Features

- Shell-based CLI with no runtime dependencies
- Supports `uv` (`__pypackages__`) and `poetry` (`.venv`)
- Initializes directly in the current directory (no nested folders)
- Auto-generates `Makefile`, `pyproject.toml`, `.gitignore`, and starter files
- Optional templates for Jupyter, CLI, PyTorch, research, and more
- Git-ready and Jupyter-compatible by default
- Fully offline operation after installation

---
## Installation

Clone the repo and install `uvstart` locally:

```bash
git clone https://github.com/jim-ecker/uvstart.git
cd uvstart
./installer.sh
```

This will install `uvstart` into `~/.local/uvstart` and symlink the script to `~/.local/bin/uvstart`.

Make sure `~/.local/bin` is in your `$PATH`:

```bash
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc   # or ~/.zshrc
source ~/.bashrc                                           # or source ~/.zshrc
```

You can now run:

```bash
uvstart help
```
---

## Getting Started

### Step 1: Create a project folder

```bash
mkdir MyProject
cd MyProject
```

### Step 2: Initialize the project

```bash
uvstart init 3.12 --backend uv --template notebook
```

This will create the following structure directly in the current directory:

```
MyProject/
├── Makefile
├── main.py
├── pyproject.toml
├── .gitignore
├── .gitattributes
├── apply_template.mk
├── notebooks/
└── README.md
```

By default, `uvstart` also initializes a Git repository using the `main` branch.

To skip Git initialization, add the `--no-git` flag:

```bash
uvstart init 3.12 --no-git
```

---

## CLI Usage

### Initialization

```bash
uvstart init <python-version> [--backend uv|poetry] [--template <template-name>] [--no-git]
```

Examples:

```bash
uvstart init 3.11
uvstart init 3.12 --backend poetry --template cli
uvstart init 3.12 --no-git
```

### Template Management

```bash
uvstart template list
uvstart template apply notebook
```

Or using `make`:

```bash
make template TEMPLATE=notebook
```

---

## Makefile Targets

| Command                     | Description                          |
|----------------------------|--------------------------------------|
| `make sync`                | Install dependencies                 |
| `make run`                 | Run the main Python entry point      |
| `make notebook`            | Launch Jupyter Notebook              |
| `make template TEMPLATE=…` | Add a feature template to project    |

---

## Backends

| Backend  | Description                          | Output Directory     |
|----------|--------------------------------------|----------------------|
| `uv`     | Fast, no-venv, uses `__pypackages__` | `__pypackages__/`    |
| `poetry` | Full-featured virtualenv manager     | `.venv/`             |

---

## Templates

Templates live in `templates/features/` and can be applied to any project. Available templates include:

- `notebook` – Jupyter setup
- `cli` – Command-line `argparse` starter
- `pytorch` – Training loop and data loader scaffold
- `research` – LaTeX paper and BibTeX setup
- `web` – (coming soon)

---

## Developer Setup

```bash
git clone https://github.com/jim-ecker/uvstart.git
cd uvstart
./uvstart init 3.12 --backend uv
```

To install globally:

```bash
./installer.sh
```

Then use `uvstart` in any folder to scaffold a new project.

---

## Contributing

PRs and issues welcome!

1. Fork the repo
2. Make changes on a feature branch
3. Submit a pull request

[https://github.com/jim-ecker/uvstart](https://github.com/jim-ecker/uvstart)

---

## License

MIT License © 2025 [Jim Ecker](https://github.com/jim-ecker)
