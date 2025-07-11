#!/bin/bash

# Comprehensive test suite for uvstart functionality
set -e

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Test counters
TESTS_RUN=0
TESTS_PASSED=0
TESTS_FAILED=0

# Test results
FAILED_TESTS=()

log_test() {
    echo -e "${BLUE}[TEST] $1${NC}"
    TESTS_RUN=$((TESTS_RUN + 1))
}

log_pass() {
    echo -e "${GREEN}✓ PASS: $1${NC}"
    TESTS_PASSED=$((TESTS_PASSED + 1))
}

log_fail() {
    echo -e "${RED}✗ FAIL: $1${NC}"
    TESTS_FAILED=$((TESTS_FAILED + 1))
    FAILED_TESTS+=("$1")
}

log_info() {
    echo -e "${YELLOW}ℹ INFO: $1${NC}"
}

# Clean up function
cleanup() {
    if [[ -n "$TEST_DIR" && -d "$TEST_DIR" ]]; then
        rm -rf "$TEST_DIR"
    fi
    if [[ -n "$ORIGINAL_DIR" ]]; then
        cd "$ORIGINAL_DIR"
    fi
}

# Set up trap for cleanup
trap cleanup EXIT

# Create test environment
setup_test_env() {
    log_info "Setting up test environment..."
    ORIGINAL_DIR=$(pwd)
    TEST_DIR=$(mktemp -d)
    export TEST_DIR
    export ORIGINAL_DIR
    
    # Detect Python version for testing
    PYTHON_VERSION=""
    for py_cmd in python3.12 python3.11 python3.10 python3; do
        if command -v "$py_cmd" &> /dev/null; then
            PYTHON_VERSION=$($py_cmd --version | grep -oE '[0-9]+\.[0-9]+' | head -1)
            break
        fi
    done
    export PYTHON_VERSION
    
    log_info "Test directory: $TEST_DIR"
    log_info "Python version: $PYTHON_VERSION"
}

# Test 1: Basic command availability
test_command_availability() {
    log_test "uvstart command availability"
    if command -v uvstart &> /dev/null; then
        log_pass "uvstart command found"
    else
        log_fail "uvstart command not found"
    fi
}

# Test 2: Help and basic commands
test_basic_commands() {
    log_test "Basic commands (help, doctor, template list)"
    
    # Test help command
    if uvstart --help &> /dev/null; then
        log_pass "Help command works"
    else
        log_fail "Help command failed"
    fi
    
    # Test doctor command
    if uvstart doctor &> /dev/null; then
        log_pass "Doctor command works"
    else
        log_fail "Doctor command failed"
    fi
    
    # Test template list
    if uvstart template list &> /dev/null; then
        log_pass "Template list works"
    else
        log_fail "Template list failed"
    fi
}

# Test 3: Project initialization
test_project_init() {
    log_test "Project initialization"
    
    cd "$TEST_DIR"
    mkdir test-init
    cd test-init
    
    if [[ -n "$PYTHON_VERSION" ]]; then
        if uvstart init . --name test-project --no-git --backend uv &> /dev/null; then
            log_pass "Project initialization successful"
            
            # Check generated files (updated to match actual output)
            if [[ -f "pyproject.toml" && -f "main.py" && -f "README.md" ]]; then
                log_pass "Required project files generated"
            else
                log_fail "Missing required project files"
            fi
            
            # Check package structure
            if [[ -d "test_project" && -f "test_project/__init__.py" ]]; then
                log_pass "Python package structure created"
            else
                log_fail "Python package structure missing"
            fi
        else
            log_fail "Project initialization failed"
        fi
    else
        log_fail "No suitable Python version found for testing"
    fi
    
    cd "$TEST_DIR"
}

# Test 4: Template features
test_template_features() {
    log_test "Template features (CLI, web, notebook)"
    
    cd "$TEST_DIR"
    
    # Test CLI template
    if uvstart generate cli-test --features cli --no-git --backend uv &> /dev/null; then
        if [[ -d "cli-test" && -f "cli-test/pyproject.toml" ]]; then
            log_pass "CLI template generation"
        else
            log_fail "CLI template files missing"
        fi
    else
        log_fail "CLI template generation failed"
    fi
    
    # Test web template
    if uvstart generate web-test --features web --no-git --backend uv &> /dev/null; then
        if [[ -d "web-test" && -f "web-test/pyproject.toml" ]]; then
            log_pass "Web template generation"
        else
            log_fail "Web template files missing"
        fi
    else
        log_fail "Web template generation failed"
    fi
    
    cd "$TEST_DIR"
}

