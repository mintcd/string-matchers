cmake_minimum_required(VERSION 3.10)
project(fdr_matcher C CXX)

set(CMAKE_C_STANDARD 11)
set(CMAKE_CXX_STANDARD 14)

# Detect architecture
include(CheckCSourceCompiles)
check_c_source_compiles("
#if !(defined(__x86_64__) || defined(_M_X64))
#error not 64bit
#endif
int main(void) { return 0; }
" ARCH_64_BIT)

check_c_source_compiles("
#if !(defined(__i386__) || defined(_M_IX86))
#error not 32bit
#endif
int main(void) { return 0; }
" ARCH_32_BIT)

set(ARCH_X86_64 ${ARCH_64_BIT})
set(ARCH_IA32 ${ARCH_32_BIT})

# Check for intrinsics headers
include(CheckIncludeFiles)
include(CheckIncludeFileCXX)
check_include_files(intrin.h HAVE_C_INTRIN_H)
check_include_file_cxx(intrin.h HAVE_CXX_INTRIN_H)
check_include_files(x86intrin.h HAVE_C_X86INTRIN_H)
check_include_file_cxx(x86intrin.h HAVE_CXX_X86INTRIN_H)

# Check for aligned memory allocation functions
include(CheckFunctionExists)
check_function_exists(posix_memalign HAVE_POSIX_MEMALIGN)
check_function_exists(_aligned_malloc HAVE__ALIGNED_MALLOC)

# Generate config.h from template
configure_file(
    ${CMAKE_CURRENT_SOURCE_DIR}/cmake/config.h.in
    ${CMAKE_CURRENT_SOURCE_DIR}/config.h
    @ONLY
)

# Generate hs_version.h from template
set(HS_MAJOR_VERSION 5)
set(HS_MINOR_VERSION 4)
set(HS_PATCH_VERSION 0)
set(HS_VERSION "5.4.0")
string(TIMESTAMP BUILD_DATE "%Y-%m-%d")
configure_file(
    ${CMAKE_CURRENT_SOURCE_DIR}/hs_version.h.in
    ${CMAKE_CURRENT_SOURCE_DIR}/hs_version.h
    @ONLY
)
# Include current directory for headers
include_directories(${CMAKE_CURRENT_SOURCE_DIR})
# Also include parent directory so hwlm/ can find fdr/ includes
get_filename_component(PARENT_DIR ${CMAKE_CURRENT_SOURCE_DIR} DIRECTORY)
include_directories(${PARENT_DIR})

# Find Boost
find_package(Boost REQUIRED)
include_directories(${Boost_INCLUDE_DIRS})

# FDR source files - Runtime
set(FDR_RUNTIME_SOURCES
    fdr/fdr.c
    fdr/teddy.c
    fdr/teddy_avx2.c
    util/multibit.c
    util/simd_utils.c
    scratch.c
    alloc.c
    database.c
    crc32.c
)

# FDR source files - Compilation
set(FDR_COMPILE_SOURCES
    fdr/fdr_compile.cpp
    fdr/fdr_compile_util.cpp
    fdr/fdr_confirm_compile.cpp
    fdr/flood_compile.cpp
    fdr/teddy_compile.cpp
    fdr/engine_description.cpp
    fdr/fdr_engine_description.cpp
    fdr/teddy_engine_description.cpp
    grey.cpp
    hwlm/hwlm_literal.cpp
    hwlm/hwlm_build.cpp
    hwlm/noodle_build.cpp
    util/ue2string.cpp
    util/target_info.cpp
    util/cpuid_flags.c
    util/compile_error.cpp
    util/alloc.cpp
)

# Create a library
add_library(fdr_matcher STATIC ${FDR_RUNTIME_SOURCES} ${FDR_COMPILE_SOURCES})

# Set C++ standard for the library
target_compile_features(fdr_matcher PUBLIC cxx_std_14)

# Add compiler definitions to suppress warnings
if(MSVC)
    target_compile_options(fdr_matcher PRIVATE /W3 /wd4244 /wd4267)
    target_compile_definitions(fdr_matcher PRIVATE _CRT_SECURE_NO_WARNINGS)
endif()

# Example executable
add_executable(fdr_example example.cpp)
target_link_libraries(fdr_example fdr_matcher)
target_compile_features(fdr_example PUBLIC cxx_std_14)
set_target_properties(fdr_example PROPERTIES
    RUNTIME_OUTPUT_DIRECTORY "${CMAKE_BINARY_DIR}"
)

# Main application executable
add_executable(fdr_main main.cpp)
target_link_libraries(fdr_main fdr_matcher)
target_compile_features(fdr_main PUBLIC cxx_std_17)
set_target_properties(fdr_main PROPERTIES
    RUNTIME_OUTPUT_DIRECTORY "${CMAKE_BINARY_DIR}"
    OUTPUT_NAME "fdr"
)

# Test patterns executable
add_executable(test_patterns test_patterns.cpp)
target_link_libraries(test_patterns fdr_matcher)
target_compile_features(test_patterns PUBLIC cxx_std_14)
