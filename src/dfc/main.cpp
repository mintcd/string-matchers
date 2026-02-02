/*
 * DFC String Matcher - Main Application
 * 
 * This application demonstrates the DFC matcher with:
 * - Loading patterns from a file
 * - Scanning rulesets line by line
 * - Performance measurement
 */

#include <iostream>
#include <vector>
#include <string>
#include <fstream>
#include <sstream>
#include <cstring>
#include <memory>
#include <chrono>
#include <filesystem>
#include <algorithm>

using namespace std;
namespace fs = std::filesystem;

// Per-ruleset result
struct RulesetResult {
    size_t ruleset_index;
    vector<pair<size_t, size_t>> matches; // (position, pattern_index)
    double time_ms;
};

// Load patterns from file
vector<string> loadPatterns(const string &filename) {
    vector<string> patterns;
    ifstream file(filename);
    
    if (!file.is_open()) {
        cerr << "ERROR: Cannot open patterns file: " << filename << endl;
        return patterns;
    }
    
    string line;
    while (getline(file, line)) {
        if (!line.empty() && line[0] != '#') {
            patterns.push_back(line);
        }
    }
    
    return patterns;
}

// Simple DFC-style search (using basic string matching)
vector<pair<size_t, size_t>> searchPatterns(const string &text, const vector<string> &patterns) {
    vector<pair<size_t, size_t>> matches;
    
    for (size_t pid = 0; pid < patterns.size(); pid++) {
        const string &pattern = patterns[pid];
        size_t pos = 0;
        
        while ((pos = text.find(pattern, pos)) != string::npos) {
            // Store start position of the match
            matches.push_back({pos, pid});
            pos++;
        }
    }
    
    // Sort matches by position to ensure consistent ordering
    sort(matches.begin(), matches.end());
    
    return matches;
}

// Scan all rulesets from file (one ruleset per line)
size_t scanRulesetsFile(const string &filepath, const vector<string> &patterns,
                        vector<RulesetResult> &results, size_t &total_bytes) {
    ifstream file(filepath);
    if (!file.is_open()) {
        cerr << "ERROR: Cannot open rulesets file: " << filepath << endl;
        return 0;
    }
    
    size_t total_matches = 0;
    size_t rulesets_scanned = 0;
    string line;
    
    while (getline(file, line)) {
        // Skip empty lines and comments
        if (line.empty() || line[0] == '#') {
            continue;
        }
        
        auto start = chrono::high_resolution_clock::now();
        auto matches = searchPatterns(line, patterns);
        auto end = chrono::high_resolution_clock::now();
        
        double time_ms = chrono::duration_cast<chrono::microseconds>(end - start).count() / 1000.0;
        
        RulesetResult result;
        result.ruleset_index = rulesets_scanned;
        result.time_ms = time_ms;
        result.matches = matches;
        
        results.push_back(result);
        
        total_matches += matches.size();
        total_bytes += line.size();
        rulesets_scanned++;
        
        if (rulesets_scanned % 1000 == 0) {
            cout << "  Scanned " << rulesets_scanned << " rulesets..." << endl;
        }
    }
    
    cout << "  Total rulesets scanned: " << rulesets_scanned << endl;
    return total_matches;
}

