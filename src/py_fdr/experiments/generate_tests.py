import os
import random
import string
from typing import Iterable


def generate_patterns(output_path: str, count: int = 50000, length: int = 8, alphabet: str = string.ascii_lowercase) -> None:
	"""Generate `count` patterns of `length` and write to `output_path` (one per line).

	Patterns are drawn uniformly from `alphabet`.
	"""
	os.makedirs(os.path.dirname(output_path), exist_ok=True)
	with open(output_path, "w", encoding="utf-8") as f:
		for _ in range(count):
			s = ''.join(random.choice(alphabet) for _ in range(length))
			f.write(s + "\n")


def generate_rulesets(output_path: str, count: int = 1000, length: int = 100, alphabet: str = string.ascii_lowercase) -> None:
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
