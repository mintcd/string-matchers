# Quick check: do any patterns appear literally in the first ruleset line?
from pathlib import Path
pfile = Path('dataset/100_short_patterns.txt')
rfile = Path('dataset/rulesets.txt')

pats = [l.strip() for l in pfile.read_text(encoding='utf-8').splitlines() if l.strip() and not l.strip().startswith('#')]
first = rfile.open(encoding='utf-8').readline()

found_in_first = [p for p in pats if p in first]
print('patterns_loaded=', len(pats))
print('first_ruleset_len=', len(first))
print('matches_in_first=', len(found_in_first))
print('sample_matches_in_first=', found_in_first[:20])

# Scan until first match anywhere (stop early)
any_match_anywhere = False
for idx,line in enumerate(rfile.open(encoding='utf-8')):
    for p in pats:
        if p and p in line:
            print('found at ruleset_index=', idx, 'pattern=', p)
            any_match_anywhere = True
            break
    if any_match_anywhere:
        break
print('any_match_anywhere=', any_match_anywhere)
