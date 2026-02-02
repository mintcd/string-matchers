"""Run and benchmark string matchers."""

import sys
import subprocess
from pathlib import Path


def run_matcher(matcher_name, patterns_file="patterns.txt", rulesets_dir=None, max_patterns=None):
    """Run a specific matcher with given patterns.
    
    Args:
        matcher_name: Name of the matcher (fdr, dfc, ac)
        patterns_file: Path to patterns file
        rulesets_dir: Directory containing rulesets to scan
        max_patterns: Maximum number of patterns to load
    """
    print(f"\n{'=' * 70}")
    print(f"Running {matcher_name.upper()} Matcher")
    print(f"{'=' * 70}\n")
    
    matcher_dir = Path("src") / matcher_name
    
    # Determine executable path (Windows vs Unix)
    if sys.platform == "win32":
        exe_path = matcher_dir / "build" / "Debug" / f"{matcher_name}_main.exe"
        if not exe_path.exists():
            exe_path = matcher_dir / "build" / "Release" / f"{matcher_name}_main.exe"
    else:
        exe_path = matcher_dir / "build" / f"{matcher_name}_main"
    
    if not exe_path.exists():
        print(f"ERROR: Executable not found at: {exe_path}")
        print(f"Please build {matcher_name} first with: python scripts/build.py --matcher {matcher_name}")
        return False
    
    # Build command
    cmd = [str(exe_path)]
    
    if patterns_file:
        cmd.extend(["--patterns", patterns_file])
    if rulesets_dir:
        cmd.extend(["--rulesets", rulesets_dir])
    if max_patterns:
        cmd.extend(["--max-patterns", str(max_patterns)])
    
    result = subprocess.run(cmd, capture_output=False)
    return result.returncode == 0


def run_matcher_example(matcher_name):
    """Run the example executable for a matcher."""
    print(f"\n{'=' * 70}")
    print(f"Running {matcher_name.upper()} Example")
    print(f"{'=' * 70}\n")
    
    matcher_dir = Path("src") / matcher_name
    
    # Determine executable path (Windows vs Unix)
    if sys.platform == "win32":
        exe_path = matcher_dir / "build" / "Debug" / f"{matcher_name}_example.exe"
        if not exe_path.exists():
            exe_path = matcher_dir / "build" / "Release" / f"{matcher_name}_example.exe"
    else:
        exe_path = matcher_dir / "build" / f"{matcher_name}_example"
    
    if not exe_path.exists():
        print(f"ERROR: Executable not found at: {exe_path}")
        return False
    
    result = subprocess.run([str(exe_path)], capture_output=False)
    return result.returncode == 0


def benchmark_all(patterns_file="patterns.txt", rulesets_dir=None, max_patterns=None):
    """Benchmark all available matchers."""
    print(f"\n{'=' * 70}")
    print("Benchmarking All String Matchers")
    print(f"{'=' * 70}\n")
    
    matchers = ["fdr", "dfc", "ac"]
    results = {}
    
    for matcher in matchers:
        if (Path("src") / matcher / "build").exists():
            print(f"\nTesting {matcher.upper()}...")
            success = run_matcher(matcher, patterns_file, rulesets_dir, max_patterns)
            results[matcher] = success
        else:
            print(f"\n{matcher.upper()} not built - skipping")
            results[matcher] = None
    
    # Summary
    print(f"\n{'=' * 70}")
    print("Benchmark Summary")
    print(f"{'=' * 70}\n")
    
    for matcher, success in results.items():
        if success is None:
            status = "NOT BUILT"
        elif success:
            status = "PASSED"
        else:
            status = "FAILED"
        print(f"  {matcher.upper():<10} : {status}")
    
    return results


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Run and benchmark string matchers")
    parser.add_argument("--matcher", choices=["fdr", "dfc", "ac", "all"], 
                       default="fdr", help="Which matcher to run (default: fdr)")
    parser.add_argument("--patterns", default="dataset/patterns.txt", 
                       help="Patterns file to use (default: dataset/patterns.txt)")
    parser.add_argument("--rulesets", default="dataset/rulesets/et-open",
                       help="Rulesets directory to scan (default: dataset/rulesets/et-open)")
    parser.add_argument("--max-patterns", type=int, default=100,
                       help="Maximum number of patterns to load (default: 100)")
    parser.add_argument("--example", action="store_true",
                       help="Run example instead of main application")
    
    args = parser.parse_args()
    
    # Convert relative paths to absolute paths
    from pathlib import Path
    patterns_path = str(Path(args.patterns).resolve())
    rulesets_path = str(Path(args.rulesets).resolve())
    
    if args.example:
        if args.matcher == "all":
            for matcher in ["fdr", "dfc", "ac"]:
                run_matcher_example(matcher)
        else:
            run_matcher_example(args.matcher)
    elif args.matcher == "all":
        benchmark_all(patterns_path, rulesets_path, args.max_patterns)
    else:
        run_matcher(args.matcher, patterns_path, rulesets_path, args.max_patterns)
