# Contributing to String Matchers

Thank you for your interest in contributing! This repository is designed to make string matching algorithms accessible for study and experimentation.

## What We're Looking For

### New String Matchers
- Aho-Corasick algorithm
- Boyer-Moore variants  
- Wu-Manber algorithm
- Other multi-pattern matching algorithms

### Improvements to Existing Extractors
- Better error handling
- Cross-platform compatibility fixes
- Documentation improvements
- Example enhancements

### Infrastructure
- Better setup scripts
- Testing frameworks
- Performance benchmarks
- Visualization tools

## How to Contribute

### Adding a New String Matcher

1. **Create a new directory** under `string-matchers/`
   ```
   string-matchers/
   ├── fdr/           # Existing
   └── aho-corasick/  # Your new matcher
   ```

2. **Create the core files**
   - `CMakeLists.txt` - Build configuration
   - `example.cpp` - Demonstration program
   - `config.h` - Platform-specific configuration (if needed)

3. **Update `config.py`**
   - Add file download mappings for your matcher
   - Follow the FDR pattern for consistency

4. **Add documentation**
   - Create `matcher/README.md` explaining the algorithm
   - Document the extraction process
   - List all required files and their purpose

5. **Test thoroughly**
   - Test on Windows, Linux, and macOS if possible
   - Verify the setup script works correctly
   - Ensure the example compiles and runs

### Improving Existing Code

1. **Fork the repository**
2. **Create a feature branch**
   ```bash
   git checkout -b feature/better-error-handling
   ```

3. **Make your changes**
   - Keep changes focused and atomic
   - Follow existing code style
   - Add comments where helpful

4. **Test your changes**
   ```bash
   python config.py --clean  # Test full setup
   ```

5. **Submit a pull request**
   - Describe what you changed and why
   - Include test results
   - Reference any related issues

## Code Style

### Python (config.py)
- Follow PEP 8
- Use type hints where helpful
- Add docstrings to functions
- Keep functions focused and small

### C/C++ (examples)
- Follow the existing style in the codebase
- Use clear variable names
- Add comments for complex logic
- Keep examples simple and educational

### CMake
- Use modern CMake (3.10+)
- Make cross-platform compatible
- Document any special requirements

## File Organization

### What Goes in the Repository
- ✅ Setup scripts (`config.py`)
- ✅ Build configuration (`CMakeLists.txt`)
- ✅ Example programs (`example.cpp`)
- ✅ Custom configuration (`config.h` if needed)
- ✅ Documentation (README, guides)

### What Gets Downloaded
- ❌ Source files from original projects
- ❌ Header files from original projects
- ❌ Build artifacts
- ❌ Third-party dependencies

## Testing Checklist

Before submitting a pull request:

- [ ] Code compiles without errors
- [ ] Setup script downloads all required files
- [ ] Example runs and produces expected output
- [ ] Works on at least one platform (specify which)
- [ ] Documentation is updated
- [ ] `.gitignore` excludes downloaded files
- [ ] Commit messages are clear

## Platform Testing

Ideally, test on multiple platforms:

| Platform | Compiler   | Notes                        |
| -------- | ---------- | ---------------------------- |
| Windows  | MSVC 2019+ | Primary development platform |
| Linux    | GCC 7+     | Ubuntu/Debian preferred      |
| macOS    | Clang 10+  | Apple Silicon and Intel      |

If you can only test on one platform, note that in your PR.

## Documentation Standards

### README.md
Each matcher should have:
- Algorithm description
- Performance characteristics
- Build instructions
- Usage examples
- References to papers/documentation

### Code Comments
- Explain **why**, not just **what**
- Document assumptions
- Note any limitations
- Reference algorithms by name

### Example Programs
- Should be self-documenting
- Include expected output
- Demonstrate key features
- Be runnable out of the box

## Licensing

- Keep original license headers on downloaded code
- New code should be compatible with the project license
- Clearly attribute original sources
- Don't remove copyright notices

## Questions?

- Open an issue for discussion
- Check existing issues and PRs
- Ask for help if you're stuck

## Code of Conduct

Be respectful and constructive:
- Welcome newcomers
- Provide helpful feedback
- Focus on the code, not the person
- Celebrate contributions of all sizes

## Recognition

Contributors will be:
- Listed in release notes
- Credited in documentation
- Thanked publicly

## Getting Started

1. Fork the repository
2. Set up your development environment
3. Look for "good first issue" tags
4. Ask questions in issues
5. Start small and iterate

## Example Contribution Workflow

```bash
# Fork and clone
git clone https://github.com/YOUR_USERNAME/string-matchers.git
cd string-matchers

# Create a branch
git checkout -b feature/improve-error-handling

# Make changes
# ... edit files ...

# Test
python config.py --clean

# Commit
git add .
git commit -m "Improve error handling in download_file"

# Push and create PR
git push origin feature/improve-error-handling
# Then create PR on GitHub
```

---

Thank you for contributing to String Matchers! 🎉
