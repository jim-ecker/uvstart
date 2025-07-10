#include "engine.hpp"
#include <iostream>
#include <vector>
#include <string>

using namespace uvstart;

void print_usage() {
    std::cout << "Usage: uvstart-engine <command> [options]\n";
    std::cout << "\nCommands:\n";
    std::cout << "  detect                     - Detect current backend\n";
    std::cout << "  backends                   - List available backends\n";
    std::cout << "  add <package> [--dev] [--backend <name>]   - Add package\n";
    std::cout << "  remove <package> [--backend <name>]        - Remove package\n";
    std::cout << "  sync [--dev] [--backend <name>]            - Sync packages\n";
    std::cout << "  run <command...> [--backend <name>]        - Run command\n";
    std::cout << "  list [--backend <name>]                    - List packages\n";
    std::cout << "  version [--backend <name>]                 - Get backend version\n";
    std::cout << "  clean [--backend <name>]                   - Clean project files\n";
    std::cout << "  install-cmd <backend>                       - Get install command\n";
    std::cout << "  clean-files <backend>                       - Get clean files list\n";
    std::cout << "\nOptions:\n";
    std::cout << "  --dev                      - Development dependencies\n";
    std::cout << "  --backend <name>           - Specific backend to use\n";
    std::cout << "  --path <path>              - Project path (default: current directory)\n";
}

int main(int argc, char* argv[]) {
    if (argc < 2) {
        print_usage();
        return 1;
    }
    
    std::string command = argv[1];
    std::string project_path = ".";
    std::string backend = "";
    bool dev = false;
    
    // Parse common options
    std::vector<std::string> args;
    for (int i = 2; i < argc; ++i) {
        std::string arg = argv[i];
        
        if (arg == "--dev") {
            dev = true;
        } else if (arg == "--backend" && i + 1 < argc) {
            backend = argv[++i];
        } else if (arg == "--path" && i + 1 < argc) {
            project_path = argv[++i];
        } else {
            args.push_back(arg);
        }
    }
    
    Engine engine(project_path);
    OperationResult result(true, "", "", 0);
    
    if (command == "detect") {
        auto detected = engine.detect_backend();
        if (detected) {
            std::cout << *detected << std::endl;
            return 0;
        } else {
            std::cout << "none" << std::endl;
            return 1;
        }
    } 
    else if (command == "backends") {
        auto backends = engine.get_available_backends();
        for (const auto& backend : backends) {
            std::cout << backend << std::endl;
        }
        return 0;
    }
    else if (command == "add") {
        if (args.empty()) {
            std::cerr << "Error: Package name required" << std::endl;
            return 1;
        }
        result = engine.add_package(args[0], dev, backend);
    }
    else if (command == "remove") {
        if (args.empty()) {
            std::cerr << "Error: Package name required" << std::endl;
            return 1;
        }
        result = engine.remove_package(args[0], backend);
    }
    else if (command == "sync") {
        result = engine.sync_packages(dev, backend);
    }
    else if (command == "run") {
        if (args.empty()) {
            std::cerr << "Error: Command required" << std::endl;
            return 1;
        }
        result = engine.run_command(args, backend);
    }
    else if (command == "list") {
        result = engine.list_packages(backend);
    }
    else if (command == "version") {
        result = engine.get_version(backend);
    }
    else if (command == "clean") {
        result = engine.clean_project(backend);
    }
    else if (command == "install-cmd") {
        if (args.empty()) {
            std::cerr << "Error: Backend name required" << std::endl;
            return 1;
        }
        std::string install_cmd = engine.get_install_command(args[0]);
        if (install_cmd.empty()) {
            std::cerr << "Error: Unknown backend: " << args[0] << std::endl;
            return 1;
        }
        std::cout << install_cmd << std::endl;
        return 0;
    }
    else if (command == "clean-files") {
        if (args.empty()) {
            std::cerr << "Error: Backend name required" << std::endl;
            return 1;
        }
        auto clean_files = engine.get_clean_files(args[0]);
        for (const auto& file : clean_files) {
            std::cout << file << std::endl;
        }
        return 0;
    }
    else {
        std::cerr << "Error: Unknown command: " << command << std::endl;
        print_usage();
        return 1;
    }
    
    // Output result
    if (!result.output.empty()) {
        std::cout << result.output;
    }
    if (!result.error.empty()) {
        std::cerr << result.error;
    }
    
    return result.exit_code;
} 