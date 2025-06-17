# Apply a feature template (e.g. notebook, cli, web, etc.)
# Usage:
#   make template TEMPLATE=cli
#   make list-templates

TEMPLATE ?=

template:
	@if [ -z "$(TEMPLATE)" ]; then \
		echo "Please specify a template using: make template TEMPLATE=cli"; \
		exit 1; \
	fi
	@TEMPLATE_DIR="./templates/features/$(TEMPLATE)"
	@if [ ! -d "$$TEMPLATE_DIR" ]; then \
		echo "Template '$(TEMPLATE)' not found in templates/features/"; \
		exit 1; \
	fi
	@echo "Applying template: $(TEMPLATE)"
	@cp -r $$TEMPLATE_DIR/* .
	@echo "Template '$(TEMPLATE)' applied"

list-templates:
	@echo "Available templates:"
	@ls templates/features/
