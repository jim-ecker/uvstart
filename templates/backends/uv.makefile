# uvstart project with uv backend
# Backend-agnostic Makefile using shared abstraction layer

PYTHON_VERSION := {{PYTHON_VERSION}}
PROJECT_NAME := {{PROJECT_NAME}}

# Include the shared backend-agnostic Makefile
include $(shell dirname $(realpath $(lastword $(MAKEFILE_LIST))))/../core/shared.makefile 