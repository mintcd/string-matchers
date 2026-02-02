from naive import naive_match

if __name__ == "__main__":
    rulesets = r'dataset\rulesets.txt'
    patterns = r'dataset\100_short_patterns.txt'
    out_dir = r'output\naive'
    naive_match(rulesets, patterns, out_dir)