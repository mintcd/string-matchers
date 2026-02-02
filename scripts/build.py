"""Build utilities for string matchers."""

import subprocess
import sys
import os
from pathlib import Path
from typing import Literal


def build_matcher(project_dir:Literal['fdr', 'ac', 'dfc']="fdr"):
    """Build a project using CMake."""
    print("\n" + "=" * 70)
    print(f"Building {project_dir.upper()} String Matcher")
    print("=" * 70)
    
    repo_root = Path(__file__).resolve().parent.parent
    project_path = repo_root / "src" / project_dir
    build_dir = project_path / "build"
    
    # Clean build directory if it exists
    if build_dir.exists():
        print(f"\nCleaning existing build directory...")
        import shutil
        shutil.rmtree(build_dir)
    
    # Configure with CMake
    print(f"\nConfiguring CMake...")
    result = subprocess.run(
        ["cmake", "-B", "build", "-S", "."],
        cwd=project_path,
        capture_output=True,
        text=True
    )
    
    if result.returncode != 0:
        print("FAILED - CMake configuration failed!")
        print(result.stderr)
        return False
    
    print("CMake configuration successful")
    
    # Build
    print(f"\nBuilding...")
    result = subprocess.run(
        ["cmake", "--build", "build"],
        cwd=project_path,
        capture_output=True,
        text=True
    )
    
    if result.returncode != 0:
        print("FAILED - Build failed!")
        print(result.stderr)
        return False
    
    print("Build successful")
    # After successful build, try to locate the built executable and print its path.
    exe_name = f"{project_dir}.exe" if sys.platform == "win32" else project_dir
    found_paths = []
    if build_dir.exists():
        for p in build_dir.rglob("*"):
            if p.is_file():
                if sys.platform == "win32":
                    if p.name.lower() == exe_name.lower():
                        found_paths.append(p.resolve())
                else:
                    if p.name == exe_name:
                        found_paths.append(p.resolve())

    if found_paths:
        print("\nBuilt executable(s):")
        for p in found_paths:
            print(p)
    else:
        print(f"\nBuilt executable not found automatically. Expected name: {exe_name}")
        print(f"Search root: {build_dir.resolve()}")
    
    return True


    
    

def run_example(project_dir="fdr"):
    """Run the example executable from a project."""
    print("\n" + "=" * 70)
    print(f"Running {project_dir.upper()} Example")
    print("=" * 70)
    print()
    
    repo_root = Path(__file__).resolve().parent.parent
    project_path = repo_root / "src" / project_dir
    
    # Determine executable path (Windows vs Unix)
    if sys.platform == "win32":
        exe_path = project_path / "build" / "Debug" / f"{project_dir}_example.exe"
        if not exe_path.exists():
            exe_path = project_path / "build" / "Release" / f"{project_dir}_example.exe"
    else:
        exe_path = project_path / "build" / f"{project_dir}_example"
    
    if not exe_path.exists():
        print(f"FAILED - Executable not found at: {exe_path}")
        return False
    
    result = subprocess.run([str(exe_path)], capture_output=False)
    
    if result.returncode == 0:
        print("\nExample completed successfully!")
        return True
    else:
        print(f"\nExample failed with exit code: {result.returncode}")
        return False


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Build string matchers")
    parser.add_argument("--matcher", choices=["fdr", "dfc", "ac", "all"],
                       default="all", help="Which matcher to build")
    parser.add_argument("--test", action="store_true",
                       help="Run example after building")
    
    args = parser.parse_args()
    
    matchers = ["fdr", "dfc", "ac"] if args.matcher == "all" else [args.matcher]
    
    for matcher in matchers:
        # Build the matcher
        success = build_matcher(matcher)
        
        if not success:
            print(f"\nBuild failed for {matcher}")
            continue
        
        # Run example if requested
        if args.test:
            run_example(matcher)
