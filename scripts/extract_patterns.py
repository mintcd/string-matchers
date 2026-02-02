
from typing import Callable, Optional


def extract_patterns(input_path: str, output_path: str, cond: Callable[[str], bool], count: int = 0, rulesets_path:str=None) -> int:
	"""
	Extract up to `count` patterns from `input_path` that satisfy `cond` and
	write them (one per line) to `output_path`.

	Args:
		input_path: path to the patterns file (one pattern per line).
		output_path: file to write the selected patterns to.
		cond: callable that takes a pattern string and returns True to select it.
		count: maximum number of patterns to write. 0 means no limit (write all matching).

	Returns:
		Number of patterns written.
	"""
	written = 0
	# If a rulesets file is provided and a positive `count` is requested,
	# collect all patterns satisfying `cond`, rank them by case-sensitive
	# occurrence count in `rulesets_path`, and write the top-`count` as
	# `pattern\tcount` lines. Otherwise fall back to streaming output of
	# the first `count` matching patterns (or all if count == 0).
	if rulesets_path and count:
		# Load ruleset lines (non-empty, non-comment)
		with open(rulesets_path, 'r', encoding='utf-8') as rf:
			rules = [ln for ln in rf if ln.strip() and not ln.lstrip().startswith('#')]

		# Collect patterns that satisfy cond
		patterns = []
		with open(input_path, 'r', encoding='utf-8') as inf:
			for raw in inf:
				pat = raw.strip()
				if not pat or pat.startswith('#'):
					continue
				try:
					if cond(pat):
						patterns.append(pat)
				except Exception:
					continue

		# Count occurrences (case-sensitive substring counts)
		from collections import Counter
		ctr = Counter()
		for idx, p in enumerate(patterns):
			for ln in rules:
				ctr[p] += ln.count(p)
			if (idx + 1) % 100 == 0:
				print(f"Processed {idx + 1}/{len(patterns)} patterns...", end='\r')

		# Rank and write top-`count`
		ranked = sorted(ctr.items(), key=lambda x: (-x[1], x[0]))
		with open(output_path, 'w', encoding='utf-8') as outf:
			for pat, cnt in ranked[:count]:
				outf.write(f"{pat}\n")
				written += 1
		return written

	# Streaming fallback: write first `count` matching patterns (or all if count==0)
	with open(input_path, 'r', encoding='utf-8') as inf, open(output_path, 'w', encoding='utf-8') as outf:
		for raw in inf:
			# strip leading/trailing whitespace and newline
			pat = raw.strip()
			if not pat or pat.startswith('#'):
				continue
			try:
				ok = cond(pat)
			except Exception:
				# If the user-provided predicate raises, skip the pattern
				ok = False
			if ok:
				outf.write(pat + '\n')
				written += 1
				if count and written >= count:
					break

	# Return number of patterns actually written
	return written
