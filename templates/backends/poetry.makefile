PYTHON_VERSION ?= {{PYTHON_VERSION}}

.PHONY: init install run add clean notebook kernel

init:
	poetry init --name {{PROJECT_NAME}} --python "^$(PYTHON_VERSION)" --no-interaction

install:
	poetry install

add:
	@read -p "Enter packages to add: " pkgs; \
	poetry add $$pkgs

run:
	poetry run python main.py

clean:
	rm -rf .venv poetry.lock

notebook:
	poetry run jupyter notebook

kernel:
	poetry run python -m ipykernel install --user --name="{{PROJECT_NAME}" --display-name="{{PROJECT_NAME}}"

include apply_template.mk
