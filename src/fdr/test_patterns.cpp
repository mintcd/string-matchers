/*
 * FDR Pattern Matcher Test Suite
 * 
 * This test program loads patterns from patterns.txt and runs comprehensive
 * test cases to evaluate FDR performance and correctness.
 */

#include <iostream>
#include <vector>
#include <string>
#include <fstream>
#include <sstream>
#include <cstring>
#include <memory>
#include <chrono>

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
using namespace chrono;

// Callback structure to collect matches
struct MatchContext {
    vector<pair<u32, u32>> matches; // (pattern_id, end_offset)
    size_t callback_count = 0;
};

// Global match context
static MatchContext *g_mctx = nullptr;

// Match callback function
static
hwlmcb_rv_t matchCallback(size_t end, u32 id, struct hs_scratch *scratch) {
    if (g_mctx) {
        g_mctx->matches.push_back(make_pair(id, (u32)end));
        g_mctx->callback_count++;
    }
    return HWLM_CONTINUE_MATCHING;
}

// Load patterns from file
vector<string> loadPatterns(const string& filename, size_t max_patterns = 100) {
    vector<string> patterns;
    ifstream file(filename);
    
    if (!file.is_open()) {
        cerr << "ERROR: Could not open " << filename << endl;
        return patterns;
    }
    
    string line;
    while (getline(file, line) && patterns.size() < max_patterns) {
        // FDR has a maximum pattern length of 8 bytes (HWLM_LITERAL_MAX_LEN)
        if (!line.empty() && line.length() >= 3 && line.length() <= 8) {
            patterns.push_back(line);
        }
    }
    
    return patterns;
}

// Test Case 1: Simple exact matches
void testExactMatches(const FDR *fdr, const vector<hwlmLiteral>& literals) {
    cout << "\n=== Test 1: Exact Pattern Matches ===" << endl;
    
    // Create test texts that contain exact patterns
    vector<string> test_texts = {
        "HTTP/1.1 200 OK",
        "User-Agent: Firefox/89.0",
        "Java/1.6.0_45 application",
        "GET /index.html HTTP/1.0",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    };
    
    struct hs_scratch *scratch = (struct hs_scratch *)calloc(1, 1024);
    hwlm_group_t groups = ~0ULL;
    
    int total_matches = 0;
    for (size_t i = 0; i < test_texts.size(); i++) {
        MatchContext mctx;
        g_mctx = &mctx;
        
        fdrExec(fdr, (const u8 *)test_texts[i].c_str(), test_texts[i].size(), 
                0, matchCallback, scratch, groups);
        
        cout << "  Text " << (i+1) << ": \"" << test_texts[i].substr(0, 40);
        if (test_texts[i].length() > 40) cout << "...";
        cout << "\" -> " << mctx.matches.size() << " matches" << endl;
        
        total_matches += mctx.matches.size();
    }
    
    cout << "Total matches: " << total_matches << endl;
    free(scratch);
}

// Test Case 2: Performance test with large text
void testPerformance(const FDR *fdr, const vector<hwlmLiteral>& literals) {
    cout << "\n=== Test 2: Performance Test ===" << endl;
    
    // Generate a large text buffer with repeated patterns
    stringstream ss;
    ss << "HTTP/1.1 200 OK\r\n";
    ss << "User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Firefox/89.0\r\n";
    ss << "Content-Type: text/html; charset=UTF-8\r\n";
    ss << "Content-Length: 1234\r\n";
    ss << "\r\n";
    ss << "<html><head><title>Test Page</title></head><body>";
    ss << "This is a test page with various patterns: HTTP, HTTPS, GET, POST, Java/1.6.0_45, ";
    ss << "Firefox/1.0, Chrome/90.0, Safari/14.0, etc.\r\n";
    
    // Repeat the text to create a large buffer
    string base_text = ss.str();
    string large_text;
    for (int i = 0; i < 1000; i++) {
        large_text += base_text;
    }
    
    cout << "  Text size: " << large_text.size() << " bytes" << endl;
    cout << "  Pattern count: " << literals.size() << endl;
    
    struct hs_scratch *scratch = (struct hs_scratch *)calloc(1, 1024);
    hwlm_group_t groups = ~0ULL;
    
    MatchContext mctx;
    g_mctx = &mctx;
    
    // Warm-up run
    fdrExec(fdr, (const u8 *)large_text.c_str(), large_text.size(), 
            0, matchCallback, scratch, groups);
    
    // Timed runs
    const int num_runs = 10;
    auto start = high_resolution_clock::now();
    
    for (int i = 0; i < num_runs; i++) {
        mctx.matches.clear();
        mctx.callback_count = 0;
        fdrExec(fdr, (const u8 *)large_text.c_str(), large_text.size(), 
                0, matchCallback, scratch, groups);
    }
    
    auto end = high_resolution_clock::now();
    auto duration = duration_cast<microseconds>(end - start);
    
    double avg_time_ms = duration.count() / 1000.0 / num_runs;
    double throughput_mbps = (large_text.size() * num_runs) / (duration.count() / 1e6) / (1024 * 1024);
    
    cout << "  Matches found: " << mctx.matches.size() << endl;
    cout << "  Avg scan time: " << avg_time_ms << " ms" << endl;
    cout << "  Throughput: " << throughput_mbps << " MB/s" << endl;
    
    free(scratch);
}

