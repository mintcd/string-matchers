#!/usr/bin/env python3
"""
FDR String Matcher Setup Script

This script automatically downloads all necessary files from the Hyperscan GitHub
repository, sets up the directory structure, and builds the FDR example.

Usage:
    python config.py          # Download files and build
    python config.py --clean  # Clean downloaded and build files only
"""

import os
import sys
import urllib.request
import subprocess
from pathlib import Path

# Hyperscan GitHub repository configuration
HYPERSCAN_REPO = "https://raw.githubusercontent.com/intel/hyperscan/master"
HYPERSCAN_SRC = f"{HYPERSCAN_REPO}/src"

# Files to download from Hyperscan repository
FILES_TO_DOWNLOAD = {
    # FDR core runtime files
    "fdr/fdr/fdr.c": f"{HYPERSCAN_SRC}/fdr/fdr.c",
    "fdr/fdr/fdr.h": f"{HYPERSCAN_SRC}/fdr/fdr.h",
    "fdr/fdr/fdr_internal.h": f"{HYPERSCAN_SRC}/fdr/fdr_internal.h",
    "fdr/fdr/fdr_loadval.h": f"{HYPERSCAN_SRC}/fdr/fdr_loadval.h",
    "fdr/fdr/fdr_confirm.h": f"{HYPERSCAN_SRC}/fdr/fdr_confirm.h",
    "fdr/fdr/fdr_confirm_runtime.h": f"{HYPERSCAN_SRC}/fdr/fdr_confirm_runtime.h",
    
    # FDR compilation files
    "fdr/fdr/fdr_compile.cpp": f"{HYPERSCAN_SRC}/fdr/fdr_compile.cpp",
    "fdr/fdr/fdr_compile.h": f"{HYPERSCAN_SRC}/fdr/fdr_compile.h",
    "fdr/fdr/fdr_compile_internal.h": f"{HYPERSCAN_SRC}/fdr/fdr_compile_internal.h",
    "fdr/fdr/fdr_compile_util.cpp": f"{HYPERSCAN_SRC}/fdr/fdr_compile_util.cpp",
    "fdr/fdr/fdr_confirm_compile.cpp": f"{HYPERSCAN_SRC}/fdr/fdr_confirm_compile.cpp",
    
    # TEDDY engine files
    "fdr/fdr/teddy.c": f"{HYPERSCAN_SRC}/fdr/teddy.c",
    "fdr/fdr/teddy.h": f"{HYPERSCAN_SRC}/fdr/teddy.h",
    "fdr/fdr/teddy_avx2.c": f"{HYPERSCAN_SRC}/fdr/teddy_avx2.c",
    "fdr/fdr/teddy_internal.h": f"{HYPERSCAN_SRC}/fdr/teddy_internal.h",
    "fdr/fdr/teddy_runtime_common.h": f"{HYPERSCAN_SRC}/fdr/teddy_runtime_common.h",
    "fdr/fdr/teddy_compile.cpp": f"{HYPERSCAN_SRC}/fdr/teddy_compile.cpp",
    "fdr/fdr/teddy_compile.h": f"{HYPERSCAN_SRC}/fdr/teddy_compile.h",
    
    # Engine description files
    "fdr/fdr/engine_description.cpp": f"{HYPERSCAN_SRC}/fdr/engine_description.cpp",
    "fdr/fdr/engine_description.h": f"{HYPERSCAN_SRC}/fdr/engine_description.h",
    "fdr/fdr/fdr_engine_description.cpp": f"{HYPERSCAN_SRC}/fdr/fdr_engine_description.cpp",
    "fdr/fdr/fdr_engine_description.h": f"{HYPERSCAN_SRC}/fdr/fdr_engine_description.h",
    "fdr/fdr/teddy_engine_description.cpp": f"{HYPERSCAN_SRC}/fdr/teddy_engine_description.cpp",
    "fdr/fdr/teddy_engine_description.h": f"{HYPERSCAN_SRC}/fdr/teddy_engine_description.h",
    
    # Flood detection files
    "fdr/fdr/flood_compile.cpp": f"{HYPERSCAN_SRC}/fdr/flood_compile.cpp",
    "fdr/fdr/flood_runtime.h": f"{HYPERSCAN_SRC}/fdr/flood_runtime.h",
    
    # Core Hyperscan files
    "fdr/grey.cpp": f"{HYPERSCAN_SRC}/grey.cpp",
    "fdr/grey.h": f"{HYPERSCAN_SRC}/grey.h",
    "fdr/ue2common.h": f"{HYPERSCAN_SRC}/ue2common.h",
    "fdr/hs_common.h": f"{HYPERSCAN_SRC}/hs_common.h",
    "fdr/hs_compile.h": f"{HYPERSCAN_SRC}/hs_compile.h",
    "fdr/hs.h": f"{HYPERSCAN_SRC}/hs.h",
    "fdr/hs_runtime.h": f"{HYPERSCAN_SRC}/hs_runtime.h",
    "fdr/hs_internal.h": f"{HYPERSCAN_SRC}/hs_internal.h",
    "fdr/hs_version.h.in": f"{HYPERSCAN_SRC}/hs_version.h.in",
    "fdr/cmake/config.h.in": f"{HYPERSCAN_REPO}/cmake/config.h.in",
    "fdr/scratch.h": f"{HYPERSCAN_SRC}/scratch.h",
    "fdr/scratch.c": f"{HYPERSCAN_SRC}/scratch.c",
    "fdr/alloc.c": f"{HYPERSCAN_SRC}/alloc.c",
    "fdr/allocator.h": f"{HYPERSCAN_SRC}/allocator.h",
    "fdr/state.h": f"{HYPERSCAN_SRC}/state.h",
    "fdr/database.h": f"{HYPERSCAN_SRC}/database.h",
    "fdr/database.c": f"{HYPERSCAN_SRC}/database.c",
    "fdr/crc32.h": f"{HYPERSCAN_SRC}/crc32.h",
    "fdr/crc32.c": f"{HYPERSCAN_SRC}/crc32.c",
    "fdr/compiler/compiler.h": f"{HYPERSCAN_SRC}/compiler/compiler.h",
    
    # HWLM (Hardware Literal Matcher) files
    "fdr/hwlm/hwlm.h": f"{HYPERSCAN_SRC}/hwlm/hwlm.h",
    "fdr/hwlm/hwlm_build.h": f"{HYPERSCAN_SRC}/hwlm/hwlm_build.h",
    "fdr/hwlm/hwlm_build.cpp": f"{HYPERSCAN_SRC}/hwlm/hwlm_build.cpp",
    "fdr/hwlm/hwlm_internal.h": f"{HYPERSCAN_SRC}/hwlm/hwlm_internal.h",
    "fdr/hwlm/hwlm_literal.h": f"{HYPERSCAN_SRC}/hwlm/hwlm_literal.h",
    "fdr/hwlm/hwlm_literal.cpp": f"{HYPERSCAN_SRC}/hwlm/hwlm_literal.cpp",
    "fdr/hwlm/noodle_engine.h": f"{HYPERSCAN_SRC}/hwlm/noodle_engine.h",
    "fdr/hwlm/noodle_build.h": f"{HYPERSCAN_SRC}/hwlm/noodle_build.h",
    "fdr/hwlm/noodle_build.cpp": f"{HYPERSCAN_SRC}/hwlm/noodle_build.cpp",
    "fdr/hwlm/noodle_internal.h": f"{HYPERSCAN_SRC}/hwlm/noodle_internal.h",
    
    # NFA files
    "fdr/nfa/nfa_api.h": f"{HYPERSCAN_SRC}/nfa/nfa_api.h",
    "fdr/nfa/nfa_api_queue.h": f"{HYPERSCAN_SRC}/nfa/nfa_api_queue.h",
    "fdr/nfa/nfa_internal.h": f"{HYPERSCAN_SRC}/nfa/nfa_internal.h",
    "fdr/nfa/nfa_kind.h": f"{HYPERSCAN_SRC}/nfa/nfa_kind.h",
    "fdr/nfa/accel.h": f"{HYPERSCAN_SRC}/nfa/accel.h",
    "fdr/nfa/callback.h": f"{HYPERSCAN_SRC}/nfa/callback.h",
    
    # SOM files
    "fdr/som/som.h": f"{HYPERSCAN_SRC}/som/som.h",
    
    # ROSE engine files
    "fdr/rose/rose_graph.h": f"{HYPERSCAN_SRC}/rose/rose_graph.h",
    "fdr/rose/rose_build.h": f"{HYPERSCAN_SRC}/rose/rose_build.h",
    "fdr/rose/rose_types.h": f"{HYPERSCAN_SRC}/rose/rose_types.h",
    "fdr/rose/rose_internal.h": f"{HYPERSCAN_SRC}/rose/rose_internal.h",
    "fdr/rose/rose_common.h": f"{HYPERSCAN_SRC}/rose/rose_common.h",
    
    # Utility headers
    "fdr/util/arch.h": f"{HYPERSCAN_SRC}/util/arch.h",
    "fdr/util/bitutils.h": f"{HYPERSCAN_SRC}/util/bitutils.h",
    "fdr/util/compare.h": f"{HYPERSCAN_SRC}/util/compare.h",
    "fdr/util/intrinsics.h": f"{HYPERSCAN_SRC}/util/intrinsics.h",
    "fdr/util/join.h": f"{HYPERSCAN_SRC}/util/join.h",
    "fdr/util/masked_move.h": f"{HYPERSCAN_SRC}/util/masked_move.h",
    "fdr/util/multibit.h": f"{HYPERSCAN_SRC}/util/multibit.h",
    "fdr/util/multibit.c": f"{HYPERSCAN_SRC}/util/multibit.c",
    "fdr/util/multibit_internal.h": f"{HYPERSCAN_SRC}/util/multibit_internal.h",
    "fdr/util/partial_store.h": f"{HYPERSCAN_SRC}/util/partial_store.h",
    "fdr/util/popcount.h": f"{HYPERSCAN_SRC}/util/popcount.h",
    "fdr/util/simd_types.h": f"{HYPERSCAN_SRC}/util/simd_types.h",
    "fdr/util/simd_utils.h": f"{HYPERSCAN_SRC}/util/simd_utils.h",
    "fdr/util/simd_utils.c": f"{HYPERSCAN_SRC}/util/simd_utils.c",
    "fdr/util/unaligned.h": f"{HYPERSCAN_SRC}/util/unaligned.h",
    "fdr/util/uniform_ops.h": f"{HYPERSCAN_SRC}/util/uniform_ops.h",
    "fdr/util/container.h": f"{HYPERSCAN_SRC}/util/container.h",
    "fdr/util/dump_mask.h": f"{HYPERSCAN_SRC}/util/dump_mask.h",
    "fdr/util/make_unique.h": f"{HYPERSCAN_SRC}/util/make_unique.h",
    "fdr/util/math.h": f"{HYPERSCAN_SRC}/util/math.h",
    "fdr/util/noncopyable.h": f"{HYPERSCAN_SRC}/util/noncopyable.h",
    "fdr/util/target_info.h": f"{HYPERSCAN_SRC}/util/target_info.h",
    "fdr/util/target_info.cpp": f"{HYPERSCAN_SRC}/util/target_info.cpp",
    "fdr/util/ue2string.h": f"{HYPERSCAN_SRC}/util/ue2string.h",
    "fdr/util/ue2string.cpp": f"{HYPERSCAN_SRC}/util/ue2string.cpp",
    "fdr/util/verify_types.h": f"{HYPERSCAN_SRC}/util/verify_types.h",
    "fdr/util/operators.h": f"{HYPERSCAN_SRC}/util/operators.h",
    "fdr/util/order_check.h": f"{HYPERSCAN_SRC}/util/order_check.h",
    "fdr/util/compile_context.h": f"{HYPERSCAN_SRC}/util/compile_context.h",
    "fdr/util/compile_error.h": f"{HYPERSCAN_SRC}/util/compile_error.h",
    "fdr/util/compile_error.cpp": f"{HYPERSCAN_SRC}/util/compile_error.cpp",
    "fdr/util/alloc.h": f"{HYPERSCAN_SRC}/util/alloc.h",
    "fdr/util/alloc.cpp": f"{HYPERSCAN_SRC}/util/alloc.cpp",
    "fdr/util/report.h": f"{HYPERSCAN_SRC}/util/report.h",
    "fdr/util/fatbit.h": f"{HYPERSCAN_SRC}/util/fatbit.h",
    "fdr/util/bytecode_ptr.h": f"{HYPERSCAN_SRC}/util/bytecode_ptr.h",
    "fdr/util/charreach.h": f"{HYPERSCAN_SRC}/util/charreach.h",
    "fdr/util/charreach.cpp": f"{HYPERSCAN_SRC}/util/charreach.cpp",
    "fdr/util/charreach_util.h": f"{HYPERSCAN_SRC}/util/charreach_util.h",
    "fdr/util/depth.h": f"{HYPERSCAN_SRC}/util/depth.h",
    "fdr/util/ue2_graph.h": f"{HYPERSCAN_SRC}/util/ue2_graph.h",
    "fdr/util/graph.h": f"{HYPERSCAN_SRC}/util/graph.h",
    "fdr/util/hash.h": f"{HYPERSCAN_SRC}/util/hash.h",
    "fdr/util/flat_containers.h": f"{HYPERSCAN_SRC}/util/flat_containers.h",
    "fdr/util/boundary_reports.h": f"{HYPERSCAN_SRC}/util/boundary_reports.h",
    "fdr/util/bitfield.h": f"{HYPERSCAN_SRC}/util/bitfield.h",
    "fdr/util/small_vector.h": f"{HYPERSCAN_SRC}/util/small_vector.h",
    "fdr/util/hash_dynamic_bitset.h": f"{HYPERSCAN_SRC}/util/hash_dynamic_bitset.h",
    "fdr/util/cpuid_flags.h": f"{HYPERSCAN_SRC}/util/cpuid_flags.h",
    "fdr/util/cpuid_flags.c": f"{HYPERSCAN_SRC}/util/cpuid_flags.c",
    
    # Parser files (needed by hwlm_build.cpp)
    "fdr/parser/position.h": f"{HYPERSCAN_SRC}/parser/position.h",
    "fdr/parser/position_info.h": f"{HYPERSCAN_SRC}/parser/position_info.h",
    "fdr/util/cpuid_inline.h": f"{HYPERSCAN_SRC}/util/cpuid_inline.h",
    "fdr/util/scatter.h": f"{HYPERSCAN_SRC}/util/scatter.h",
}





