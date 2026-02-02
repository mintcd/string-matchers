"""Clean workspace: remove downloaded, build and output files.

Expose a callable `clean(root='.', yes=False, verbose=False)` so other
tools can invoke cleanup programmatically. The function will consult the
download helper modules (when available) to know which files were fetched
and include `dataset/` and `output/` for removal.
"""

from pathlib import Path
import argparse
import shutil
import sys
import os
from typing import Iterable, List


def _collect_from_downloaders(root: Path):
	"""Return a set of paths known to be created by the downloader modules."""
	targets = set()

	# Load downloader modules directly from files to avoid import path issues
	dl_dir = (root / "scripts" / "downloads")
	loader_info = [
		(dl_dir / "download_ac.py", "AC_FILES"),
		(dl_dir / "download_dfc.py", "DFC_FILES"),
		(dl_dir / "download_fdr.py", "FDR_FILES"),
	]

	import importlib.util

	for path, varname in loader_info:
		try:
			if not path.exists():
				continue
			spec = importlib.util.spec_from_file_location(f"_dl_{path.stem}", str(path))
			mod = importlib.util.module_from_spec(spec)
			spec.loader.exec_module(mod)  # type: ignore
			mapping = getattr(mod, varname, {}) or {}
			for dest in mapping.keys():
				targets.add((root / dest).resolve())
				# Also add the top package subdirectory (e.g. src/fdr/cmake,
				# src/fdr/hwlm, src/fdr/fdr) so we can remove the whole
				# folder instead of individual files when appropriate.
				try:
					parts = Path(dest).parts
					# Expect patterns like src/<pkg>/<subdir>/...
					if len(parts) >= 3 and parts[0] == 'src':
						topdir = root.joinpath(*parts[:3]).resolve()
						targets.add(topdir)
				except Exception:
					pass
		except Exception:
			# ignore problems loading downloaders; fall back gracefully
			continue

	# The dataset downloader writes into `dataset/` (rulesets, patterns)
	dataset_dir = (root / "dataset").resolve()
	if dataset_dir.exists():
		targets.add(dataset_dir)

	# output/ directory produced by runs
	output_dir = (root / "output").resolve()
	if output_dir.exists():
		targets.add(output_dir)

	return targets


def _collect_generic(root: Path) -> Iterable[Path]:
	"""Collect common build/temporary targets under the project root."""
	patterns_files = [
		"**/*.pyc",
		"**/*.pyo",
		"**/*~",
		"**/*.o",
		"**/*.obj",
		"**/*.so",
		"**/*.dll",
		"**/*.exe",
		"**/*.class",
	]

	dir_names = ["__pycache__", "build", "dist", "bin", "obj"]

	targets = set()

	for name in dir_names:
		for d in root.rglob(name):
			if d.is_dir():
				targets.add(d.resolve())

	for pat in patterns_files:
		for p in root.glob(pat):
			targets.add(p.resolve())

	# logs/ at root
	logs = (root / "logs").resolve()
	if logs.exists():
		targets.add(logs)

	return targets


def _remove(path: Path, do_remove: bool, verbose: bool):
	if not do_remove:
		print(f"Would remove: {path}")
		return
	if path.is_dir():
		if verbose:
			print(f"Removing directory: {path}")
		shutil.rmtree(path, ignore_errors=True)
	else:
		if verbose:
			print(f"Removing file: {path}")
		try:
			path.unlink()
		except Exception:
			try:
				shutil.rmtree(path)
			except Exception as e:
				print(f"Failed to remove {path}: {e}", file=sys.stderr)


def clean(root: str = ".", yes: bool = False, verbose: bool = False) -> List[Path]:
	"""Collect cleanup targets and optionally delete them.

	Args:
		root: project root path.
		yes: when True, perform deletion. Otherwise dry-run.
		verbose: verbose output.

	Returns: list of targets (resolved Path objects) discovered.
	"""
	# If the caller passed the default root ('.') we try to infer the
	# repository root relative to this script so imports like
	# `from clean import clean` (when running inside `scripts/`) still
	# operate on the repository root.
	if root == "." or root is None:
		try:
			script_dir = Path(__file__).resolve().parent
			repo_root = script_dir.parent
			rootp = repo_root
		except Exception:
			rootp = Path(root).resolve()
	else:
		rootp = Path(root).resolve()

	targets = set()
	targets |= _collect_from_downloaders(rootp)
	targets |= set(_collect_generic(rootp))

	# Normalize and sort
	targets = sorted(targets, key=lambda p: (p.is_file(), str(p)))

	if not targets:
		if verbose:
			print("No cleanup targets found.")
		return []

	# print("Cleanup targets:")
	# for t in targets:
	# 	print(" -", t)

	if not yes:
		print("Dry-run: no files removed. Pass `yes=True` to delete.")
		return targets

	# Proceed to remove
	for t in targets:
		_remove(t, True, verbose)

	print("Cleanup complete.")


def main(argv=None):
	parser = argparse.ArgumentParser(description="Clean downloaded, build and output files")
	parser.add_argument("-y", "--yes", action="store_true", help="Actually delete files (default: dry-run)")
	parser.add_argument("-v", "--verbose", action="store_true", help="Verbose output")
	parser.add_argument("--root", default=".", help="Project root (default: project root)")
	args = parser.parse_args(argv)

	clean(root=args.root, yes=args.yes, verbose=args.verbose)


if __name__ == "__main__":
	sys.exit(main())

