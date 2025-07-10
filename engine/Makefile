CXX = g++
CXXFLAGS = -std=c++17 -O2 -Wall -Wextra

# Check if we're on macOS or Linux and adjust linker flags accordingly
UNAME_S := $(shell uname -s)
ifeq ($(UNAME_S),Darwin)
    # macOS - use dynamic linking (static linking is tricky on macOS)
    LDFLAGS = 
else
    # Linux - use static linking for portability
    LDFLAGS = -static-libgcc -static-libstdc++
endif

# Source files
SOURCES = backend_config.cpp engine.cpp cli.cpp
OBJECTS = $(SOURCES:.cpp=.o)
TARGET = uvstart-engine

# Default target
all: $(TARGET)

# Build the executable
$(TARGET): $(OBJECTS)
	$(CXX) $(CXXFLAGS) $(OBJECTS) -o $(TARGET) $(LDFLAGS)

# Build object files
%.o: %.cpp
	$(CXX) $(CXXFLAGS) -c $< -o $@

# Clean build artifacts
clean:
	rm -f $(OBJECTS) $(TARGET)

# Install to parent directory for easy access
install: $(TARGET)
	cp $(TARGET) ../

# Test build (compile only)
test-build: $(OBJECTS)
	@echo "Build test successful"

# Dependencies
backend_config.o: backend_config.cpp backend_config.hpp
engine.o: engine.cpp engine.hpp backend_config.hpp
cli.o: cli.cpp engine.hpp backend_config.hpp

.PHONY: all clean install test-build 