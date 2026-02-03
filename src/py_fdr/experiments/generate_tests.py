import os
import random
import string
from typing import Iterable


ALPH_ABCD = 'abcd'


def int_to_pattern(x: int, length: int = 8, alphabet: str = ALPH_ABCD) -> str:
	"""Convert integer x in [0, base^length) to a pattern string over `alphabet`.

	Uses little-endian bit operations for base-4 when alphabet length==4, otherwise generic.
	"""
	base = len(alphabet)
	s = []
	for _ in range(length):
		s.append(alphabet[x % base])
		x //= base
	return ''.join(reversed(s))


def sample_unique_patterns(n: int, length: int = 8, alphabet: str = ALPH_ABCD, seed: int | None = None) -> list:
	"""Sample `n` distinct patterns uniformly from alphabet^length.

	If n > base^length will raise ValueError.
	"""
	base = len(alphabet)
	universe = base ** length
	if n > universe:
		raise ValueError('n larger than universe size')
	if seed is not None:
		random.seed(seed)
	ints = random.sample(range(universe), n)
	return [int_to_pattern(x, length=length, alphabet=alphabet) for x in ints]


def sample_patterns_with_replacement(n: int, length: int = 8, alphabet: str = ALPH_ABCD, seed: int | None = None) -> list:
	if seed is not None:
		random.seed(seed)
	return [''.join(random.choices(alphabet, k=length)) for _ in range(n)]


def generate_patterns(output_path: str, count: int = 50000, length: int = 8, alphabet: str = string.ascii_lowercase) -> None:
	"""Generate `count` patterns of `length` and write to `output_path` (one per line).

	Patterns are drawn uniformly from `alphabet`.
	"""
	os.makedirs(os.path.dirname(output_path), exist_ok=True)
	with open(output_path, "w", encoding="utf-8") as f:
		for _ in range(count):
			s = ''.join(random.choice(alphabet) for _ in range(length))
			f.write(s + "\n")


def generate_rulesets(output_path: str, count: int = 1000, length: int = 100, alphabet: str = ALPH_ABCD) -> None:
	"""Generate `count` rulesets (each a string of `length`) and write to `output_path`.

	Each ruleset is a line composed of characters from `alphabet`.
	"""
	os.makedirs(os.path.dirname(output_path), exist_ok=True)
	with open(output_path, "w", encoding="utf-8") as f:
		for _ in range(count):
			s = ''.join(random.choice(alphabet) for _ in range(length))
			f.write(s + "\n")


if __name__ == "__main__":
	# Default locations: same directory as this script
	base_dir = os.path.dirname(__file__)
	patterns_path = os.path.join(base_dir, "patterns.txt")
	rulesets_path = os.path.join(base_dir, "rulesets.txt")

	print(f"Generating patterns -> {patterns_path}")
	generate_patterns(patterns_path)
	print("Patterns generation complete.")

	print(f"Generating rulesets -> {rulesets_path}")
	generate_rulesets(rulesets_path)
	print("Rulesets generation complete.")
