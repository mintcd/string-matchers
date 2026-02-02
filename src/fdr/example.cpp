/*
 * FDR String Matcher Example
 * 
 * This example demonstrates how to use the FDR (Fast Dictionary-based Regular expression)
 * string matcher extracted from Hyperscan.
 * 
 * The example:
 * 1. Compiles a set of literal patterns into an FDR engine
 * 2. Scans text buffers for matches
 * 3. Reports all found matches
 */

#include <iostream>
#include <vector>
#include <string>
#include <cstring>
#include <fstream>
#include <sstream>
#include <algorithm>
#include <cctype>
#include <memory>
#include <ctime>

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

// Callback structure to collect matches
struct MatchContext {
    vector<pair<u32, u32>> matches; // (pattern_id, end_offset)
};

// Global match context (for simplicity in this example)
static MatchContext *g_mctx = nullptr;

// Match callback function
static
hwlmcb_rv_t matchCallback(size_t end, u32 id, struct hs_scratch *scratch) {
    if (g_mctx) {
        g_mctx->matches.push_back(make_pair(id, (u32)end));
    }
    return HWLM_CONTINUE_MATCHING;
}

int main(int argc, char **argv) {
    cout << "=== FDR String Matcher Example ===" << endl << endl;

    // Step 1: Define patterns to search for (can be provided via CLI)
    vector<hwlmLiteral> literals;

    auto trim = [](string &s) {
        s.erase(s.begin(), find_if(s.begin(), s.end(), [](unsigned char ch) { return !isspace(ch); }));
        s.erase(find_if(s.rbegin(), s.rend(), [](unsigned char ch) { return !isspace(ch); }).base(), s.end());
    };

    auto split_csv = [&](const string &in) {
        vector<string> out;
        string token;
        istringstream ss(in);
        while (getline(ss, token, ',')) {
            trim(token);
            if (!token.empty()) out.push_back(token);
        }
        return out;
    };

    // Parse CLI: --string "text to scan" and --patterns "p1,p2,..."
    string input_str;
    string patterns_str;

    for (int i = 1; i < argc; ++i) {
        string a = argv[i];
        if (a == "--string" && i + 1 < argc) {
            input_str = argv[++i];
        } else if (a == "--patterns" && i + 1 < argc) {
            patterns_str = argv[++i];
        } else if (a == "--help" || a == "-h") {
            cout << "Usage: fdr_example --string \"text\" --patterns \"p1,p2,...\"\n";
            return 0;
        } else {
            cerr << "Unknown option: " << a << "\n";
            return 1;
        }
    }

    if (input_str.empty() || patterns_str.empty()) {
        cerr << "ERROR: both --string and --patterns must be provided.\n";
        cout << "Usage: fdr_example --string \"text\" --patterns \"p1,p2,...\"\n";
        return 1;
    }

    // parse patterns CSV and build literals
    vector<string> pats = split_csv(patterns_str);
    u32 id = 0;
    for (auto &p : pats) {
        literals.emplace_back(p, false, id++);
    }

    string text = input_str;
    cout << "Text: \"" << text << "\"" << endl;
    cout << endl;

    cout << "Patterns" << endl;
    for (const auto &lit : literals) {
        cout << "  [" << lit.id << "] \"" << lit.s << "\"" << endl;
    }
    cout << endl;

    // Step 2: Compile patterns into FDR engine
    cout << "Compiling FDR engine..." << endl;
    
    try {
        // Create Grey options (compilation settings)
        Grey grey;
        
        // Get current target (CPU capabilities)
        target_t target = get_current_target();

           cout << "Building FDR prototype..." << endl;
           cout << "Target info: has_avx2=" << (target.has_avx2() ? "yes" : "no")
               << ", is_atom_class=" << (target.is_atom_class() ? "yes" : "no") << endl;
           cout << "Literals count: " << literals.size() << endl;
        
        // Build FDR engine prototype
        // Using engine type HWLM_ENGINE_FDR (value 1)
        auto proto = fdrBuildProto(1, literals, false, target, grey);
        

        if (!proto) {
            cout << "ERROR: Failed to build FDR prototype" << endl;
            cout << "(diagnostic) Failed at fdrBuildProto - proto is null" << endl;
            return 1;
        }

        cout << "FDR proto built" << endl;
        
        // Build the actual FDR engine from prototype
        auto fdr = fdrBuildTable(*proto, grey);

        cout << "FDR table built (returned pointer?) " << (fdr ? "yes" : "no") << endl;

        if (!fdr) {
            cout << "ERROR: Failed to build FDR engine" << endl;
            cout << "(diagnostic) fdrBuildTable returned null" << endl;
            return 1;
        }
        
        cout << "SUCCESS: FDR engine compiled!" << endl;
        cout << endl;

        // Step 3: Create a minimal scratch space
        // For simple FDR usage, we just need a scratch with fdr_conf fields set to null
        struct hs_scratch *scratch = (struct hs_scratch *)calloc(1, 1024); // Allocate enough space
        if (!scratch) {
            cout << "ERROR: Failed to allocate scratch space" << endl;
            return 1;
        }
        
        cout << "Allocated scratch space" << endl;

        // Step 4: Scan text for matches
        cout << "=== Scanning Demonstration ===" << endl;
        cout << endl;
        
        // Perform the scan
        MatchContext mctx;
        g_mctx = &mctx; // Set global context for callback
        hwlm_group_t groups = ~0ULL; // Match all groups

        cout << "Calling fdrExec..." << endl;
        
        hwlm_error_t result = fdrExec(fdr.get(), 
                                      (const u8 *)text.c_str(), 
                                      text.size(), 
                                      0, 
                                      matchCallback, 
                                      scratch,
                                      groups);
        
        if (result != HWLM_SUCCESS) {
            cout << "ERROR: FDR scan failed" << endl;
            free(scratch);
            return 1;
        }
        
        // Free scratch
        free(scratch);
        
        // Display results
        cout << "Found " << mctx.matches.size() << " matches:" << endl;
        for (const auto &match : mctx.matches) {
            const auto &lit = literals[match.first];
            u32 end_offset = match.second;
            u32 start_offset = (end_offset >= lit.s.length()) ? (end_offset - lit.s.length()) : 0;
            cout << "  Pattern [" << match.first << "] \"" << lit.s 
                 << "\" at offset " << start_offset << "-" << end_offset << endl;
        }
        cout << endl;
        
        cout << "=== Summary ===" << endl;
        cout << endl;
        cout << "Successfully compiled and executed FDR string matcher!" << endl;
        cout << "The FDR engine scanned " << text.size() << " bytes and found " 
             << mctx.matches.size() << " matches." << endl;
        
    } catch (const exception &e) {
        cout << "ERROR: " << e.what() << endl;
        return 1;
    }

    return 0;
}

// cd 'D:\Projects\string-matchers\src\fdr-minified\build'
// cmake --build . --config Debug --target fdr_example;
// & 'D:\Projects\string-matchers\src\fdr-minified\build\Debug\fdr_example.exe' --string "hello world, this is a test. hello again!" --patterns "hello,world,test" > logfile.txt 2>&1

// cmake --build . --config Debug --target fdr_example; & 'D:\Projects\string-matchers\src\fdr\build\Debug\fdr_example.exe' --string "hello world, this is a test. hello again!" --patterns "hello,world,test"