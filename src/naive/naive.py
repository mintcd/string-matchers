import os
import time


def naive_match(rulesets_file: str, patterns_file: str, output_dir: str, max_tests: int = 0):
    """Scan `rulesets_file` using naive matching against `patterns_file` and
    write `metadata.txt` and `results.txt` into `output_dir` using the same
    format as the other matchers.

    Args:
        rulesets_file (str): Path to the file containing rulesets (one per line).
        patterns_file (str): Path to the file containing patterns.
        output_dir (str): Directory where `metadata.txt` and `results.txt` will be written.
        max_tests (int): Optional limit on number of rulesets to process (0 = all).
    """
    # Load patterns (skip empty and comment lines)
    patterns = []
    with open(patterns_file, 'r', encoding='utf-8') as pf:
        for line in pf:
            line = line.rstrip('\n')
            if not line or line.startswith('#'):
                continue
            patterns.append(line)

    results = []
    processed = 0
    total_matches = 0

    # Scan rulesets (each line is a ruleset / text to search)
    with open(rulesets_file, 'r', encoding='utf-8') as rf:
        for idx, raw in enumerate(rf):
            line = raw.rstrip('\n')
            if not line or line.startswith('#'):
                continue

            processed += 1
            start = time.perf_counter()
            matches = naive_match_all(line, patterns)
            end = time.perf_counter()

            time_ms = (end - start) * 1000.0

            matches = matches or []
            matches.sort()

            results.append({'ruleset_index': idx, 'matches': matches, 'time_ms': time_ms})
            total_matches += len(matches)

            if processed % 100 == 0:
                print(f"  Scanned {processed} rulesets...")

            if max_tests and processed >= max_tests:
                print(f"  Reached requested max_tests={max_tests}; stopping.")
                break

    # Write outputs
    os.makedirs(output_dir, exist_ok=True)

    metadata_path = os.path.join(output_dir, 'metadata.txt')
    with open(metadata_path, 'w', encoding='utf-8') as mh:
        mh.write('Input Files:\n')
        mh.write('  Patterns: ' + patterns_file + '\n')
        mh.write('  Rulesets: ' + rulesets_file + '\n')
        mh.write('\n')
        mh.write('Column Descriptions for results.txt:\n')
        mh.write('  ruleset_index - Zero-based index of the ruleset (line number in rulesets file)\n')
        mh.write('  matches       - List of (position, pattern_index) pairs where patterns matched\n')
        mh.write('  time_ms       - Time taken to scan this ruleset in milliseconds\n')
        mh.write('\n')
        mh.write('Match Format: (position, pattern_index)\n')
        mh.write('  position      - Byte offset in the ruleset where the match starts (0-indexed)\n')
        mh.write('  pattern_index - Index of the matched pattern from patterns file\n')

    results_path = os.path.join(output_dir, 'results.txt')
    with open(results_path, 'w', encoding='utf-8') as rf:
        rf.write('ruleset_index\tmatches\ttime_ms\n')
        for r in results:
            rf.write(str(r['ruleset_index']))
            rf.write('\t')
            rf.write('[')
            first = True
            for m in r['matches']:
                if not first:
                    rf.write(',')
                rf.write(f"({m[0]},{m[1]})")
                first = False
            rf.write(']')
            rf.write('\t')
            rf.write(f"{r['time_ms']:.6f}\n")

    print(f"  Written: {metadata_path}")
    print(f"  Written: {results_path} ({len(results)} rows)")


def naive_match_all(text: str, patterns: list[str]):
    """Naive string match for multiple patterns.
    Args:
        text (str): The text to search within.
        patterns (list[str]): The patterns to search for.
    Returns:
        list[tuple[int,int]]: A list of (position, pattern_index) tuples where each pattern occurs in text.
    """
    all_matches = []
    for pattern_index, pattern in enumerate(patterns):
        matches = naive_match_single(text, pattern)
        for position in matches:
            all_matches.append((position, pattern_index))
    return all_matches

def naive_match_single(text: str, pattern: str):
    """Naive string match, actually not naive because it uses str.find.
    Args:
        text (str): The text to search within.
        pattern (str): The pattern to search for.

    Returns:
        list[int]: List of starting indices where `pattern` occurs in `text`.
    """
    matches = []
    n = len(text)
    m = len(pattern)

    if m == 0:
        return list(range(n + 1))

    # Use first character to find candidate start positions quickly.
    first = pattern[0]
    start = 0
    i = text.find(first, start)

    while i != -1:
        # Ensure remaining length is sufficient, then compare slice (fast C-level)
        if i + m <= n and text[i:i + m] == pattern:
            matches.append(i)
        start = i + 1
        i = text.find(first, start)

    return matches