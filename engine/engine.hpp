#pragma once

#include "backend_config.hpp"
#include <string>
#include <vector>
#include <optional>

namespace uvstart {

/**
 * Result of a backend operation
 */
struct OperationResult {
    bool success;
    std::string output;
    std::string error;
    int exit_code;
    
    OperationResult(bool success, const std::string& output, const std::string& error, int exit_code)
        : success(success), output(output), error(error), exit_code(exit_code) {}
};

/**
 * Main backend abstraction engine
 * This class provides the core functionality for backend detection and command execution
 */
class Engine {
private:
    BackendRegistry registry_;
    std::string project_path_;
    
public:
    Engine(const std::string& project_path = ".");
    
    // Backend detection
    std::optional<std::string> detect_backend() const;
    std::vector<std::string> get_available_backends() const;
    bool is_backend_available(const std::string& backend_name) const;
    
    // Command execution
    OperationResult add_package(const std::string& package, bool dev = false, const std::string& backend = "");
    OperationResult remove_package(const std::string& package, const std::string& backend = "");
    OperationResult sync_packages(bool dev = false, const std::string& backend = "");
    OperationResult run_command(const std::vector<std::string>& command, const std::string& backend = "");
    OperationResult list_packages(const std::string& backend = "");
    OperationResult get_version(const std::string& backend = "");
    OperationResult clean_project(const std::string& backend = "");
    
    // Information retrieval
    std::string get_install_command(const std::string& backend) const;
    std::vector<std::string> get_clean_files(const std::string& backend) const;
    
    // Set project path
    void set_project_path(const std::string& path);
    std::string get_project_path() const;
    
private:
    // Helper methods
    std::string resolve_backend(const std::string& backend) const;
    OperationResult execute_command(const std::vector<std::string>& command) const;
    bool file_exists(const std::string& filename) const;
    bool directory_exists(const std::string& dirname) const;
    std::string read_file(const std::string& filename) const;
    std::vector<std::string> substitute_placeholders(const std::vector<std::string>& cmd_template, 
                                                      const std::vector<std::string>& args) const;
};

} // namespace uvstart 