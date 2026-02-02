"""Download Snort rulesets and extract patterns."""

import urllib.request
import tarfile
import re
from pathlib import Path


# Snort Rulesets URLs
ET_OPEN_URL = "https://rules.emergingthreats.net/open/snort-2.9.0/emerging.rules.tar.gz"
TALOS_COMMUNITY_URL = "https://www.snort.org/downloads/community/snort3-community-rules.tar.gz"


def download_raw(base_dir="../../dataset"):
    """Download and extract Snort rulesets for testing.
    
    Args:
        base_dir: Base directory for datasets (default: ../../dataset relative to this script,
                  which resolves to string-matchers/dataset)
    """
    print("\n" + "=" * 70)
    print("Downloading Snort Rulesets for Testing")
    print("=" * 70)
    print()
    
    # Get absolute path relative to this script file
    script_dir = Path(__file__).parent
    base_path = (script_dir / base_dir).resolve()
    base_path.mkdir(parents=True, exist_ok=True)
    
    rulesets_dir = base_path / "rulesets"
    rulesets_dir.mkdir(exist_ok=True)
    
    # Download ET-Open ruleset
    print("[1/2] ET-Open ruleset ... ", end="", flush=True)
    et_file = rulesets_dir / "et-open.tar.gz"
    try:
        urllib.request.urlretrieve(ET_OPEN_URL, et_file)
        print("OK")
        
        # Extract
        print("      Extracting ... ", end="", flush=True)
        with tarfile.open(et_file, 'r:gz') as tar:
            tar.extractall(rulesets_dir / "et-open")
        print("OK")
        et_file.unlink()  # Remove archive
    except Exception as e:
        print(f"FAILED ({e})")
    
    # Download Talos Community ruleset
    print("[2/2] Talos Community ruleset ... ", end="", flush=True)
    talos_file = rulesets_dir / "talos.tar.gz"
    try:
        urllib.request.urlretrieve(TALOS_COMMUNITY_URL, talos_file)
        print("OK")
        
        # Extract
        print("      Extracting ... ", end="", flush=True)
        with tarfile.open(talos_file, 'r:gz') as tar:
            tar.extractall(rulesets_dir / "talos")
        print("OK")
        talos_file.unlink()  # Remove archive
    except Exception as e:
        print(f"FAILED ({e})")
    
    print(f"\nRulesets downloaded to: {rulesets_dir}/")
    return True


def extract(base_dir="../../dataset", output_file="patterns.txt", max_patterns=None):
    """Extract string patterns from Snort rules for testing.
    
    Args:
        base_dir: Base directory for datasets (default: ../../dataset relative to this script)
        output_file: Output filename for patterns (will be saved in base_dir)
        max_patterns: Maximum number of patterns to extract (None for all)
    """
    print("\n" + "=" * 70)
    print("Extracting Patterns from Rules")
    print("=" * 70)
    print()
    
    # Get absolute path relative to this script file
    script_dir = Path(__file__).parent
    base_path = (script_dir / base_dir).resolve()
    
    rulesets_dir = base_path / "rulesets"
    
    if not rulesets_dir.exists():
        print("ERROR: Rulesets directory not found. Run with rulesets download first.")
        return False
    
    patterns = set()
    
    # Pattern to match content fields in Snort rules
    # Example: content:"GET "; content:"|28 29|"; 
    content_pattern = re.compile(r'content\s*:\s*"([^"]+)"')
    
    # Find all .rules files
    rules_files = list(rulesets_dir.rglob("*.rules"))
    print(f"Found {len(rules_files)} rule files")
    
    for rules_file in rules_files:
        try:
            with open(rules_file, 'r', encoding='utf-8', errors='ignore') as f:
                for line in f:
                    # Find all content matches in the line
                    matches = content_pattern.findall(line)
                    for match in matches:
                        # Skip patterns with hex content (|XX|) for simplicity
                        if '|' not in match and len(match) > 2:
                            # Trim leading/trailing whitespace from extracted patterns
                            patterns.add(match.strip())
        except Exception as e:
            print(f"Warning: Could not read {rules_file}: {e}")
    
    # Write patterns to file
    output_path = base_path / output_file
    with open(output_path, 'w', encoding='utf-8') as f:
        pattern_list = sorted(patterns)
        if max_patterns:
            pattern_list = pattern_list[:max_patterns]
        for pattern in pattern_list:
            f.write(f"{pattern}\n")
    
    print(f"\nExtracted {len(pattern_list)} unique patterns")
    print(f"Patterns saved to: {output_path}")
    
    # Print some statistics
    lengths = [len(p) for p in pattern_list]
    if lengths:
        print(f"Pattern length: min={min(lengths)}, max={max(lengths)}, avg={sum(lengths)//len(lengths)}")
    
    # Filter and save short patterns (<=8 bytes for FDR)
    # Ensure short patterns are trimmed as well
    short_patterns = [p for p in sorted(patterns) if len(p.strip()) <= 8]
    short_output_path = base_path / "short_patterns.txt"
    with open(short_output_path, 'w', encoding='utf-8') as f:
        for pattern in short_patterns:
            f.write(f"{pattern}\n")
    
    print(f"\nFiltered {len(short_patterns)} patterns (<=8 bytes)")
    print(f"Short patterns saved to: {short_output_path}")
    if short_patterns:
        short_lengths = [len(p) for p in short_patterns]
        print(f"Short pattern length: min={min(short_lengths)}, max={max(short_lengths)}, avg={sum(short_lengths)//len(short_lengths)}")
    
    # Combine all rulesets into a single file (no comments)
    rulesets_output_path = base_path / "rulesets.txt"
    rule_lines = 0
    rule_bytes = 0
    with open(rulesets_output_path, 'w', encoding='utf-8', errors='ignore') as out_f:
        for rules_file in rules_files:
            try:
                with open(rules_file, 'r', encoding='utf-8', errors='ignore') as in_f:
                    for line in in_f:
                        # Keep only non-comment lines and non-empty lines
                        stripped = line.strip()
                        if stripped and not stripped.startswith('#'):
                            out_f.write(line)
                            rule_lines += 1
                            rule_bytes += len(line)
            except Exception as e:
                print(f"Warning: Could not read {rules_file}: {e}")
    
    print(f"\nCombined rulesets (no comments) into: {rulesets_output_path}")
    print(f"Rule lines: {rule_lines}, Size: {rule_bytes / (1024*1024):.2f} MB")
    
    return True

def download_dataset(base_dir="../../dataset"): 
    download_raw(base_dir)
    extract(base_dir)