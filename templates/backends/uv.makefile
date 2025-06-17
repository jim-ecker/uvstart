PYTHON_VERSION ?= {{PYTHON_VERSION}}
PROJECT_NAME := {{PROJECT_NAME}}

.PHONY: venv add run lock sync clean jupyter-install notebook kernel

venv:
	uv venv --python=$(PYTHON_VERSION)

add:
	@read -p "Enter packages to add: " pkgs; \
	uv add $$pkgs

run:
	uv run python main.py

lock:
	uv lock

sync:
	uv sync

clean:
	rm -rf .venv __pypackages__ uv.lock

jupyter-install:
	uv add notebook ipykernel

notebook:
	uv run jupyter notebook

kernel:
	uv run python -m ipykernel install --user --name="$(PROJECT_NAME)" --display-name="$(PROJECT_NAME)"

include apply_template.mk
