#!/usr/bin/env python3
from pathlib import Path
import sys
import random
import statistics
import csv

# ensure src is on sys.path
root = Path(__file__).resolve().parents[3]
src_path = str(root / 'src')
if src_path not in sys.path:
    sys.path.insert(0, src_path)

from py_fdr.main import load_patterns, scan_rulesets_file, FDRCompiler, FDR
import os
import importlib.machinery
import importlib.util


def main():
    base = Path(__file__).parent
    # Prefer local experiments/dataset if present (generated tests), else fall back to repo-level dataset
    local_dataset = base / 'dataset'
    # loader for generate_tests helpers (in same folder)
    gt_path = base / 'generate_tests.py'
    gt = None
    if gt_path.exists():
        loader = importlib.machinery.SourceFileLoader('generate_tests', str(gt_path))
        spec = importlib.util.spec_from_loader(loader.name, loader)
        gt = importlib.util.module_from_spec(spec)
        loader.exec_module(gt)

    if (local_dataset / 'short_patterns.txt').exists():
        short_patterns_path = local_dataset / 'short_patterns.txt'
    else:
        short_patterns_path = root / 'dataset' / 'short_patterns.txt'

    # rulesets: prefer experiments/rulesets.txt, then experiments/dataset/rulesets.txt, then repo dataset
    rulesets_candidate = base / 'rulesets.txt'
    if rulesets_candidate.exists():
        rulesets_path = rulesets_candidate
    elif (local_dataset / 'rulesets.txt').exists():
        rulesets_path = local_dataset / 'rulesets.txt'
    else:
        rulesets_path = root / 'dataset' / 'rulesets.txt'

    print('short_patterns:', short_patterns_path)
    print('rulesets:', rulesets_path)

    # We will sample directly from the 4^8 universe (alphabet a-d) using helpers if available.
    if gt is None:
        # fallback: load any provided short_patterns file
        short_patterns = list(load_patterns(str(short_patterns_path)))
        if not short_patterns:
            raise SystemExit('No short_patterns loaded and generate_tests not available')
        use_universe = False
    else:
        use_universe = True

    # pattern counts: 8,16,24,... up to 50000
    pattern_counts = list(range(8, 50001, 8))

    log_path = base / 'experiment_progress.csv'
    if not log_path.exists():
        with log_path.open('w', encoding='utf-8', newline='') as lh:
            writer = csv.writer(lh)
            writer.writerow(['n_patterns','avg_time_ms','total_matches','total_bytes'])

    random.seed(1234)

    for idx, n in enumerate(pattern_counts, start=1):
        try:
            if use_universe:
                # universe size base^length where base=4 and length=8
                try:
                    if n <= (len(gt.ALPH_ABCD) ** 8):
                        sample = gt.sample_unique_patterns(n, length=8, alphabet=gt.ALPH_ABCD, seed=1234 + idx)
                    else:
                        sample = gt.sample_patterns_with_replacement(n, length=8, alphabet=gt.ALPH_ABCD, seed=1234 + idx)
                except Exception:
                    # fallback to drawing with replacement
                    sample = gt.sample_patterns_with_replacement(n, length=8, alphabet=gt.ALPH_ABCD, seed=1234 + idx)
            else:
                if n <= len(short_patterns):
                    sample = random.sample(short_patterns, n)
                else:
                    sample = random.choices(short_patterns, k=n)

            # compile
            compiler = FDRCompiler(sample)
            compiler.compile(strategy=1)
            engine = FDR(compiler)

            # scan all rulesets (no max_tests)
            results, total_matches, total_bytes = scan_rulesets_file(str(rulesets_path), engine, sample, max_tests=0)

            times = [r['time_ms'] for r in results] if results else [0.0]
            avg_time = statistics.mean(times)

            # append to CSV
            with log_path.open('a', encoding='utf-8', newline='') as lh:
                writer = csv.writer(lh)
                writer.writerow([n, f"{avg_time:.6f}", total_matches, total_bytes])

            # write per-length results and metadata in experiments/output
            out_base = base / 'output'
            out_base.mkdir(parents=True, exist_ok=True)

            # save patterns used for this run
            patterns_file_path = out_base / f'patterns_length_{n}.txt'
            with patterns_file_path.open('w', encoding='utf-8') as pf:
                for p in sample:
                    pf.write(p + '\n')
                    
            # write results in the requested single-file form
            results_path = out_base / f'results_length_{n}.txt'
            with results_path.open('w', encoding='utf-8') as rf:
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

            print(f"[{idx}/{len(pattern_counts)}] n={n} avg_time_ms={avg_time:.6f} matches={total_matches} -> {results_path}")

        except Exception as e:
            print(f"ERROR at n={n}: {e}")
            # still continue to next n
            with log_path.open('a', encoding='utf-8', newline='') as lh:
                writer = csv.writer(lh)
                writer.writerow([n, 'ERROR', 'ERROR', 'ERROR'])

    print('Experiment finished')


if __name__ == '__main__':
    main()
