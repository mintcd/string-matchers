# String Matchers - Isolated Study Repository

This repository contains isolated extractions of string matching engines for study and experimentation. Each matcher is extracted from its original source and configured to build and run independently.

## Available Matchers

### FDR (Fast Dictionary-based Regular expression)
Extracted from Intel Hyperscan - A high-performance SIMD-accelerated literal string matching engine.

**Source:** [Intel Hyperscan](https://github.com/intel/hyperscan)

## Quick Start

### Prerequisites
- Python 3.6+
- CMake 3.10+
- C/C++ compiler (MSVC on Windows, GCC/Clang on Linux)
- Boost (headers only)

### Setup and Run

```bash
# Clone this repository
git clone <your-repo-url>
cd string-matchers

# Run the setup script (downloads files, builds, and runs example)
python config.py

# Or download only without building
python config.py --no-build

# Or build without running the example
python config.py --no-run
```

## What the Setup Script Does

The `config.py` script automatically:

1. **Downloads** all necessary source files from the original Hyperscan GitHub repository
2. **Creates** the proper directory structure
3. **Configures** the build with CMake
4. **Builds** the FDR library and example
5. **Runs** the example to verify everything works

## Directory Structure

```
string-matchers/
├── config.py           # Setup script
├── README.md          # This file
└── fdr/               # FDR matcher directory
    ├── CMakeLists.txt # Build configuration
    ├── config.h       # Platform configuration
    ├── example.cpp    # Example usage
    ├── *.c, *.cpp     # Source files (downloaded)
    ├── *.h            # Header files (downloaded)
    ├── hwlm/          # Hardware Literal Matcher (downloaded)
    ├── rose/          # ROSE engine types (downloaded)
    ├── util/          # Utility functions (downloaded)
    └── build/         # Build artifacts
```

## FDR Matcher Details

The FDR extraction includes:
- **Runtime engine** - Fast scanning implementation with SIMD optimizations
- **Compilation infrastructure** - Pattern compilation and optimization
- **TEDDY engine** - Specialized SIMD matcher for small pattern sets
- **Supporting infrastructure** - ~70 files, 15,000+ lines of code

### Building Manually

If you prefer to build manually after downloading:

```bash
cd fdr
cmake -B build -S .
cmake --build build

# Run the example
./build/Debug/fdr_example.exe  # Windows
./build/fdr_example            # Linux/Mac
```

## Files Included in Repository

The following files are maintained in this repository (not downloaded):

- `config.py` - Automated setup script
- `fdr/CMakeLists.txt` - Build system configuration
- `fdr/config.h` - Minimal platform detection header
- `fdr/example.cpp` - Demonstration program

All other files are automatically downloaded from the original Hyperscan source.

## Why This Approach?

This repository uses a download-on-setup approach rather than copying all files because:

1. **License compliance** - Keeps original code in its source repository
2. **Up-to-date sources** - Always fetches from the canonical Hyperscan repo
3. **Minimal repo size** - Only custom files are stored
4. **Attribution** - Clear source attribution to original authors
5. **Learning focus** - Emphasizes the extraction and integration process

## What You Can Learn

Studying the FDR extraction provides insights into:
- **SIMD string matching algorithms** - Parallel byte scanning techniques
- **Hash-based pattern matching** - Efficient multi-pattern searching
- **Performance optimization** - CPU intrinsics and cache-friendly designs
- **Compilation strategies** - Pattern analysis and bytecode generation
- **Software architecture** - Modular engine design

## Limitations

The FDR extraction is **functionally complete** but requires significant Hyperscan infrastructure for standalone pattern compilation:
- Pattern analysis and literal grouping
- Bytecode generation framework  
- Scratch space management
- Full compilation context

The extracted code is ideal for:
- ✅ Studying algorithms and data structures
- ✅ Understanding SIMD optimization techniques
- ✅ Learning string matching architectures
- ✅ Examining the FDR implementation

Not suitable for:
- ❌ Production string matching (use full Hyperscan instead)
- ❌ Standalone pattern compilation without additional work

## Contributing

Contributions welcome! Please:
- Keep the setup script up-to-date with Hyperscan changes
- Add more string matchers (Aho-Corasick, etc.)
- Improve documentation and examples
- Report issues with the setup process

## License

The setup infrastructure (config.py, CMakeLists.txt, example.cpp) in this repository is provided as-is for educational purposes.

**Downloaded Hyperscan source files** retain their original BSD 3-Clause license:
- Copyright (c) 2015-2020, Intel Corporation
- See individual file headers for complete license text
- Original source: https://github.com/intel/hyperscan

## References

- [Hyperscan Documentation](http://intel.github.io/hyperscan/)
- [Hyperscan GitHub](https://github.com/intel/hyperscan)
- [FDR Algorithm Paper](https://www.intel.com/content/www/us/en/developer/articles/technical/fast-dictionary-based-string-matching.html)

## Troubleshooting

**CMake not found:**
```bash
# Windows
choco install cmake

# Linux
sudo apt-get install cmake  # Debian/Ubuntu
sudo yum install cmake      # RedHat/CentOS

# Mac
brew install cmake
```

**Boost not found:**
```bash
# Windows
choco install boost-msvc-14.3

# Linux
sudo apt-get install libboost-all-dev  # Debian/Ubuntu

# Mac
brew install boost
```

**Build fails:**
- Ensure you have a C++14 compatible compiler
- Check that all files downloaded successfully
- Try cleaning and rebuilding: `python config.py --clean`

## Support

For issues with:
- **Setup script**: Open an issue in this repository
- **Hyperscan code**: Refer to the [Hyperscan project](https://github.com/intel/hyperscan)
- **Build problems**: Check the troubleshooting section above

---

**Created for educational purposes** - Study, learn, and experiment with string matching algorithms!
