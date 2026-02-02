from typing import Dict, List
from .Register import Register
from .utils import LOG

"""
  Assigns patterns to buckets and builds masks.
"""
class FDRCompiler:
    def __init__(self, patterns):
        """Initialize the FDR compiler with patterns.
          Args:
              patterns (List[str]): List of patterns to compile.
        """
        self.patterns = patterns

    def compile(self, domain_bits=9, strategy=1, log_file: str | None = None):
        """ 
          Compile the patterns into buckets and masks.
            domain_bits (int): Number of bits for the domain.
            strategy (int): Strategy for pattern assignment.
              1 - by length (default)
              2 - all patterns have the same length, assigned uniformly
        """
        self.domain_bits = domain_bits
        if strategy == 1:
          self.buckets = assignPatternsToBucketsByLength(self.patterns)
        elif strategy == 2:
          self.buckets = assignPatternsToBucketsUniformly(self.patterns)
        else:
          raise ValueError('Unsupported strategy: {}'.format(strategy))
        self.masks = buildMasks(self.buckets, self.domain_bits, log_file=log_file)

        LOG("Compiled FDR with {} patterns into buckets and masks".format(len(self.patterns)), log_file=log_file)


def assignPatternsToBucketsByLength(patterns):
    buckets: List[List[str]] = [[] for _ in range(8)]
    for pat in patterns:
        assert 1 <= len(pat) <= 8, 'Pattern length must be between 1 and 8'
        buckets[len(pat)-1].append(pat)
    return buckets

def assignPatternsToBucketsUniformly(patterns):
    buckets: List[List[str]] = [[] for _ in range(8)]
    for idx, pat in enumerate(patterns):
        buckets[idx % 8].append(pat)
    return buckets

def buildMasks(buckets, domain_bits, log_file: str | None = None):
    masks : Dict[int, Register] = {}
    for c in range(0, 2**domain_bits):
      # Set the lower 64 bits to all ones, upper 64 bits to zeros so that the upper 64 bits of st-mask are not affected
      masks[Register(c, domain_bits).getValue()] = Register(-1, 128) >> 64

      """
      If the byte position of a sh-mask exceeds the longest pattern of a certain bucket (called ‘padding byte’), we encode the bucket id in the padding byte. This ensures matching correctness by carrying a match at a lower input byte along in the shift process.

      """
    for b in range(8):
       if len(buckets[b]) == 0:
         continue
       
       pat_length = len(buckets[b][0])

       for c in masks.keys():
          # Set the bit of the positions larger than the pattern length
          for p in range(pat_length, 8):
            masks[c].setBit(False, p, b)

    # Set bits according to super-characters in patterns
    for b in range(8):
      for pat in buckets[b]:
        for pos in range(len(pat)):
            char_pos_from_right = len(pat) - pos - 1
            super_char = getSuperChar(pat, pos, domain_bits)
            masks[super_char].setBit(False, char_pos_from_right, b)
            LOG(f"Pattern '{pat}', char '{pat[pos]}', super-char '{super_char}', pos '{char_pos_from_right}', bucket '{b}', bit set {char_pos_from_right}", log_file=log_file)

    return masks
    
def getSuperChar(text: str, pos: int, domain_bits: int) -> str:
    """
    Get the super-character for a given character position in a pattern.

       Args:
           pat (str): The pattern string.
           pos (int): The position of the character in the pattern.
           domain_bits (int): Number of bits for the domain.
       Returns:
           str: The super-character.
    """

    if pos < 0 or pos >= len(text):
      raise ValueError('Position out of bounds in getSuperChar')

    start = ord(text[pos])
    end = ord(text[pos+1]) if pos + 1 < len(text) else 0

    raw = (start | (end << 8)) & ((1 << domain_bits) - 1)

    return Register(raw, domain_bits).getValue()