# Test 5: From-directory template creation
test_from_directory_template() {
    log_test "From-directory template creation"
    
    cd "$TEST_DIR"
    
    # Create a sample project to turn into a template
    mkdir sample-project
    cd sample-project
    
    # Create sample files
    cat > main.py << 'EOF'
def main():
    print("Hello from sample project!")

if __name__ == "__main__":
    main()
EOF
    
    cat > config.json << 'EOF'
{
    "app_name": "sample-app",
    "version": "1.0.0",
    "debug": true
}
EOF
    
    mkdir src
    cat > src/__init__.py << 'EOF'
"""Sample package"""
__version__ = "1.0.0"
EOF
    
    mkdir tests
    cat > tests/test_main.py << 'EOF'
def test_main():
    from main import main
    assert main is not None
EOF
    
    # Test creating template from this directory
    if uvstart template from-directory sample-template --description "A sample template" &> /dev/null; then
        log_pass "Template creation from directory"
        
        # Verify template was created
        if uvstart template list | grep -q "sample-template" &> /dev/null; then
            log_pass "Template appears in template list"
        else
            log_fail "Template not found in list"
        fi
    else
        log_fail "Template creation from directory failed"
    fi
    
    cd "$TEST_DIR"
}

# Test 6: Project analysis
test_project_analysis() {
    log_test "Project analysis functionality"
    
    cd "$TEST_DIR"
    
    # Use an existing project or create one
    if [[ -d "test-init" ]]; then
        cd test-init
        
        if uvstart --path . analyze &> /dev/null; then
            log_pass "Project analysis command works"
        else
            log_fail "Project analysis command failed"
        fi
        
        cd "$TEST_DIR"
    else
        log_fail "No project available for analysis testing"
    fi
}

# Test 7: Configuration management
test_configuration() {
    log_test "Configuration management"
    
    # Test with a temporary config file
    CONFIG_DIR="$HOME/.local/uvstart"
    CONFIG_FILE="$CONFIG_DIR/config.yaml"
    BACKUP_CONFIG=""
    
    # Backup existing config if it exists
    if [[ -f "$CONFIG_FILE" ]]; then
        BACKUP_CONFIG="$CONFIG_FILE.backup.$$"
        cp "$CONFIG_FILE" "$BACKUP_CONFIG"
    fi
    
    # Create test config
    mkdir -p "$CONFIG_DIR"
    cat > "$CONFIG_FILE" << 'EOF'
default_backend: uv
default_python_version: 3.11
author: Test User
email: test@example.com
EOF
    
    # Test that uvstart reads the config (implicit test via doctor command)
    if uvstart doctor &> /dev/null; then
        log_pass "Configuration system integration"
    else
        log_fail "Configuration system integration failed"
    fi
    
    # Restore backup config
    if [[ -n "$BACKUP_CONFIG" ]]; then
        mv "$BACKUP_CONFIG" "$CONFIG_FILE"
    else
        rm -f "$CONFIG_FILE"
    fi
}

# Test 8: Template info command
test_template_info() {
    log_test "Template info command"
    
    # Test getting info for a built-in template
    if uvstart template info cli &> /dev/null; then
        log_pass "Template info command works"
    else
        log_fail "Template info command failed"
    fi
}

# Test 9: Engine integration (if engine is available)
test_engine_integration() {
    log_test "C++ engine integration"
    
    ENGINE_PATH="$ORIGINAL_DIR/engine/uvstart-engine"
    
    if [[ -x "$ENGINE_PATH" ]]; then
        # Test engine directly
        if "$ENGINE_PATH" backends &> /dev/null; then
            log_pass "C++ engine executable works"
        else
            log_fail "C++ engine execution failed"
        fi
        
        # Test uvstart commands that use the engine
        cd "$TEST_DIR"
        if [[ -d "test-init" ]]; then
            cd test-init
            
            # Test backend detection
            if uvstart info &> /dev/null; then
                log_pass "Backend info via engine"
            else
                log_fail "Backend info via engine failed"
            fi
            
            cd "$TEST_DIR"
        fi
    else
        log_fail "C++ engine not found or not executable"
    fi
}

