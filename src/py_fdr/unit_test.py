from .FDRCompiler import FDRCompiler
from .FDR import FDR

patterns = [l.rstrip('\n') for l in open('dataset/100_short_patterns.txt') if l.strip() and not l.startswith('#')]
compiler = FDRCompiler(patterns)
compiler.compile(strategy=1)
engine = FDR(compiler)

with open('dataset/rulesets.txt', 'r', encoding='utf-8') as fh:
    for idx, raw in enumerate(fh):
        if idx == 0:
          line = raw.rstrip('\n')

          try:
              engine.exec(line, log_file=f'logs/bad_ruleset_{idx}.log')
          except Exception as e:
              print('FAILED ruleset index:', idx)
              print('RULESET LINE:', line)
              print('EXCEPTION:', repr(e))
              raise