#!/usr/bin/env python3
"""Runner: build SimpleFDR from dataset/100_short_patterns.txt, run it
against each line in dataset/rulesets.txt, and write results to
output/py_fdr_100_short_patterns/results.txt

This script intentionally uses the simplified `SimpleFDR` in
`fdr.py` to produce lightweight, comparable output for analysis.
"""
import os
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
# Ensure this script's directory is on sys.path so local module imports work
import sys
SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))
DATASET_DIR = ROOT / 'dataset'
OUTPUT_DIR = ROOT / 'output' / 'py_fdr_100_short_patterns'

from FDR import FDR


def load_patterns(path: Path):
    pats = []
    with path.open('rb') as fh:
        for line in fh:
            line = line.rstrip(b"\r\n")
            if not line:
                continue
            pats.append(line)
    return pats


def load_rulesets(path: Path):
    lines = []
    with path.open('rb') as fh:
        for line in fh:
            lines.append(line.rstrip(b"\r\n"))
    return lines


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    pats = load_patterns(DATASET_DIR / '100_short_patterns.txt')
    rules = load_rulesets(DATASET_DIR / 'rulesets.txt')

    engine = FDR(pats, stride=1, domain_bits=9)

    results = []

    for idx, rule in enumerate(rules):
        hits = []

        def cb(offset, pid):
            hits.append((offset, pid))

        t0 = time.perf_counter()
        engine.exec(rule, cb)
        t1 = time.perf_counter()

        dt_ms = (t1 - t0) * 1000.0
        if idx % 100 == 0:
            # print progress and a short cpu counter snapshot (if available)
            counters = getattr(engine, 'cpu', None)
            counters_str = ''
            if counters is not None:
                counters_str = f" cpu_counters={counters.counters}"
            print(f"Processed ruleset {idx}, matches={len(hits)}, time={dt_ms:.6f} ms{counters_str}")
            # reset engine counters between large batches
            if hasattr(engine, 'reset_counters'):
                engine.reset_counters()
        results.append((idx, hits, dt_ms))

    out_file = OUTPUT_DIR / 'results.txt'
    with out_file.open('w', encoding='utf-8') as fh:
        fh.write('ruleset_index\tmatches\ttime_ms\n')
        for idx, hits, dt in results:
            fh.write(f"{idx}\t{hits}\t{dt:.6f}\n")

    meta = OUTPUT_DIR / 'metadata.txt'
    with meta.open('w', encoding='utf-8') as fh:
        fh.write(f'patterns:{len(pats)}\n')
        fh.write(f'rulesets:{len(rules)}\n')
        fh.write(f'engine_stride:{engine.stride}\n')
        fh.write(f'engine_domain_bits:{engine.domain}\n')

    print('Wrote', out_file)


if __name__ == '__main__':
    main()
