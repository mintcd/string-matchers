from typing import Dict, List
from .Register import Register


class CPU:
    """Simple CPU abstraction that holds counters and primitive
    operations used by the Python FDR implementation.
    """
    def __init__(self):
        self.counters = {
            'andn': 0,
            'shifts': 0,
            'ors': 0,
            'lshifts': 0,
            'rshifts': 0
        }

    def reset(self):
        for k in self.counters:
            self.counters[k] = 0

    def andn(self, a: Register, b: Register) -> Register:
        self.counters['andn'] += 1
        return ~a & b

    def lshift(self, val: Register, count: int) -> Register:
        self.counters['lshifts'] += 1
        return val << count

    def rshift(self, val: Register, count: int) -> Register:
        self.counters['rshifts'] += 1
        return val >> count

    def or128(self, a: Register, b: Register) -> Register:
        self.counters['ors'] += 1
        return a | b
    
    def load128(self, val: int) -> Register:
        return Register(val, length=128)