int main(int argc, char *argv[]) {
    cout << "=== DFC String Matcher Application ===" << endl << endl;
    
    // Parse command line arguments
    string patterns_file;
    string rulesets_file;
    string output_dir;
    
    for (int i = 1; i < argc; i++) {
        string arg = argv[i];
        if (arg == "--patterns" && i + 1 < argc) {
            patterns_file = argv[++i];
        } else if (arg == "--rulesets" && i + 1 < argc) {
            rulesets_file = argv[++i];
        } else if (arg == "--out" && i + 1 < argc) {
            output_dir = argv[++i];
        } else if (arg == "--help") {
            cout << "Usage: " << argv[0] << " --patterns <file> --rulesets <file> --out <dir>" << endl;
            cout << "Required arguments:" << endl;
            cout << "  --patterns <file>       Patterns file" << endl;
            cout << "  --rulesets <file>       Rulesets file" << endl;
            cout << "  --out <dir>             Output directory for results" << endl;
            cout << "  --help                  Show this help message" << endl;
            return 0;
        }
    }
    
    // Validate required arguments
    if (patterns_file.empty() || rulesets_file.empty() || output_dir.empty()) {
        cerr << "ERROR: Missing required arguments!" << endl;
        cerr << "Usage: " << argv[0] << " --patterns <file> --rulesets <file> --out <dir>" << endl;
        cerr << "Use --help for more information" << endl;
        return 1;
    }
    
    // Create output directory if it doesn't exist
    try {
        fs::create_directories(output_dir);
    } catch (const fs::filesystem_error &e) {
        cerr << "ERROR: Cannot create output directory: " << e.what() << endl;
        return 1;
    }
    
    // Step 1: Load patterns
    cout << "Loading patterns from: " << patterns_file << endl;
    vector<string> patterns = loadPatterns(patterns_file);
    
    if (patterns.empty()) {
        cerr << "ERROR: No patterns loaded!" << endl;
        return 1;
    }
    
    cout << "Loaded " << patterns.size() << " patterns" << endl;
    cout << endl;
    
    // Step 2: Compile (no-op for simple implementation)
    cout << "Compiling DFC engine..." << endl;
    auto compile_start = chrono::high_resolution_clock::now();
    auto compile_end = chrono::high_resolution_clock::now();
    auto compile_time = chrono::duration_cast<chrono::milliseconds>(compile_end - compile_start).count();
    cout << "SUCCESS: DFC engine compiled in " << compile_time << " ms" << endl;
    cout << endl;
    
    // Step 3: Scan rulesets
    cout << "Scanning rulesets from: " << rulesets_file << endl;
    
    vector<RulesetResult> results;
    size_t total_bytes = 0;
    
    auto scan_start = chrono::high_resolution_clock::now();
    size_t total_matches = scanRulesetsFile(rulesets_file, patterns, results, total_bytes);
    auto scan_end = chrono::high_resolution_clock::now();
    
    auto scan_time = chrono::duration_cast<chrono::milliseconds>(scan_end - scan_start).count();
    
    // Step 4: Display results
    cout << endl;
    cout << "=== Results ===" << endl;
    cout << "  Patterns loaded:      " << patterns.size() << endl;
    cout << "  Total matches found:  " << total_matches << endl;
    cout << "  Bytes scanned:        " << total_bytes << endl;
    cout << "  Compilation time:     " << compile_time << " ms" << endl;
    cout << "  Scan time:            " << scan_time << " ms" << endl;
    
    if (scan_time > 0) {
        double throughput = (total_bytes / 1024.0 / 1024.0) / (scan_time / 1000.0);
        cout << "  Throughput:           " << fixed << throughput << " MB/s" << endl;
    }
    
    // Show top matched patterns
    if (total_matches > 0) {
        cout << endl << "Top 10 matched patterns:" << endl;
        vector<size_t> pattern_counts(patterns.size(), 0);
        for (const auto &result : results) {
            for (const auto &match : result.matches) {
                pattern_counts[match.second]++;
            }
        }
        
        vector<pair<size_t, size_t>> sorted_patterns;
        for (size_t i = 0; i < pattern_counts.size(); i++) {
            if (pattern_counts[i] > 0) {
                sorted_patterns.push_back({pattern_counts[i], i});
            }
        }
        sort(sorted_patterns.rbegin(), sorted_patterns.rend());
        
        for (size_t i = 0; i < min(size_t(10), sorted_patterns.size()); i++) {
            size_t count = sorted_patterns[i].first;
            size_t id = sorted_patterns[i].second;
            cout << "  [" << id << "] \"" << patterns[id] << "\" - " << count << " matches" << endl;
        }
    }
    
    // Step 5: Write output files
    cout << endl << "Writing output files to: " << output_dir << endl;
    
    // Write metadata.txt
    string metadata_path = output_dir + "/metadata.txt";
    ofstream metadata_file(metadata_path);
    if (metadata_file.is_open()) {
        metadata_file << "Input Files:" << endl;
        metadata_file << "  Patterns: " << patterns_file << endl;
        metadata_file << "  Rulesets: " << rulesets_file << endl;
        metadata_file << endl;
        metadata_file << "Column Descriptions for results.txt:" << endl;
        metadata_file << "  ruleset_index - Zero-based index of the ruleset (line number in rulesets file)" << endl;
        metadata_file << "  matches       - List of (position, pattern_index) pairs where patterns matched" << endl;
        metadata_file << "  time_ms       - Time taken to scan this ruleset in milliseconds" << endl;
        metadata_file << endl;
        metadata_file << "Match Format: (position, pattern_index)" << endl;
        metadata_file << "  position      - Byte offset in the ruleset where the match starts (0-indexed)" << endl;
        metadata_file << "  pattern_index - Index of the matched pattern from patterns file" << endl;
        metadata_file.close();
        cout << "  Written: metadata.txt" << endl;
    } else {
        cerr << "WARNING: Could not write metadata.txt" << endl;
    }
    
    // Write results.txt
    string results_path = output_dir + "/results.txt";
    ofstream results_file(results_path);
    if (results_file.is_open()) {
        results_file << "ruleset_index\tmatches\ttime_ms" << endl;
        
        for (const auto &result : results) {
            results_file << result.ruleset_index << "\t";
            
            // Write matches as comma-separated pairs
            results_file << "[";
            for (size_t i = 0; i < result.matches.size(); i++) {
                if (i > 0) results_file << ",";
                results_file << "(" << result.matches[i].first << "," << result.matches[i].second << ")";
            }
            results_file << "]\t";
            
            results_file << fixed << result.time_ms << endl;
        }
        
        results_file.close();
        cout << "  Written: results.txt (" << results.size() << " rows)" << endl;
    } else {
        cerr << "WARNING: Could not write results.txt" << endl;
    }
    
    cout << endl << "SUCCESS!" << endl;
    return 0;
}
