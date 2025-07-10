#!/bin/bash

# Simple test script for uvstart functionality
set -e

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

log_test() {
    echo -e "${BLUE}Testing: $1${NC}"
}

log_pass() {
    echo -e "${GREEN}PASS: $1${NC}"
}

log_fail() {
    echo -e "${RED}FAIL: $1${NC}"
}

# Test 1: Check uvstart is available
log_test "uvstart command availability"
if command -v uvstart &> /dev/null; then
    log_pass "uvstart command found"
else
    log_fail "uvstart command not found"
    exit 1
fi

# Test 2: Check help command
log_test "uvstart help command"
if uvstart help &> /dev/null; then
    log_pass "Help command works"
else
    log_fail "Help command failed"
fi

# Test 3: Check doctor command
log_test "uvstart doctor command"
if uvstart doctor --quick &> /dev/null; then
    log_pass "Doctor command works"
else
    log_fail "Doctor command failed"
fi

# Test 4: Check template list
log_test "uvstart template list"
if uvstart template list &> /dev/null; then
    log_pass "Template list works"
else
    log_fail "Template list failed"
fi

# Test 5: Test project creation in temporary directory
log_test "Project creation"
TEMP_DIR=$(mktemp -d)
ORIGINAL_DIR=$(pwd)

cd "$TEMP_DIR"

# Test with Python version detection
PYTHON_VERSION=""
for py_cmd in python3.12 python3.11 python3.10 python3; do
    if command -v "$py_cmd" &> /dev/null; then
        PYTHON_VERSION=$($py_cmd --version | grep -oE '[0-9]+\.[0-9]+' | head -1)
        break
    fi
done

if [[ -n "$PYTHON_VERSION" ]]; then
    if uvstart init "$PYTHON_VERSION" --no-git &> /dev/null; then
        log_pass "Project creation successful"
        
        # Check generated files
        if [[ -f "Makefile" && -f "pyproject.toml" && -f "main.py" ]]; then
            log_pass "Required files generated"
        else
            log_fail "Missing required files"
        fi
    else
        log_fail "Project creation failed"
    fi
else
    log_fail "No suitable Python version found"
fi

# Cleanup
cd "$ORIGINAL_DIR"
rm -rf "$TEMP_DIR"

echo
echo "Basic tests completed!"
echo "Run 'uvstart doctor' for comprehensive environment check." 