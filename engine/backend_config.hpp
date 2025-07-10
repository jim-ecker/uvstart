#pragma once

#include <string>
#include <vector>
#include <map>
#include <memory>

namespace uvstart {

/**
 * Configuration for a package manager backend
 * This struct contains all the information needed to interact with a backend
 */
struct BackendConfig {
    std::string name;
    
    // Detection files and patterns
    std::vector<std::string> detection_files;
    std::vector<std::string> detection_patterns;  // Patterns to search in pyproject.toml
    
    // Installation information
    std::string install_url;
    
    // Command templates - these define how to translate unified commands
    std::vector<std::string> add_cmd;
    std::vector<std::string> add_dev_cmd;
    std::vector<std::string> remove_cmd;
    std::vector<std::string> sync_cmd;
    std::vector<std::string> sync_dev_cmd;
    std::vector<std::string> run_cmd;
    std::vector<std::string> list_cmd;
    std::vector<std::string> version_cmd;
    
    // Files to clean up
    std::vector<std::string> clean_files;
    
    // Constructor for easy initialization
    BackendConfig(
        const std::string& name,
        const std::vector<std::string>& detection_files,
        const std::vector<std::string>& detection_patterns,
        const std::string& install_url,
        const std::vector<std::string>& add_cmd,
        const std::vector<std::string>& add_dev_cmd,
        const std::vector<std::string>& remove_cmd,
        const std::vector<std::string>& sync_cmd,
        const std::vector<std::string>& sync_dev_cmd,
        const std::vector<std::string>& run_cmd,
        const std::vector<std::string>& list_cmd,
        const std::vector<std::string>& version_cmd,
        const std::vector<std::string>& clean_files
    );
};

/**
 * Registry of all supported backends
 * This class manages backend configurations and provides lookup functionality
 */
class BackendRegistry {
private:
    std::map<std::string, std::unique_ptr<BackendConfig>> backends_;
    
public:
    BackendRegistry();
    
    // Register a new backend configuration
    void register_backend(const std::string& name, std::unique_ptr<BackendConfig> config);
    
    // Get backend configuration by name
    const BackendConfig* get_backend(const std::string& name) const;
    
    // Get all available backend names
    std::vector<std::string> get_backend_names() const;
    
    // Get all backend configurations
    const std::map<std::string, std::unique_ptr<BackendConfig>>& get_all_backends() const;
    
private:
    void initialize_default_backends();
};

} // namespace uvstart 