<!-- Taken from Hyperscan: A Fast Multi-pattern Regex Matcher for Modern CPUs -->

```python
function MATCH
  # FDREngineDescription::getSchemeWidth and fdr_engine_description.cpp:1-80
  n = number of bits of a super-character.  
  # fdr.c:getInitState:60-110 (uses fdr->start)
  R = the mask at the beginning  

  # fdr.c:700-780
  for each 8 bytes V of the input
    for i = 0..7
      # fdr.c:150-220:get_conf_stride_ (reachX and andn)
      superChar = V[8*i:8*i+n-1]
      
      # fdr.c:150-220:load_m128_from_u64a(ft + reachX)
      M[i] = shiftOrMask[superChar]

      # fdr.c:150-220:lshiftbyte_m128 (we shift i bytes)
      S[i] = M[i] << i

    for i = 0..7
      # fdr.c:150-220:or128
      R = R | S[i]

    # fdr.c:330-380:do_confirm_fdr:findAndClearLSB_64
    for zero bit b in lower 8 bytes of R
      # fdr.c:347:findAndClearLSB_64
      i = the bit position of b

      # fdr.c:348
      j = the byte position of b

      # fdr_confirm.h:1-120:LitInfo::size
      l = the length of strings in bucket i

      # window loaded via `unaligned_load_u64a(...)` and confirmation via `confWithBit(...)` which computes `CONF_HASH_CALL` in `fdr_confirm_runtime.h:1-80`
      h = HASH(V[j-l+1:j]) # In our simplified version, we do naive matching right away 
      if h is valid
        # reported by calling the callback `a->cb(...)` inside `confWithBit(...)` on success in `fdr_confirm_runtime.h:80-120`
        exact match  
      
      R := R >> 8
```

**Notes**
1. Each character has 8 bits, according to ASCII
2. Registers have 128 bits
3. Patterns are no longer than 8 bits. So that when we shift the text by up to 7 bits, information is not lost.
4. FDR handles 8 bytes of input at a time
5. Features excluded to the actual implementation
  - Flood detection
  - Stride (only OR at certain positions)
  - The FDR engine is laid out in bytecode in order: header (`fdr_base`), table (`tab` at compile time and `ft` at run time). This leverages more SIMD.