# First build

cmake .. -DCMAKE_BUILD_TYPE=Debug

# After modification
// cmake --build . --config Debug --target fdr_main
// & "D:\Projects\string-matchers\src\fdr-minified\build\Debug\fdr_main.exe" --patterns "D:\Projects\string-matchers\dataset\100_short_patterns.txt" --rulesets "D:\Projects\string-matchers\dataset\rulesets.txt" --out "D:\Projects\string-matchers\output\fdr_minified_100_short_patterns"

// python D:\Projects\string-matchers\scripts\compare_results.py "D:\Projects\string-matchers\output\fdr_100_short_patterns\results.txt" "D:\Projects\string-matchers\output\fdr_minified_100_short_patterns\results.txt"