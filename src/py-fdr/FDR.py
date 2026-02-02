# A minimal implementation to ensure correctness. No CPU yet.

from typing import List
from Register import Register
from FDRCompiler import FDRCompiler, getSuperChar
from utils import LOG

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