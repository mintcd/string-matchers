cmake_minimum_required(VERSION 3.10)
project(dfc_matcher)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Example executable (standalone, no library needed for demo)
add_executable(dfc_example
    example.cpp
)

# Set output directory
set_target_properties(dfc_example PROPERTIES
    RUNTIME_OUTPUT_DIRECTORY "${CMAKE_BINARY_DIR}"
)

# Main executable
add_executable(dfc_main
    main.cpp
)

set_target_properties(dfc_main PROPERTIES
    RUNTIME_OUTPUT_DIRECTORY "${CMAKE_BINARY_DIR}"
)