def download_all_files():
    """Download all required files from Hyperscan repository."""
    print("=" * 70)
    print("FDR String Matcher Setup")
    print("=" * 70)
    print(f"\nDownloading {len(FILES_TO_DOWNLOAD)} files from Hyperscan repository...")
    print()
    
    success_count = 0
    failed_files = []
    total_files = len(FILES_TO_DOWNLOAD)
    
    for idx, (dest_path, url) in enumerate(FILES_TO_DOWNLOAD.items(), 1):
        # Show progress
        print(f"[{idx}/{total_files}] {dest_path} ... ", end="", flush=True)
        
        dest_file = Path(dest_path)
        dest_file.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            urllib.request.urlretrieve(url, dest_file)
            print("OK")
            success_count += 1
        except Exception as e:
            print(f"FAILED ({e})")
            failed_files.append(dest_path)
    
    print()
    print(f"Downloaded: {success_count}/{total_files} files")
    
    if failed_files:
        print(f"\nFailed to download {len(failed_files)} files:")
        for f in failed_files:
            print(f"  - {f}")
        return False
    
    return True


def build_project():
    """Build the FDR project using CMake."""
    print("\n" + "=" * 70)
    print("Building FDR String Matcher")
    print("=" * 70)
    
    fdr_dir = Path("fdr")
    build_dir = fdr_dir / "build"
    
    # Clean build directory if it exists
    if build_dir.exists():
        print(f"\nCleaning existing build directory...")
        import shutil
        shutil.rmtree(build_dir)
    
    # Configure with CMake
    print(f"\nConfiguring CMake...")
    result = subprocess.run(
        ["cmake", "-B", "build", "-S", "."],
        cwd=fdr_dir,
        capture_output=True,
        text=True
    )
    
    if result.returncode != 0:
        print("FAILED - CMake configuration failed!")
        print(result.stderr)
        return False
    
    print("OK - CMake configuration successful")
    
    # Build
    print(f"\nBuilding...")
    result = subprocess.run(
        ["cmake", "--build", "build"],
        cwd=fdr_dir,
        capture_output=True,
        text=True
    )
    
    if result.returncode != 0:
        print("FAILED - Build failed!")
        print(result.stderr)
        return False
    
    print("OK - Build successful")
    
    return True


