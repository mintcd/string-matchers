# String Matchers - Isolated Study Repository

This repository contains isolated extractions of string matching engines for study and experimentation. Each matcher is extracted from its original source and configured to build and run independently.

## Available Matchers

### FDR (Fast Dictionary-based Regular expression)
Extracted from Intel Hyperscan - A high-performance SIMD-accelerated literal string matching engine.

**Source:** [Intel Hyperscan](https://github.com/intel/hyperscan)

### DFC (Direct Filter Classification)
Extracted from Snort3 - Optimized multi-pattern matching algorithm used in intrusion detection.

**Source:** [Snort3](https://github.com/snort3/snort3)

### Aho-Corasick (AC)
Extracted from Snort3 - Classic multi-pattern matching algorithm with BNFA variant.

**Source:** [Snort3](https://github.com/snort3/snort3)

## Prerequisites
- Python 3.6+
- CMake 3.10+
- C/C++ compiler (MSVC on Windows, GCC/Clang on Linux)
- Boost (headers only)

Check out `scripts/main.ipynb` to reproduce the results.