// Test Case 3: No match test
void testNoMatches(const FDR *fdr, const vector<hwlmLiteral>& literals) {
    cout << "\n=== Test 3: No Match Test ===" << endl;
    
    string text = "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx";
    
    struct hs_scratch *scratch = (struct hs_scratch *)calloc(1, 1024);
    hwlm_group_t groups = ~0ULL;
    
    MatchContext mctx;
    g_mctx = &mctx;
    
    fdrExec(fdr, (const u8 *)text.c_str(), text.size(), 
            0, matchCallback, scratch, groups);
    
    cout << "  Text: (60 'x' characters)" << endl;
    cout << "  Matches found: " << mctx.matches.size() << endl;
    cout << "  Status: " << (mctx.matches.empty() ? "PASS" : "FAIL") << endl;
    
    free(scratch);
}

// Test Case 4: Overlapping patterns
void testOverlappingPatterns(const FDR *fdr, const vector<hwlmLiteral>& literals) {
    cout << "\n=== Test 4: Overlapping Patterns ===" << endl;
    
    // Text with overlapping matches
    string text = "HTTP/1.1 and HTTP/1.0 and HTTP";
    
    struct hs_scratch *scratch = (struct hs_scratch *)calloc(1, 1024);
    hwlm_group_t groups = ~0ULL;
    
    MatchContext mctx;
    g_mctx = &mctx;
    
    fdrExec(fdr, (const u8 *)text.c_str(), text.size(), 
            0, matchCallback, scratch, groups);
    
    cout << "  Text: \"" << text << "\"" << endl;
    cout << "  Matches found: " << mctx.matches.size() << endl;
    
    // Display matches
    for (const auto& match : mctx.matches) {
        if (match.first < literals.size()) {
            cout << "    Pattern [" << match.first << "] \"" 
                 << literals[match.first].s << "\" at offset " << match.second << endl;
        }
    }
    
    free(scratch);
}

// Test Case 5: Case sensitivity
void testCaseSensitivity(const FDR *fdr, const vector<hwlmLiteral>& literals) {
    cout << "\n=== Test 5: Case Sensitivity ===" << endl;
    
    vector<string> test_cases = {
        "HTTP",      // Uppercase
        "http",      // Lowercase
        "Http",      // Mixed case
    };
    
    struct hs_scratch *scratch = (struct hs_scratch *)calloc(1, 1024);
    hwlm_group_t groups = ~0ULL;
    
    for (const auto& text : test_cases) {
        MatchContext mctx;
        g_mctx = &mctx;
        
        fdrExec(fdr, (const u8 *)text.c_str(), text.size(), 
                0, matchCallback, scratch, groups);
        
        cout << "  \"" << text << "\" -> " << mctx.matches.size() << " matches" << endl;
    }
    
    free(scratch);
}

int main(int argc, char *argv[]) {
    cout << "=== FDR Pattern Matcher Test Suite ===" << endl;
    
    // Load patterns from file
    size_t max_patterns = 50; // Start with 50 patterns for testing
    if (argc > 1) {
        max_patterns = atoi(argv[1]);
    }
    
    cout << "\nLoading patterns from patterns.txt..." << endl;
    vector<string> pattern_strings = loadPatterns("../patterns.txt", max_patterns);
    
    if (pattern_strings.empty()) {
        cerr << "ERROR: No patterns loaded!" << endl;
        return 1;
    }
    
    cout << "Loaded " << pattern_strings.size() << " patterns" << endl;
    
    // Convert to hwlmLiteral format
    vector<hwlmLiteral> literals;
    for (size_t i = 0; i < pattern_strings.size(); i++) {
        literals.emplace_back(pattern_strings[i], false, i);
    }
    
    // Compile FDR engine
    cout << "\nCompiling FDR engine..." << endl;
    
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
        
        cout << "SUCCESS: FDR engine compiled with " << literals.size() << " patterns" << endl;
        
        // Run test cases
        testExactMatches(fdr.get(), literals);
        testPerformance(fdr.get(), literals);
        testNoMatches(fdr.get(), literals);
        testOverlappingPatterns(fdr.get(), literals);
        testCaseSensitivity(fdr.get(), literals);
        
        cout << "\n=== All Tests Completed ===" << endl;
        
    } catch (const exception& e) {
        cerr << "ERROR: " << e.what() << endl;
        return 1;
    }
    
    return 0;
}