# Test 10: Research template functionality
test_research_template() {
    log_test "Research template functionality"
    
    cd "$TEST_DIR"
    
    # Create a research-like project
    mkdir research-project
    cd research-project
    
    # Create typical research files
    cat > experiment.yaml << 'EOF'
name: test_experiment
seed: 42
learning_rate: 0.001
batch_size: 32
epochs: 100
EOF
    
    cat > analyze.py << 'EOF'
import json

def run_experiment(config):
    print(f"Running experiment with config: {config}")
    return {"accuracy": 0.95, "loss": 0.05}

if __name__ == "__main__":
    with open("experiment.yaml") as f:
        import yaml
        config = yaml.safe_load(f)
    results = run_experiment(config)
    print(results)
EOF
    
    mkdir data
    touch data/.gitkeep
    
    # Test creating research template
    if uvstart template research research-template --description "Research template for experiments" &> /dev/null; then
        log_pass "Research template creation"
    else
        log_fail "Research template creation failed"
    fi
    
    cd "$TEST_DIR"
}

# Test 11: Error handling and edge cases
test_error_handling() {
    log_test "Error handling and edge cases"
    
    # Test invalid template name (check output instead of exit code)
    if uvstart template info non-existent-template 2>&1 | grep -q "not found"; then
        log_pass "Proper error handling for non-existent template"
    else
        log_fail "Should show error message for non-existent template"
    fi
    
    # Test invalid command
    if ! uvstart invalid-command &> /dev/null; then
        log_pass "Proper error handling for invalid command"
    else
        log_fail "Should fail for invalid command"
    fi
    
    # Test project creation with invalid path (check for reasonable error)
    if uvstart generate invalid-project --output "/root/cannot-write-here" 2>&1 | grep -q -i "error\|permission\|cannot\|invalid"; then
        log_pass "Proper error handling for invalid paths"
    else
        log_fail "Should show error for problematic paths"
    fi
}

# Test 12: Multiple backend support
test_backend_support() {
    log_test "Multiple backend support"
    
    cd "$TEST_DIR"
    
    # Test different backends if available
    for backend in uv poetry; do
        if command -v "$backend" &> /dev/null; then
            mkdir "test-$backend"
            cd "test-$backend"
            
            if uvstart init . --name "test-$backend" --backend "$backend" --no-git &> /dev/null; then
                log_pass "$backend backend project creation"
            else
                log_fail "$backend backend project creation failed"
            fi
            
            cd "$TEST_DIR"
        else
            log_info "$backend not available for testing"
        fi
    done
}

# Main test execution
main() {
    echo "uvstart Comprehensive Test Suite"
    echo "================================="
    echo
    
    setup_test_env
    
    # Run all tests
    test_command_availability
    test_basic_commands
    test_project_init
    test_template_features
    test_from_directory_template
    test_project_analysis
    test_configuration
    test_template_info
    test_engine_integration
    test_research_template
    test_error_handling
    test_backend_support
    
    # Print summary
    echo
    echo "================================="
    echo "Test Summary"
    echo "================================="
    echo "Tests run: $TESTS_RUN"
    echo -e "Tests passed: ${GREEN}$TESTS_PASSED${NC}"
    echo -e "Tests failed: ${RED}$TESTS_FAILED${NC}"
    
    if [[ $TESTS_FAILED -gt 0 ]]; then
        echo
        echo "Failed tests:"
        for test in "${FAILED_TESTS[@]}"; do
            echo -e "  ${RED}✗ $test${NC}"
        done
        echo
        echo "Please fix the failing tests before deploying."
        exit 1
    else
        echo
        echo -e "${GREEN}All tests passed! 🎉${NC}"
        echo "uvstart is ready for deployment."
        exit 0
    fi
}

# Run main function
main "$@" 