"""Aho-Corasick downloader from Snort3."""

import urllib.request
from pathlib import Path

# Snort3 GitHub repository configuration
SNORT3_REPO = "https://raw.githubusercontent.com/snort3/snort3/master"
SNORT3_SRC = f"{SNORT3_REPO}/src/search_engines"

# Aho-Corasick files to download
AC_FILES = {
    "src/ac/ac_full.cc": f"{SNORT3_SRC}/ac_full.cc",
    "src/ac/ac_bnfa.cc": f"{SNORT3_SRC}/ac_bnfa.cc",
    "src/ac/bnfa_search.h": f"{SNORT3_SRC}/bnfa_search.h",
    "src/ac/bnfa_search.cc": f"{SNORT3_SRC}/bnfa_search.cc",
    "src/ac/search_tool.h": f"{SNORT3_SRC}/search_tool.h",
    "src/ac/search_tool.cc": f"{SNORT3_SRC}/search_tool.cc",
    "src/ac/search_common.h": f"{SNORT3_SRC}/search_common.h",
    "src/ac/pat_stats.h": f"{SNORT3_SRC}/pat_stats.h",
}


def download_ac(base_dir=None):
    """Download Aho-Corasick files from Snort3 repository."""
    print("\n" + "=" * 70)
    print("Aho-Corasick (ac_full + BNFA) - from Snort3")
    print("=" * 70)
    print(f"\nDownloading {len(AC_FILES)} files...")
    print()
    # Resolve base path: default to repository root when no base_dir provided
    script_dir = Path(__file__).resolve().parent
    repo_root = script_dir.parent.parent
    if base_dir:
        base_path = Path(base_dir)
        if not base_path.is_absolute():
            base_path = (repo_root / base_path).resolve()
    else:
        base_path = repo_root
    success_count = 0
    failed_files = []
    total_files = len(AC_FILES)
    
    for idx, (dest_path, url) in enumerate(AC_FILES.items(), 1):
        print(f"[{idx}/{total_files}] {dest_path} ... ", end="", flush=True)
        
        dest_file = base_path / dest_path
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
