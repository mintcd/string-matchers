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
#include <memory>

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

int main() {
    cout << "=== FDR String Matcher Example ===" << endl << endl;

    // Step 1: Define patterns to search for
    vector<hwlmLiteral> literals;
    
    // Pattern 0: "hello"
    literals.emplace_back("hello", false, 0);
    
    // Pattern 1: "world"
    literals.emplace_back("world", false, 1);
    
    // Pattern 2: "test"
    literals.emplace_back("test", false, 2);

    cout << "Patterns to search for:" << endl;
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
        
        // Build FDR engine prototype
        // Using engine type HWLM_ENGINE_FDR (value 1)
        auto proto = fdrBuildProto(1, literals, false, target, grey);
        
        if (!proto) {
            cout << "ERROR: Failed to build FDR prototype" << endl;
            return 1;
        }
        
        // Build the actual FDR engine from prototype
        auto fdr = fdrBuildTable(*proto, grey);
        
        if (!fdr) {
            cout << "ERROR: Failed to build FDR engine" << endl;
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
        
        string text = "hello world, this is a test. hello again!";
        cout << "Text to scan: \"" << text << "\"" << endl;
        cout << endl;
        
        // Perform the scan
        MatchContext mctx;
        g_mctx = &mctx; // Set global context for callback
        hwlm_group_t groups = ~0ULL; // Match all groups
        
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
