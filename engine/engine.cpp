#include "engine.hpp"
#include <filesystem>
#include <fstream>
#include <sstream>
#include <cstdlib>
#include <unistd.h>
#include <sys/wait.h>

namespace uvstart {

Engine::Engine(const std::string& project_path) : project_path_(project_path) {}

std::optional<std::string> Engine::detect_backend() const {
    const auto& backends = registry_.get_all_backends();
    
    // First pass: check for lock files and specific files
    for (const auto& [name, config] : backends) {
        for (const auto& file : config->detection_files) {
            std::string full_path = project_path_ + "/" + file;
            if (file_exists(full_path)) {
                return name;
            }
        }
    }
    
    // Second pass: check pyproject.toml for backend-specific patterns
    std::string pyproject_path = project_path_ + "/pyproject.toml";
    if (file_exists(pyproject_path)) {
        std::string content = read_file(pyproject_path);
        
        for (const auto& [name, config] : backends) {
            for (const auto& pattern : config->detection_patterns) {
                if (content.find(pattern) != std::string::npos) {
                    return name;
                }
            }
        }
    }
    
    return std::nullopt;
}

std::vector<std::string> Engine::get_available_backends() const {
    return registry_.get_backend_names();
}

bool Engine::is_backend_available(const std::string& backend_name) const {
    return registry_.get_backend(backend_name) != nullptr;
}

OperationResult Engine::add_package(const std::string& package, bool dev, const std::string& backend) {
    std::string resolved_backend = resolve_backend(backend);
    if (resolved_backend.empty()) {
        return OperationResult(false, "", "No backend found or specified", 1);
    }
    
    const BackendConfig* config = registry_.get_backend(resolved_backend);
    if (!config) {
        return OperationResult(false, "", "Backend not found: " + resolved_backend, 1);
    }
    
    auto cmd_template = dev ? config->add_dev_cmd : config->add_cmd;
    auto command = substitute_placeholders(cmd_template, {package});
    
    return execute_command(command);
}

OperationResult Engine::remove_package(const std::string& package, const std::string& backend) {
    std::string resolved_backend = resolve_backend(backend);
    if (resolved_backend.empty()) {
        return OperationResult(false, "", "No backend found or specified", 1);
    }
    
    const BackendConfig* config = registry_.get_backend(resolved_backend);
    if (!config) {
        return OperationResult(false, "", "Backend not found: " + resolved_backend, 1);
    }
    
    auto command = substitute_placeholders(config->remove_cmd, {package});
    return execute_command(command);
}

OperationResult Engine::sync_packages(bool dev, const std::string& backend) {
    std::string resolved_backend = resolve_backend(backend);
    if (resolved_backend.empty()) {
        return OperationResult(false, "", "No backend found or specified", 1);
    }
    
    const BackendConfig* config = registry_.get_backend(resolved_backend);
    if (!config) {
        return OperationResult(false, "", "Backend not found: " + resolved_backend, 1);
    }
    
    auto cmd_template = dev ? config->sync_dev_cmd : config->sync_cmd;
    auto command = substitute_placeholders(cmd_template, {});
    
    return execute_command(command);
}

OperationResult Engine::run_command(const std::vector<std::string>& command, const std::string& backend) {
    std::string resolved_backend = resolve_backend(backend);
    if (resolved_backend.empty()) {
        return OperationResult(false, "", "No backend found or specified", 1);
    }
    
    const BackendConfig* config = registry_.get_backend(resolved_backend);
    if (!config) {
        return OperationResult(false, "", "Backend not found: " + resolved_backend, 1);
    }
    
    std::vector<std::string> full_command = config->run_cmd;
    full_command.insert(full_command.end(), command.begin(), command.end());
    
    return execute_command(full_command);
}

OperationResult Engine::list_packages(const std::string& backend) {
    std::string resolved_backend = resolve_backend(backend);
    if (resolved_backend.empty()) {
        return OperationResult(false, "", "No backend found or specified", 1);
    }
    
    const BackendConfig* config = registry_.get_backend(resolved_backend);
    if (!config) {
        return OperationResult(false, "", "Backend not found: " + resolved_backend, 1);
    }
    
    return execute_command(config->list_cmd);
}

OperationResult Engine::get_version(const std::string& backend) {
    std::string resolved_backend = resolve_backend(backend);
    if (resolved_backend.empty()) {
        return OperationResult(false, "", "No backend found or specified", 1);
    }
    
    const BackendConfig* config = registry_.get_backend(resolved_backend);
    if (!config) {
        return OperationResult(false, "", "Backend not found: " + resolved_backend, 1);
    }
    
    return execute_command(config->version_cmd);
}

OperationResult Engine::clean_project(const std::string& backend) {
    std::string resolved_backend = resolve_backend(backend);
    if (resolved_backend.empty()) {
        return OperationResult(false, "", "No backend found or specified", 1);
    }
    
    const BackendConfig* config = registry_.get_backend(resolved_backend);
    if (!config) {
        return OperationResult(false, "", "Backend not found: " + resolved_backend, 1);
    }
    
    std::string output;
    bool success = true;
    
    for (const auto& file : config->clean_files) {
        std::string full_path = project_path_ + "/" + file;
        try {
            if (std::filesystem::exists(full_path)) {
                std::filesystem::remove_all(full_path);
                output += "Removed: " + file + "\n";
            }
        } catch (const std::exception& e) {
            output += "Failed to remove " + file + ": " + e.what() + "\n";
            success = false;
        }
    }
    
    return OperationResult(success, output, "", success ? 0 : 1);
}

std::string Engine::get_install_command(const std::string& backend) const {
    const BackendConfig* config = registry_.get_backend(backend);
    return config ? config->install_url : "";
}

std::vector<std::string> Engine::get_clean_files(const std::string& backend) const {
    const BackendConfig* config = registry_.get_backend(backend);
    return config ? config->clean_files : std::vector<std::string>{};
}

void Engine::set_project_path(const std::string& path) {
    project_path_ = path;
}

std::string Engine::get_project_path() const {
    return project_path_;
}

std::string Engine::resolve_backend(const std::string& backend) const {
    if (!backend.empty()) {
        return backend;
    }
    
    auto detected = detect_backend();
    return detected ? *detected : "";
}

OperationResult Engine::execute_command(const std::vector<std::string>& command) const {
    if (command.empty()) {
        return OperationResult(false, "", "Empty command", 1);
    }
    
    // Create command string
    std::ostringstream cmd_stream;
    for (size_t i = 0; i < command.size(); ++i) {
        if (i > 0) cmd_stream << " ";
        // Simple escaping for spaces
        if (command[i].find(' ') != std::string::npos) {
            cmd_stream << "\"" << command[i] << "\"";
        } else {
            cmd_stream << command[i];
        }
    }
    
    std::string cmd_str = cmd_stream.str();
    
    // Execute command and capture output
    FILE* pipe = popen(cmd_str.c_str(), "r");
    if (!pipe) {
        return OperationResult(false, "", "Failed to execute command", 1);
    }
    
    std::string output;
    char buffer[128];
    while (fgets(buffer, sizeof(buffer), pipe) != nullptr) {
        output += buffer;
    }
    
    int exit_code = pclose(pipe);
    bool success = (exit_code == 0);
    
    return OperationResult(success, output, success ? "" : output, exit_code);
}

bool Engine::file_exists(const std::string& filename) const {
    return std::filesystem::exists(filename);
}

bool Engine::directory_exists(const std::string& dirname) const {
    return std::filesystem::exists(dirname) && std::filesystem::is_directory(dirname);
}

std::string Engine::read_file(const std::string& filename) const {
    std::ifstream file(filename);
    if (!file) {
        return "";
    }
    
    std::ostringstream content;
    content << file.rdbuf();
    return content.str();
}

std::vector<std::string> Engine::substitute_placeholders(const std::vector<std::string>& cmd_template, 
                                                         const std::vector<std::string>& args) const {
    std::vector<std::string> result = cmd_template;
    
    // Simple placeholder substitution - add args at the end
    result.insert(result.end(), args.begin(), args.end());
    
    return result;
}

} // namespace uvstart 