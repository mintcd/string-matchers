# Scripts Directory

Modular Python scripts for managing string matcher downloads, builds, and benchmarks.

## Structure

```
scripts/
├── __init__.py              # Package init
├── build.py                 # Build and compilation utilities
├── run.py                   # Benchmark and execution utilities
└── downloads/               # Download modules
    ├── __init__.py          # Downloads package init
    ├── fdr_download.py      # FDR (Hyperscan) downloader
    ├── dfc_download.py      # DFC (Snort3) downloader
    ├── ac_download.py       # Aho-Corasick (Snort3) downloader
    └── main.py              # Ruleset downloads and pattern extraction
```

## Modules

### downloads/fdr_download.py
Downloads FDR implementation from Intel Hyperscan repository (122 files).

**Functions:**
- `download_fdr(base_dir=".")` - Download all FDR files

### downloads/dfc_download.py
Downloads DFC implementation from Snort3 repository (4 files).

**Functions:**
- `download_dfc(base_dir=".")` - Download all DFC files

### downloads/ac_download.py
Downloads Aho-Corasick implementation from Snort3 repository (8 files).

**Functions:**
- `download_ac(base_dir=".")` - Download all AC files

### downloads/main.py
Downloads Snort rulesets and extracts test patterns.

**Functions:**
- `download_rulesets(base_dir=".")` - Download ET-Open and Talos rulesets
- `extract_patterns(base_dir=".", output_file="patterns.txt", max_patterns=None)` - Extract patterns from rules

### build.py
Build utilities for compiling string matchers.

**Functions:**
- `build_matcher(project_dir="fdr")` - Build a project using CMake
- `run_example(project_dir="fdr")` - Run the example executable

### run.py
Benchmark and execution utilities.

**Functions:**
- `run_matcher(matcher_name, patterns_file, input_file)` - Run a specific matcher
- `benchmark_all(patterns_file, input_file)` - Benchmark all matchers

**CLI Usage:**
```bash
python scripts/run.py --matcher fdr --patterns patterns.txt
python scripts/run.py --matcher all
```

## Usage Examples

### Import individual modules:
```python
from downloads.fdr_download import download_fdr
from downloads.main import download_rulesets, extract_patterns
from build import build_matcher

# Download FDR
download_fdr()

# Download rulesets
download_rulesets()

# Extract patterns
extract_patterns(max_patterns=1000)

# Build
build_matcher("fdr")
```

### Use from command line:
```bash
# Download everything
python config.py --no-build --rulesets --extract-patterns

# Run benchmarks
python scripts/run.py --matcher all --patterns patterns.txt
```

## Benefits of Modular Structure

1. **Separation of concerns** - Each module has a single responsibility
2. **Reusability** - Modules can be imported independently
3. **Maintainability** - Easier to update individual components
4. **Testability** - Each module can be tested independently
5. **Clarity** - Clear organization and purpose for each file
