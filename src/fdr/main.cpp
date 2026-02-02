/*
 * FDR String Matcher - Main Application
 * 
 * This application demonstrates the FDR matcher with:
 * - Loading patterns from a file
 * - Scanning multiple ruleset files
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

#include "fdr/fdr.h"
#include "fdr/fdr_compile.h"
#include "hwlm/hwlm.h"
#include "hwlm/hwlm_literal.h"
#include "hwlm/hwlm_build.h"
#include "ue2common.h"
#include "grey.h"
#include "util/target_info.h"
#include "hs.h"

using namespace std;
using namespace ue2;
namespace fs = std::filesystem;

// Callback structure to collect matches
struct MatchContext {
    vector<pair<u32, u32>> matches; // (pattern_id, end_offset)
    size_t total_bytes_scanned = 0;
};

// Per-ruleset result
struct RulesetResult {
    size_t ruleset_index;
    vector<pair<u32, u32>> matches; // (position, pattern_index)
    double time_ms;
};

// Global match context
static MatchContext *g_mctx = nullptr;

// Match callback function
static
hwlmcb_rv_t matchCallback(size_t end, u32 id, struct hs_scratch *scratch) {
    if (g_mctx) {
        g_mctx->matches.push_back(make_pair(id, (u32)end));
    }
    return HWLM_CONTINUE_MATCHING;
}

// Load patterns from file
vector<string> loadPatterns(const string &filename, size_t max_patterns = 0) {
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
            if (max_patterns > 0 && patterns.size() >= max_patterns) {
                break;
            }
        }
    }
    
    return patterns;
}

// Read file contents
string readFile(const string &filename) {
    ifstream file(filename, ios::binary);
    if (!file.is_open()) {
        return "";
    }
    
    stringstream buffer;
    buffer << file.rdbuf();
    return buffer.str();
}

// Scan a single ruleset (text string)
size_t scanRuleset(const string &ruleset, const FDR *fdr_engine, struct hs_scratch *scratch) {
    if (ruleset.empty()) {
        return 0;
    }
    
    hwlm_group_t groups = ~0ULL;
    size_t before_count = g_mctx->matches.size();
    
    hwlm_error_t result = fdrExec(fdr_engine,
                                  (const u8 *)ruleset.c_str(),
                                  ruleset.size(),
                                  0,
                                  matchCallback,
                                  scratch,
                                  groups);
    
    g_mctx->total_bytes_scanned += ruleset.size();
    
    if (result != HWLM_SUCCESS) {
        return 0;
    }
    
    return g_mctx->matches.size() - before_count;
}

// Scan all rulesets from file (one ruleset per line)
size_t scanRulesetsFile(const string &filepath, const FDR *fdr_engine, struct hs_scratch *scratch,
                        const vector<string> &patterns, vector<RulesetResult> *results = nullptr) {
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
        
        size_t before_count = g_mctx->matches.size();
        
        auto start = chrono::high_resolution_clock::now();
        size_t matches = scanRuleset(line, fdr_engine, scratch);
        auto end = chrono::high_resolution_clock::now();
        
        double time_ms = chrono::duration_cast<chrono::microseconds>(end - start).count() / 1000.0;
        
        // Store per-ruleset result if requested
        if (results) {
            RulesetResult result;
            result.ruleset_index = rulesets_scanned;
            result.time_ms = time_ms;
            
            // Extract matches for this specific ruleset
            for (size_t i = before_count; i < g_mctx->matches.size(); i++) {
                // FDR callback returns inclusive end position (position of last character)
                // Convert to start position: inclusive_end - pattern_length + 1
                u32 pattern_id = g_mctx->matches[i].first;
                u32 inclusive_end_pos = g_mctx->matches[i].second;
                u32 start_pos = inclusive_end_pos - patterns[pattern_id].length() + 1;
                result.matches.push_back({start_pos, pattern_id});
            }

            // Ensure a consistent ordering: sort by start position then pattern id
            sort(result.matches.begin(), result.matches.end());
            
            results->push_back(result);
        }
        
        total_matches += matches;
        rulesets_scanned++;
        
        if (rulesets_scanned % 1000 == 0) {
            cout << "  Scanned " << rulesets_scanned << " rulesets..." << endl;
        }
    }
    
    cout << "  Total rulesets scanned: " << rulesets_scanned << endl;
    return total_matches;
}

int main(int argc, char *argv[]) {
    cout << "=== FDR String Matcher Application ===" << endl << endl;
    
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
    vector<string> pattern_strings = loadPatterns(patterns_file);
    
    if (pattern_strings.empty()) {
        cerr << "ERROR: No patterns loaded!" << endl;
        return 1;
    }
    
    cout << "Loaded " << pattern_strings.size() << " patterns" << endl;
    
    // Filter patterns to only those within FDR's 8-byte limit
    vector<string> valid_patterns;
    size_t filtered_count = 0;
    for (const auto &pattern : pattern_strings) {
        if (pattern.size() <= 8) {
            valid_patterns.push_back(pattern);
        } else {
            filtered_count++;
        }
    }
    
    if (filtered_count > 0) {
        cout << "Filtered out " << filtered_count << " patterns exceeding 8-byte limit" << endl;
    }
    cout << "Using " << valid_patterns.size() << " valid patterns" << endl;
    
    if (valid_patterns.empty()) {
        cerr << "ERROR: No valid patterns within 8-byte limit!" << endl;
        return 1;
    }
    cout << endl;
    
    // Convert to hwlmLiteral format
    vector<hwlmLiteral> literals;
    for (size_t i = 0; i < valid_patterns.size(); i++) {
        literals.emplace_back(valid_patterns[i], false, (u32)i);
    }
    
    // Step 2: Compile FDR engine
    cout << "Compiling FDR engine..." << endl;
    auto compile_start = chrono::high_resolution_clock::now();
    
    try {
        Grey grey;
        target_t target = get_current_target();
        
        auto proto = fdrBuildProto(1, literals, false, target, grey);
        if (!proto) {
            cerr << "ERROR: Failed to build FDR prototype" << endl;
            return 1;
        }
        
        auto fdr = fdrBuildTable(*proto, grey);
        if (!fdr) {
            cerr << "ERROR: Failed to build FDR engine" << endl;
            return 1;
        }
        
        auto compile_end = chrono::high_resolution_clock::now();
        auto compile_time = chrono::duration_cast<chrono::milliseconds>(compile_end - compile_start).count();
        
        cout << "SUCCESS: FDR engine compiled in " << compile_time << " ms" << endl;
        cout << endl;
        
        // Step 3: Create scratch space
        struct hs_scratch *scratch = (struct hs_scratch *)calloc(1, 1024);
        if (!scratch) {
            cerr << "ERROR: Failed to allocate scratch space" << endl;
            return 1;
        }
        
        // Step 4: Scan rulesets
        cout << "Scanning rulesets from: " << rulesets_file << endl;
        
        MatchContext mctx;
        g_mctx = &mctx;
        
        vector<RulesetResult> results;
        
        auto scan_start = chrono::high_resolution_clock::now();
        size_t total_matches = scanRulesetsFile(rulesets_file, fdr.get(), scratch, valid_patterns, &results);
        auto scan_end = chrono::high_resolution_clock::now();
        
        auto scan_time = chrono::duration_cast<chrono::milliseconds>(scan_end - scan_start).count();
        
        free(scratch);
        
        // Step 5: Display results
        cout << endl;
        cout << "=== Results ===" << endl;
        cout << "  Patterns loaded:      " << valid_patterns.size() << endl;
        cout << "  Total matches found:  " << mctx.matches.size() << endl;
        cout << "  Bytes scanned:        " << mctx.total_bytes_scanned << endl;
        cout << "  Compilation time:     " << compile_time << " ms" << endl;
        cout << "  Scan time:            " << scan_time << " ms" << endl;
        
        if (scan_time > 0) {
            double throughput = (mctx.total_bytes_scanned / 1024.0 / 1024.0) / (scan_time / 1000.0);
            cout << "  Throughput:           " << fixed << throughput << " MB/s" << endl;
        }
        
        // Show top matched patterns
        if (!mctx.matches.empty()) {
            cout << endl << "Top 10 matched patterns:" << endl;
            vector<size_t> pattern_counts(valid_patterns.size(), 0);
            for (const auto &match : mctx.matches) {
                pattern_counts[match.first]++;
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
                cout << "  [" << id << "] \"" << valid_patterns[id] << "\" - " << count << " matches" << endl;
            }
        }
        
        // Step 6: Write output files
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
        
    } catch (const exception &e) {
        cerr << "ERROR: " << e.what() << endl;
        return 1;
    }
    
    cout << endl << "SUCCESS!" << endl;
    return 0;
}
