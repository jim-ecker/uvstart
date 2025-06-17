# uvstart

**uvstart** is a modern, zero-dependency scaffolding tool for Python projects using [`uv`](https://astral.sh/uv) by default, with support for multiple backends and optional project templates.

##  Features

-  Supports `uv`, `poetry` (more coming)
-  Add features like `notebook`, `cli`, `web`, `pytorch`, `research`
-  Generates isolated, reproducible projects
-  Uses a Makefile for easy workflows
-  Apply templates later with `make template TEMPLATE=name`

##  Quickstart

```bash
curl -fsSL https://raw.githubusercontent.com/jim-ecker/uvstart/main/installer.sh | bash

mkdir MyProject && cd MyProject
uvstart 3.12 --backend uv --template notebook
```

##  Usage

```bash
make list-templates         # see available feature templates
make template TEMPLATE=cli  # apply CLI scaffold
make run                    # run your project
```

##  Supported Templates

- `notebook`
- `cli`
- `web`
- `pytorch`
- `research`

##  Supported Backends

- `uv` (default)
- `poetry`

##  Contributing

Feel free to submit pull requests for new backends or templates!

##  License

MIT
