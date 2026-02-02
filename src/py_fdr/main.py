#!/usr/bin/env python3
"""
Python entrypoint for py-fdr runner.
Accepts the same CLI as the C++ `main.cpp` programs and writes
`metadata.txt` and `results.txt` to the output directory.
"""
import argparse
import os
import sys
import time
from typing import List, Tuple

from .FDRCompiler import FDRCompiler
from .FDR import FDR


def load_patterns(path: str, max_patterns: int = 0) -> List[str]:
	pats: List[str] = []
	with open(path, 'r', encoding='utf-8') as fh:
		for line in fh:
			line = line.rstrip('\n')
			if not line or line.startswith('#'):
				continue
			pats.append(line)
			if max_patterns and len(pats) >= max_patterns:
				break
	return pats


def scan_rulesets_file(filepath: str, fdr_engine: FDR, patterns: List[str], max_tests: int = 0):
	results = []
	total_matches = 0
	total_bytes = 0

	processed = 0
	with open(filepath, 'r', encoding='utf-8') as fh:
		for idx, raw in enumerate(fh):
			line = raw.rstrip('\n')
			if not line or line.startswith('#'):
				continue

			# Count this as a processed testcase
			processed += 1

			total_bytes += len(line)

			try:
				start = time.perf_counter()
				matches = fdr_engine.exec(line)
				end = time.perf_counter()
			except Exception as e:
				# Print the testcase that caused the error and re-raise
				print(f"ERROR while processing ruleset index {idx}: {line}", file=sys.stderr)
				raise

			time_ms = (end - start) * 1000.0

			# matches returned as list of (start_pos, pattern_index)
			matches = matches or []

			# sort by start position then pattern id
			matches.sort()

			results.append({'ruleset_index': idx, 'matches': matches, 'time_ms': time_ms})

			total_matches += len(matches)

			if (processed) % 100 == 0:
				print(f"  Scanned {processed} rulesets...")

			if max_tests and processed >= max_tests:
				print(f"  Reached requested --test_num={max_tests}; stopping.")
				break

	print(f"  Total rulesets scanned: {len(results)}")
	return results, total_matches, total_bytes


def write_outputs(output_dir: str, patterns_file: str, rulesets_file: str, patterns: List[str], results: List[dict]):
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

	print('  Written: metadata.txt')

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

	print(f"  Written: results.txt ({len(results)} rows)")


def main(argv: List[str]):
	parser = argparse.ArgumentParser(description='py-fdr runner')
	parser.add_argument('--patterns', required=True, help='Patterns file')
	parser.add_argument('--rulesets', required=True, help='Rulesets file')
	parser.add_argument('--out', required=True, help='Output directory for results')
	parser.add_argument('--test_num', type=int, default=0, help='Maximum number of tests to run (0 = all)')

	args = parser.parse_args(argv)

	patterns_file = args.patterns
	rulesets_file = args.rulesets
	output_dir = args.out

	print('=== py-FDR String Matcher Application ===\n')

	# Load patterns
	print('Loading patterns from:', patterns_file)
	pattern_strings = load_patterns(patterns_file)
	if not pattern_strings:
		print('ERROR: No patterns loaded!', file=sys.stderr)
		return 1

	print(f'Loaded {len(pattern_strings)} patterns')

	# Filter patterns to <= 8 bytes
	valid_patterns = [p for p in pattern_strings if len(p) <= 8]
	filtered_count = len(pattern_strings) - len(valid_patterns)
	if filtered_count > 0:
		print(f'Filtered out {filtered_count} patterns exceeding 8-byte limit')
	print(f'Using {len(valid_patterns)} valid patterns')

	if not valid_patterns:
		print('ERROR: No valid patterns within 8-byte limit!', file=sys.stderr)
		return 1

	# Compile
	print('\nCompiling FDR engine...')
	compile_start = time.perf_counter()
	compiler = FDRCompiler(valid_patterns)
	compiler.compile(strategy=1)
	fdr_engine = FDR(compiler)
	compile_end = time.perf_counter()
	compile_time_ms = (compile_end - compile_start) * 1000.0
	print(f'SUCCESS: FDR engine compiled in {int(compile_time_ms)} ms\n')

	# Scan rulesets
	print('Scanning rulesets from:', rulesets_file)
	scan_start = time.perf_counter()
	results, total_matches, total_bytes = scan_rulesets_file(rulesets_file, fdr_engine, valid_patterns, max_tests=args.test_num)
	scan_end = time.perf_counter()
	scan_time_ms = (scan_end - scan_start) * 1000.0

	# Display results summary
	print('\n=== Results ===')
	print('  Patterns loaded:      ', len(valid_patterns))
	# Collect all matches from results
	all_matches = []
	for r in results:
		all_matches.extend(r['matches'])

	print('  Total matches found:  ', len(all_matches))
	print('  Bytes scanned:        ', total_bytes)
	print('  Compilation time:     ', f"{int(compile_time_ms)} ms")
	print('  Scan time:            ', f"{int(scan_time_ms)} ms")
	if scan_time_ms > 0:
		throughput = (total_bytes / 1024.0 / 1024.0) / (scan_time_ms / 1000.0)
		print('  Throughput:           ', f"{throughput:.2f} MB/s")

	# Top matched patterns
	if all_matches:
		print('\nTop 10 matched patterns:')
		pattern_counts = [0] * len(valid_patterns)
		for m in all_matches:
			pattern_counts[m[1]] += 1

		sorted_patterns = [(c, i) for i, c in enumerate(pattern_counts) if c > 0]
		sorted_patterns.sort(reverse=True)

		for i, (count, pid) in enumerate(sorted_patterns[:10]):
			print(f"  [{pid}] \"{valid_patterns[pid]}\" - {count} matches")

	# Write outputs
	print('\nWriting output files to:', output_dir)
	write_outputs(output_dir, patterns_file, rulesets_file, valid_patterns, results)

	print('\nSUCCESS!')
	return 0


if __name__ == '__main__':
	sys.exit(main(sys.argv[1:]))
