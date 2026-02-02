"""Main script - imports dataset download functionality."""

from dataset_download import download_rulesets, extract_patterns


if __name__ == "__main__":
    # Download rulesets to string-matchers/dataset/rulesets
    download_rulesets()
    
    # Extract patterns to string-matchers/dataset/patterns.txt
    extract_patterns()