def run_example():
    """Run the FDR example executable."""
    print("\n" + "=" * 70)
    print("Running FDR Example")
    print("=" * 70)
    print()
    
    fdr_dir = Path("fdr")
    
    # Determine executable path (Windows vs Unix)
    if sys.platform == "win32":
        exe_path = fdr_dir / "build" / "Debug" / "fdr_example.exe"
    else:
        exe_path = fdr_dir / "build" / "fdr_example"
    
    if not exe_path.exists():
        print(f"FAILED - Executable not found at: {exe_path}")
        return False
    
    result = subprocess.run([str(exe_path)], capture_output=False)
    
    return result.returncode == 0


def main():
    """Main setup process."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Setup and build FDR string matcher")
    parser.add_argument("--clean", action="store_true", help="Clean and rebuild")
    parser.add_argument("--no-build", action="store_true", help="Download files only, don't build")
    parser.add_argument("--no-run", action="store_true", help="Don't run the example after building")
    args = parser.parse_args()
    
    # Change to script directory
    os.chdir(Path(__file__).parent)
    
    # Clean if requested
    if args.clean:
        print("=" * 70)
        print("Cleaning Previous Build and Downloads")
        print("=" * 70)
        print()
        
        import shutil
        
        # Clean build directory
        build_dir = Path("fdr/build")
        if build_dir.exists():
            print("Removing build directory...", end=" ", flush=True)
            shutil.rmtree(build_dir)
            print("OK")
        else:
            print("No build directory to clean")
        
        # Clean downloaded files
        fdr_dir = Path("fdr")
        if fdr_dir.exists():
            print("Removing downloaded files...", end=" ", flush=True)
            # Remove all files except our custom ones
            custom_files = {
                "CMakeLists.txt", 
                "example.cpp"
            }
            custom_subdir_files = set()  # No custom subdirectory files
            removed_count = 0
            
            # Count all files first (for accurate reporting)
            def count_files(path):
                count = 0
                for item in path.iterdir():
                    if item.is_file():
                        count += 1
                    elif item.is_dir():
                        count += count_files(item)
                return count
            
            def should_preserve(file_path: Path) -> bool:
                """Check if a file should be preserved during clean."""
                rel_path = file_path.relative_to(fdr_dir)
                # Check root level custom files
                if file_path.parent == fdr_dir and file_path.name in custom_files:
                    return True
                # Check subdirectory custom files
                if str(rel_path).replace('\\', '/') in custom_subdir_files:
                    return True
                return False
            
            # Remove files and directories
            for item in fdr_dir.iterdir():
                if item.is_file() and not should_preserve(item):
                    item.unlink()
                    removed_count += 1
                elif item.is_dir():
                    # For directories, selectively remove files
                    preserved = False
                    for root, dirs, files in os.walk(item, topdown=False):
                        root_path = Path(root)
                        for file in files:
                            file_path = root_path / file
                            if should_preserve(file_path):
                                preserved = True
                            else:
                                file_path.unlink()
                                removed_count += 1
                        # Remove empty directories
                        for dir_name in dirs:
                            dir_path = root_path / dir_name
                            if dir_path.exists() and not any(dir_path.iterdir()):
                                dir_path.rmdir()
                    
                    # Remove top-level directory if empty
                    if not preserved and item.exists() and not any(item.iterdir()):
                        item.rmdir()
            
            if removed_count > 0:
                print(f"OK (removed {removed_count} files)")
            else:
                print("OK (no files to remove)")
        else:
            print("No downloaded files to clean")
        
        print("\nClean completed successfully!")
        return 0
    
    # Download files
    if not download_all_files():
        print("\nFAILED - Setup failed: Could not download all files")
        return 1
    
    print("\nSUCCESS - All files downloaded successfully!")
    
    if args.no_build:
        print("\nSkipping build (--no-build specified)")
        return 0
    
    # Build project
    if not build_project():
        print("\nFAILED - Build failed!")
        return 1
    
    print("\nSUCCESS - Build completed successfully!")
    
    if args.no_run:
        print("\nSkipping example run (--no-run specified)")
        return 0
    
    # Run example
    if not run_example():
        print("\nFAILED - Example run failed!")
        return 1
    
    print("\n" + "=" * 70)
    print("SUCCESS - Setup completed successfully!")
    print("=" * 70)
    print(f"\nTo rebuild: cd fdr && cmake --build build")
    print(f"To run example: .{os.sep}fdr{os.sep}build{os.sep}Debug{os.sep}fdr_example.exe")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
