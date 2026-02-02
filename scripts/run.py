"""Run matchers."""

import sys
import subprocess
from pathlib import Path
from typing import Literal, Optional


def run_matcher(matcher_name: Literal["fdr", "dfc", "ac"], 
                patterns_file, 
                rulesets_file, 
                max_patterns,
                output_dir: Optional[str] = None):
    """Run a specific matcher with given patterns.
    
    Args:
        matcher_name: Name of the matcher (fdr, dfc, ac)
        patterns_file: Path to patterns file
        rulesets_file: Path to rulesets file
        max_patterns: Maximum number of patterns to load
    """
    print(f"\n{'=' * 70}")
    print(f"Running {matcher_name.upper()} Matcher")
    print(f"{'=' * 70}\n")
    
    repo_root = Path(__file__).resolve().parent.parent
    matcher_dir = repo_root / "src" / matcher_name

    # Prefer an executable placed directly inside the matcher folder
    # e.g. src/fdr/fdr.exe or src/fdr/fdr
    if sys.platform == "win32":
        exe_path = matcher_dir / "build" / "Debug" / f"{matcher_name}.exe"
        if not exe_path.exists():
            print("Not found", exe_path)
            exe_path = matcher_dir / "build" / "Release" / f"{matcher_name}.exe"
    else:
        exe_path = matcher_dir / matcher_name
        if not exe_path.exists():
            exe_path = matcher_dir / "build" / f"{matcher_name}_main"
    
    if not exe_path.exists():
        print(f"ERROR: Executable not found: {exe_path}")
        return False
    
    print(f"Executing {exe_path}")
    
    # Build command
    cmd = [str(exe_path)]
    
    if patterns_file:
        cmd.extend(["--patterns", patterns_file])
    if rulesets_file:
        cmd.extend(["--rulesets", rulesets_file])
    if max_patterns:
        cmd.extend(["--max-patterns", str(max_patterns)])
    if output_dir:
        cmd.extend(["--out", output_dir])
    result = subprocess.run(cmd, capture_output=True, text=True, cwd=repo_root)

    if result.stdout:
        print(result.stdout)
    if result.returncode != 0 and result.stderr:
        print(result.stderr)

    return result.returncode == 0
