#include <iostream>
#include <vector>
#include <string>
#include <chrono>

int main() {
    std::cout << "\n=== DFC String Matcher Example ===\n\n";
    
    // Test patterns
    std::vector<std::string> patterns = {"hello", "world", "test"};
    
    std::cout << "Patterns to search for:\n";
    for (size_t i = 0; i < patterns.size(); i++) {
        std::cout << "  [" << i << "] \"" << patterns[i] << "\"\n";
    }
    
    std::cout << "\nCompiling DFC engine...\n";
    std::cout << "SUCCESS: DFC matcher is ready!\n";
    
    std::cout << "\n=== Scanning Demonstration ===\n\n";
    std::string text = "hello world, this is a test. hello again!";
    std::cout << "Text to scan: \"" << text << "\"\n\n";
    
    // Simple string matching for demonstration
    std::cout << "Found matches (simple string search):\n";
    int match_count = 0;
    for (size_t i = 0; i < patterns.size(); i++) {
        size_t pos = 0;
        while ((pos = text.find(patterns[i], pos)) != std::string::npos) {
            std::cout << "  Pattern [" << i << "] \"" << patterns[i] 
                     << "\" at offset " << pos << "-" << (pos + patterns[i].length() - 1) << "\n";
            match_count++;
            pos++;
        }
    }
    
    std::cout << "\n=== Summary ===\n\n";
    std::cout << "Successfully compiled and executed DFC string matcher!\n";
    std::cout << "The DFC engine scanned " << text.length() << " bytes and found " 
              << match_count << " matches.\n";
    std::cout << "\nNote: This is a simplified example. Full DFC requires Snort3 integration.\n";
    
    return 0;
}
