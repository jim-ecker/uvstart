#include "backend_config.hpp"
#include <memory>

namespace uvstart {

// BackendConfig constructor
BackendConfig::BackendConfig(
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
    const std::vector<std::string>& clean_files)
    : name(name)
    , detection_files(detection_files)
    , detection_patterns(detection_patterns)
    , install_url(install_url)
    , add_cmd(add_cmd)
    , add_dev_cmd(add_dev_cmd)
    , remove_cmd(remove_cmd)
    , sync_cmd(sync_cmd)
    , sync_dev_cmd(sync_dev_cmd)
    , run_cmd(run_cmd)
    , list_cmd(list_cmd)
    , version_cmd(version_cmd)
    , clean_files(clean_files) {
}

// BackendRegistry constructor
BackendRegistry::BackendRegistry() {
    initialize_default_backends();
}

void BackendRegistry::register_backend(const std::string& name, std::unique_ptr<BackendConfig> config) {
    backends_[name] = std::move(config);
}

const BackendConfig* BackendRegistry::get_backend(const std::string& name) const {
    auto it = backends_.find(name);
    return (it != backends_.end()) ? it->second.get() : nullptr;
}

std::vector<std::string> BackendRegistry::get_backend_names() const {
    std::vector<std::string> names;
    for (const auto& pair : backends_) {
        names.push_back(pair.first);
    }
    return names;
}

const std::map<std::string, std::unique_ptr<BackendConfig>>& BackendRegistry::get_all_backends() const {
    return backends_;
}

void BackendRegistry::initialize_default_backends() {
    // PDM Backend Configuration
    register_backend("pdm", std::make_unique<BackendConfig>(
        "pdm",
        std::vector<std::string>{"pdm.lock"},                    // Detection files
        std::vector<std::string>{},                              // Detection patterns
        "curl -sSL https://pdm-project.org/install-pdm.py | python3 -",  // Install URL
        std::vector<std::string>{"pdm", "add"},                  // Add command
        std::vector<std::string>{"pdm", "add", "--dev"},         // Add dev command  
        std::vector<std::string>{"pdm", "remove"},               // Remove command
        std::vector<std::string>{"pdm", "sync"},                 // Sync command
        std::vector<std::string>{"pdm", "sync", "--dev"},        // Sync dev command
        std::vector<std::string>{"pdm", "run"},                  // Run command
        std::vector<std::string>{"pdm", "list"},                 // List command
        std::vector<std::string>{"pdm", "--version"},            // Version command
        std::vector<std::string>{"pdm.lock", ".pdm-python", "__pypackages__"}  // Clean files
    ));
    
    // uv Backend Configuration
    register_backend("uv", std::make_unique<BackendConfig>(
        "uv",
        std::vector<std::string>{"uv.lock", "__pypackages__"},   // Detection files
        std::vector<std::string>{"[tool.uv]"},                   // Detection patterns
        "curl -LsSf https://astral.sh/uv/install.sh | sh",       // Install URL
        std::vector<std::string>{"uv", "add"},                   // Add command
        std::vector<std::string>{"uv", "add", "--group", "dev"}, // Add dev command
        std::vector<std::string>{"uv", "remove"},                // Remove command
        std::vector<std::string>{"uv", "sync"},                  // Sync command
        std::vector<std::string>{"uv", "sync", "--group", "dev"}, // Sync dev command
        std::vector<std::string>{"uv", "run"},                   // Run command
        std::vector<std::string>{"uv", "pip", "list"},           // List command
        std::vector<std::string>{"uv", "--version"},             // Version command
        std::vector<std::string>{"uv.lock", "__pypackages__"}    // Clean files
    ));
    
    // Poetry Backend Configuration
    register_backend("poetry", std::make_unique<BackendConfig>(
        "poetry",
        std::vector<std::string>{"poetry.lock"},                 // Detection files
        std::vector<std::string>{"poetry"},                      // Detection patterns (in pyproject.toml)
        "curl -sSL https://install.python-poetry.org | python3 -", // Install URL
        std::vector<std::string>{"poetry", "add"},               // Add command
        std::vector<std::string>{"poetry", "add", "--group", "dev"}, // Add dev command
        std::vector<std::string>{"poetry", "remove"},            // Remove command
        std::vector<std::string>{"poetry", "install"},           // Sync command
        std::vector<std::string>{"poetry", "install", "--with", "dev"}, // Sync dev command
        std::vector<std::string>{"poetry", "run"},               // Run command
        std::vector<std::string>{"poetry", "show"},              // List command
        std::vector<std::string>{"poetry", "--version"},         // Version command
        std::vector<std::string>{"poetry.lock", ".venv"}         // Clean files
    ));
    
    // Rye Backend Configuration
    register_backend("rye", std::make_unique<BackendConfig>(
        "rye",
        std::vector<std::string>{"requirements.lock"},           // Detection files
        std::vector<std::string>{},                              // Detection patterns
        "curl -sSf https://rye-up.com/get | bash",               // Install URL
        std::vector<std::string>{"rye", "add"},                  // Add command
        std::vector<std::string>{"rye", "add", "--dev"},         // Add dev command
        std::vector<std::string>{"rye", "remove"},               // Remove command
        std::vector<std::string>{"rye", "sync"},                 // Sync command
        std::vector<std::string>{"rye", "sync"},                 // Sync dev command (same as sync)
        std::vector<std::string>{"rye", "run"},                  // Run command
        std::vector<std::string>{"rye", "list"},                 // List command
        std::vector<std::string>{"rye", "--version"},            // Version command
        std::vector<std::string>{"requirements.lock", ".venv"}   // Clean files
    ));
    
    // Hatch Backend Configuration
    register_backend("hatch", std::make_unique<BackendConfig>(
        "hatch",
        std::vector<std::string>{"hatch.lock"},                  // Detection files (hypothetical)
        std::vector<std::string>{"[tool.hatch"},                 // Detection patterns - more specific
        "pipx install hatch",                                    // Install URL
        std::vector<std::string>{"hatch", "add"},                // Add command
        std::vector<std::string>{"hatch", "add", "--dev"},       // Add dev command
        std::vector<std::string>{"hatch", "remove"},             // Remove command
        std::vector<std::string>{"hatch", "dep", "sync"},        // Sync command
        std::vector<std::string>{"hatch", "dep", "sync"},        // Sync dev command
        std::vector<std::string>{"hatch", "run"},                // Run command
        std::vector<std::string>{"hatch", "dep", "show"},        // List command
        std::vector<std::string>{"hatch", "--version"},          // Version command
        std::vector<std::string>{".venv"}                        // Clean files
    ));
}

} // namespace uvstart