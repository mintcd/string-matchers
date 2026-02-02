#!/usr/bin/env python3
"""Compare two TSV results files produced by FDR runs.

Usage:
  python scripts/compare_results.py A_results.txt B_results.txt

Prints a summary and the first mismatches (up to 20). Exits with code 0 if
all match lists are identical for the same ruleset indices, otherwise exits
with code 2.
"""

import ast
import argparse
import sys
import re
from pathlib import Path


def load(path: Path):
    d = {}
    with path.open('r', encoding='utf-8') as fh:
        # skip header if present
        first = fh.readline()
        if not first:
            return d
        # if first line doesn't look like header, treat it as data
        if not first.startswith('ruleset_index'):
            fh = (line for line in ([first] + fh.readlines()))
        for line in fh:
            line = line.rstrip('\n')
            if not line:
                continue
            parts = line.split('\t')
            if len(parts) < 2:
                continue
            try:
                idx = int(parts[0])
            except Exception:
                continue
            s = parts[1]
            try:
                matches = ast.literal_eval(s)
            except Exception:
                # try to normalize tuple spacing: '(25,21)' -> '(25, 21)'
                s2 = re.sub(r'\(\s*(\d+)\s*,\s*(\d+)\s*\)', r'(\1, \2)', s)
                matches = ast.literal_eval(s2)
            d[idx] = matches
    return d

def compare_results(a_path: Path, b_path: Path, show: int = 20) -> int:
    """Compare two result files and print a summary of differences.

    Args:
        a_path: Path to first results file
        b_path: Path to second results file
        show: number of mismatches to display
    Returns:
        Exit code: 0 if files match, 2 if differences found, 3 on error.
    """
    # Accept either str or Path for convenience (notebooks often pass str)
    print(f'Comparing results:\n A: {a_path}\n B: {b_path}\n')
    a_path = Path(a_path)
    b_path = Path(b_path)

    if not a_path.exists():
        print('File not found:', a_path)
        return 3
    if not b_path.exists():
        print('File not found:', b_path)
        return 3

    Amap = load(a_path)
    Bmap = load(b_path)

    Ak = set(Amap.keys())
    Bk = set(Bmap.keys())
    common = sorted(Ak & Bk)
    onlyA = sorted(Ak - Bk)
    onlyB = sorted(Bk - Ak)

    print(f'counts: A={len(Amap)} B={len(Bmap)} common={len(common)}')
    if onlyA:
        print(f'indexes only in A (sample): {onlyA[:10]}')
    if onlyB:
        print(f'indexes only in B (sample): {onlyB[:10]}')

    mismatches = []
    for idx in common:
        if Amap[idx] != Bmap[idx]:
            mismatches.append((idx, Amap[idx], Bmap[idx]))

    print('mismatches:', len(mismatches))
    toshow = min(len(mismatches), show)
    for i in range(toshow):
        idx, a, b = mismatches[i]
        print('\n--- mismatch', i + 1, 'index', idx)
        print('A:', a)
        print('B:', b)

    if len(mismatches) == 0 and not onlyA and not onlyB:
        print('\nFiles coincide (match lists identical for all indices).')
        return 0
    else:
        print('\nDone.')
        return 2
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('a')
    parser.add_argument('b')
    parser.add_argument('--show', type=int, default=20,
                        help='number of mismatches to show')
    args = parser.parse_args()

    return compare_results(Path(args.a), Path(args.b), args.show)


if __name__ == '__main__':
    sys.exit(main())
