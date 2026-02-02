# A minimal implementation to ensure correctness. No CPU yet.
import os
import time

from typing import List
from .Register import Register
from .FDRCompiler import FDRCompiler, getSuperChar
from .utils import LOG
import multiprocessing

ITER_BYTES = 8

class FDR:
  def __init__(self, fdr_compiler: FDRCompiler):
    """Initialize the FDR engine with compiled patterns.
      Args:
          fdr_compiler (FDRCompiler): Compiled FDR patterns and masks.
    """
    self.patterns = fdr_compiler.patterns
    self.pattern_by_index = {pat: idx for idx, pat in enumerate(self.patterns)}
    self.masks = fdr_compiler.masks
    self.domain_bits = fdr_compiler.domain_bits
    self.buckets = fdr_compiler.buckets

  def exec(self, text: str, log_file: str | None = None) -> List[int]:
    # Clear the log file
    if log_file:
      # Use LOG to create parent directory and touch the file safely
      LOG("", log_file=log_file)

    matches = []

    st_mask = self.initState(log_file=log_file)

    """
      In actual matching, FDR handles 8 bytes of input at a time.
    """
    step = 0
    for i in range(0, len(text), ITER_BYTES):
      step+=1
      chunk_len = min(ITER_BYTES, len(text) - i)
      LOG(f"--- Step {step}: Processing text positions {i} to {i+chunk_len-1} ---", log_file=log_file)


      for j in range(chunk_len):
        super_char = getSuperChar(text, i + j, self.domain_bits)

        super_char_mask = self.masks.get(super_char)
        LOG(f"Scanning {text[i+j]}, superchar {super_char}, masks\n", super_char_mask, log_file=log_file, indent=2)

        # We cannot ignore the case that this may be the end of a pattern
        null_super_char_mask = self.masks.get(getSuperChar(text[i+j], 0, self.domain_bits))
        super_char_mask = super_char_mask & null_super_char_mask
        LOG(f"Anded mask:\n", super_char_mask, log_file=log_file, indent=2)


        st_mask = st_mask | (super_char_mask << (j * 8))

        LOG("Updated st-mask\n", st_mask, log_file=log_file, indent=2)

      # Report matches in lower 64 bits
      for b in range(8):
        for p in range(0, chunk_len):
          if st_mask.getBit(p, b) == False:
            match_pos = p + i
            LOG(f"Found a match ending at {match_pos} for bucket {b}", log_file=log_file, indent=2)

            # Do exact matching
            match_pos_start = match_pos + 1 - len(self.buckets[b][0])
            assert match_pos_start >= 0, f"Match position {match_pos_start} out of bounds"
            sub_text = text[match_pos_start : match_pos + 1]
            for pat in self.buckets[b]:
              if sub_text == pat:
                LOG(f"Found a match starting at {match_pos_start} for '{pat}'", log_file=log_file, indent=2)
                matches.append((match_pos_start, self.pattern_by_index[pat]))
      

      st_mask = st_mask >> 64

    return matches


  def initState(self, log_file: str | None = None):
    st_mask = Register(0, 128)

    """
    The st-mask is initially 0 except for the byte positions smaller than the shortest pattern. This avoids a false-positive match at a position smaller than the shortest pattern.
    """
    
    for b in range(8):
      if len(self.buckets[b]) == 0:
        continue
      min_pat_len = len(self.buckets[b][0])
      for p in range(0, min_pat_len-1):
        st_mask.setBit(True, p, b)
    LOG("Initial st_mask:\n", st_mask, log_file=log_file)
    return st_mask
  

# Multiprocessing globals / helpers
_global_fdr_engine = None

def _worker_init(patterns):
  """Initializer for worker processes: compile patterns and create an FDR engine."""
  global _global_fdr_engine
  fdr_compiler = FDRCompiler(patterns)
  fdr_compiler.compile()
  _global_fdr_engine = FDR(fdr_compiler)

def _worker_exec(item):
  """Worker execution: run the global FDR engine on a single (idx, line).
  Returns a dict matching the existing results structure.
  """
  idx, line = item
  start = time.perf_counter()
  matches = _global_fdr_engine.exec(line)
  end = time.perf_counter()

  time_ms = (end - start) * 1000.0
  matches = matches or []
  matches.sort()
  return {'ruleset_index': idx, 'matches': matches, 'time_ms': time_ms, 'matched_count': len(matches)}
  

def fdr_match(rulesets_file: str, patterns_file: str, output_file: str, max_patterns: int = 0, max_tests: int = 0):
  # Load patterns from the patterns file (skip blank lines and comments)
  patterns = []
  with open(patterns_file, 'r', encoding='utf-8') as pf:
    for idx, raw in enumerate(pf):
      if max_patterns and idx >= max_patterns:
        break
      line = raw.rstrip('\n')
      if not line or line.startswith('#'):
        continue
      patterns.append(line)

  fdr_compiler = FDRCompiler(patterns)
  fdr_compiler.compile()

  results = []
  processed = 0
  total_matches = 0

  # Read and collect ruleset lines first (preserve file index)
  items = []
  with open(rulesets_file, 'r', encoding='utf-8') as rf:
    for idx, raw in enumerate(rf):
      line = raw.rstrip('\n')
      if not line or line.startswith('#'):
        continue
      items.append((idx, line))
      if max_tests and len(items) >= max_tests:
        break

  print(f"Detected {multiprocessing.cpu_count()} CPU cores. Run with {min(int(multiprocessing.cpu_count()/2), len(items))} workers.")

  if items:
    # Start a pool of workers (one per CPU or fewer if fewer items)
    num_workers = min(int(multiprocessing.cpu_count()/2), len(items))
    ctx = multiprocessing.get_context('spawn') if os.name == 'nt' else multiprocessing.get_context()
    with ctx.Pool(processes=num_workers, initializer=_worker_init, initargs=(patterns,)) as pool:
      for res in pool.imap_unordered(_worker_exec, items):
        results.append({'ruleset_index': res['ruleset_index'], 'matches': res['matches'], 'time_ms': res['time_ms']})
        processed += 1
        total_matches += res.get('matched_count', 0)
        if processed % 100 == 0:
          print(f"  Scanned {processed} rulesets...")

  # Ensure results are ordered by ruleset_index like before
  results.sort(key=lambda r: r['ruleset_index'])

  # Write outputs
  os.makedirs(output_file, exist_ok=True)

  metadata_path = os.path.join(output_file, 'metadata.txt')
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

  results_path = os.path.join(output_file, 'results.txt')
  with open(results_path, 'w', encoding='utf-8') as rf_out:
    rf_out.write('ruleset_index\tmatches\ttime_ms\n')
    for r in results:
      rf_out.write(str(r['ruleset_index']))
      rf_out.write('\t')
      rf_out.write('[')
      first = True
      for m in r['matches']:
        if not first:
          rf_out.write(',')
        rf_out.write(f"({m[0]},{m[1]})")
        first = False
      rf_out.write(']')
      rf_out.write('\t')
      rf_out.write(f"{r['time_ms']:.6f}\n")

  print(f"  Written: {metadata_path}")
  print(f"  Written: {results_path} ({len(results)} rows)")
  