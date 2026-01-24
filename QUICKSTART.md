# Quick Start Guide

## Setup in 30 Seconds

```bash
# 1. Run the setup script
python config.py

# That's it! The script will:
# - Download all necessary files from Hyperscan
# - Build the FDR library
# - Run the example
```

## What Gets Downloaded

The script downloads **83 files** from the Intel Hyperscan GitHub repository:
- 13 source files (.c/.cpp)
- 70+ header files (.h)
- Total: ~15,000 lines of code

## Options

```bash
# Download and build, but don't run example
python config.py --no-run

# Only download files, skip building
python config.py --no-build

# Clean and rebuild everything
python config.py --clean
```

## Manual Build

After downloading with `--no-build`:

```bash
cd fdr
cmake -B build -S .
cmake --build build
```

## Run the Example

```bash
# Windows
.\fdr\build\Debug\fdr_example.exe

# Linux/Mac
./fdr/build/fdr_example
```

## What the Example Shows

The example demonstrates:
- Pattern definition using the `hwlmLiteral` structure
- Overview of FDR compilation process
- What would be needed for full pattern matching

**Sample output:**
```
=== FDR String Matcher Example ===

Patterns to search for:
  [0] "hello"
  [1] "world"
  [2] "test"

Compiling FDR engine...
  Note: Full compilation requires Hyperscan infrastructure...
```

## Troubleshooting

**Python not found:**
- Install Python 3.6+ from python.org
- Make sure it's in your PATH

**CMake not found:**
- Windows: `choco install cmake`
- Linux: `sudo apt-get install cmake`
- Mac: `brew install cmake`

**Boost not found:**
- The script only needs Boost headers
- Windows: `choco install boost-msvc-14.3`
- Linux: `sudo apt-get install libboost-all-dev`
- Mac: `brew install boost`

**Download fails:**
- Check internet connection
- Verify GitHub is accessible
- Try again - network issues are transient

## File Structure After Setup

```
string-matchers/
├── config.py                    # Setup script
├── README.md                    # Full documentation
├── QUICKSTART.md               # This file
└── fdr/
    ├── CMakeLists.txt          # Build config (kept in repo)
    ├── config.h                # Platform config (kept in repo)
    ├── example.cpp             # Example code (kept in repo)
    ├── fdr.c                   # Downloaded from Hyperscan
    ├── fdr_compile.cpp         # Downloaded from Hyperscan
    ├── teddy.c                 # Downloaded from Hyperscan
    ├── [80 more files...]      # Downloaded from Hyperscan
    └── build/                  # Build artifacts
        └── Debug/
            ├── fdr_matcher.lib # Compiled library
            └── fdr_example.exe # Example executable
```

## Next Steps

1. **Study the code** - Browse the downloaded files
2. **Read the algorithms** - Check `fdr.c` for the main scanning logic
3. **Explore SIMD** - Look at `teddy.c` for SIMD optimizations
4. **Understand compilation** - Read `fdr_compile.cpp` for pattern compilation

## Quick Reference

| Command                             | Description                         |
| ----------------------------------- | ----------------------------------- |
| `python config.py`                  | Full setup (download + build + run) |
| `python config.py --no-run`         | Setup without running example       |
| `python config.py --no-build`       | Download files only                 |
| `python config.py --clean`          | Clean and rebuild                   |
| `cd fdr && cmake --build build`     | Rebuild manually                    |
| `.\fdr\build\Debug\fdr_example.exe` | Run example (Windows)               |

## Need Help?

- Check the full [README.md](README.md) for detailed information
- Review error messages - they usually indicate what's missing
- Ensure all prerequisites (Python, CMake, Compiler, Boost) are installed
- Try `python config.py --clean` to start fresh

---

**Ready to start?** Just run: `python config.py`
