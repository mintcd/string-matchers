#!/usr/bin/env python3
"""
String Matchers Setup Script

This script automatically downloads all necessary files and builds the matchers.

Usage:
    python config.py                    # Download and build all matchers
    python config.py --no-build         # Download only
    python config.py --rulesets         # Also download rulesets
    python config.py --extract-patterns # Extract patterns from rulesets
    python config.py --clean            # Clean all downloads and builds
"""

import os
import sys
import shutil
from pathlib import Path

# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent / "scripts"))
sys.path.insert(0, str(Path(__file__).parent / "scripts" / "downloads"))

from downloads.fdr_download import download_fdr
from downloads.dfc_download import download_dfc
from downloads.ac_download import download_ac
from downloads.main import download_rulesets, extract_patterns
from build import build_matcher, run_example


def clean_all():
    """Clean all downloaded files and builds."""
    print("=" * 70)
    print("Cleaning All Downloads and Builds")
    print("=" * 70)
    print()
    
    dirs_to_clean = ["fdr", "dfc", "ac", "rulesets"]
    
    for dir_name in dirs_to_clean:
        dir_path = Path(dir_name)
        if dir_path.exists():
            print(f"Removing {dir_name}/ ...", end=" ", flush=True)
            shutil.rmtree(dir_path)
            print("OK")
        else:
            print(f"No {dir_name}/ directory")
    
    # Remove patterns file
    patterns_file = Path("patterns.txt")
    if patterns_file.exists():
        print("Removing patterns.txt ...", end=" ", flush=True)
        patterns_file.unlink()
        print("OK")
    
    print("\nClean completed successfully!")


def main():
    """Main setup process."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Setup and build string matchers")
    parser.add_argument("--clean", action="store_true", help="Clean all downloads and builds")
    parser.add_argument("--no-build", action="store_true", help="Download files only, don't build")
    parser.add_argument("--no-run", action="store_true", help="Don't run the example after building")
    parser.add_argument("--rulesets", action="store_true", help="Download Snort rulesets (ET-Open and Talos)")
    parser.add_argument("--extract-patterns", action="store_true", help="Extract patterns from rulesets")
    parser.add_argument("--max-patterns", type=int, help="Maximum number of patterns to extract")
    args = parser.parse_args()
    
    # Change to script directory
    os.chdir(Path(__file__).parent)
    
    # Clean if requested
    if args.clean:
        clean_all()
        return 0
    
    # Download FDR files
    if not download_fdr():
        print("\nFAILED - Could not download FDR files")
        return 1
    
    print("\nSUCCESS - FDR files downloaded!")
    
    # Download DFC files
    if not download_dfc():
        print("\nWARNING - Could not download all DFC files")
    else:
        print("\nSUCCESS - DFC files downloaded!")
    
    # Download AC files
    if not download_ac():
        print("\nWARNING - Could not download all AC files")
    else:
        print("\nSUCCESS - AC files downloaded!")
    
    # Download rulesets if requested
    if args.rulesets:
        download_rulesets()
    
    # Extract patterns if requested
    if args.extract_patterns:
        extract_patterns(max_patterns=args.max_patterns)
    
    if args.no_build:
        print("\nSkipping build (--no-build specified)")
        return 0
    
    # Build all matchers
    matchers_to_build = ["fdr", "dfc", "ac"]
    build_results = {}
    
    for matcher in matchers_to_build:
        if not build_matcher(matcher):
            print(f"\nWARNING - {matcher.upper()} build failed!")
            build_results[matcher] = False
        else:
            print(f"\nSUCCESS - {matcher.upper()} build completed!")
            build_results[matcher] = True
            
            if not args.no_run and matcher == "fdr":
                # Run FDR example as primary test
                if not run_example(matcher):
                    print(f"\nWARNING - {matcher.upper()} example run failed!")
    
    print("\n" + "=" * 70)
    print("SUCCESS - Setup completed!")
    print("=" * 70)
    print(f"\nDownloaded:")
    print(f"  - FDR matcher")
    print(f"  - DFC matcher")
    print(f"  - AC matcher")
    print(f"\nBuilt:")
    for matcher, success in build_results.items():
        status = "[OK]" if success else "[FAIL]"
        print(f"  {status} {matcher.upper()} matcher")
    if args.rulesets:
        print(f"\nRulesets:")
        print(f"  - Snort rulesets downloaded")
    if args.extract_patterns:
        print(f"\nPatterns:")
        print(f"  - Patterns extracted")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
