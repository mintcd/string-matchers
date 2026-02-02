from math import ceil
from typing import List, Literal

from numpy import uint


class Register:
    """
      Register Simulation
    """
    def __init__(self, val, length: int = 128, access: Literal['left-to-right', 'right-to-left']='right-to-left'):
        # Accept single-character strings as character codes
        self.length = length
        if isinstance(val, str) and len(val) == 1:
            val = ord(val)
        self.value = to_bool_list(val, length=length)
        self.access = access

    def __str__(self):
        res = ""
        n = len(self.value)
        for idx, bit in enumerate(self.value):
            res += '1' if bit else '0'
            # insert a space after every 8 bits, except after the last group
            if (n - 1 - idx) % 8 == 0 and idx != n - 1:
                res += ' '
        return res
    
    def __eq__(self, other: 'Register'):
        return self.value == other.value
    
    def getValue(self, type: Literal['str', 'int']='str') -> str | int:
        """
        Returns the bits in the register as a string of bits or as an integer.
        """
        if type == 'str':
            return ''.join(['1' if b else '0' for b in self.value])
        elif type == 'int':
            int_value = 0
            for bit in self.value:
                int_value = (int_value << 1) | (1 if bit else 0)
            return int_value
        else:
            raise ValueError('Unsupported type for getValue: {}'.format(type))
        
    def setBit(self, bit: bool, byte_pos: int, bit_pos: int):
        pos = byte_pos * 8 + bit_pos
        if pos < 0 or pos >= len(self.value):
            raise ValueError('Bit position out of range')
        if self.access == 'right-to-left':
            self.value[len(self.value) - 1 - pos] = bit
        else:
            self.value[pos] = bit

    def getBit(self, byte_pos: int, bit_pos: int) -> bool:
        pos = byte_pos * 8 + bit_pos
        if pos < 0 or pos >= len(self.value):
            raise ValueError('Bit position out of range')
        if self.access == 'right-to-left':
            return self.value[len(self.value) - 1 - pos]
        else:
            return self.value[pos]

    
    def __or__(self, other: 'Register'):   
        assert(other.length == len(self.value)), 'Registers must be of the same length for OR operation'     

        result = Register(0, length=len(self.value), access=self.access)
        result.value = [a or b for a, b in zip(self.value, other.value)]
        return result
    
    def __and__(self, other: 'Register'):
        assert(other.length == len(self.value)), 'Registers must be of the same length for OR operation'     
        
        result = Register(0, length=len(self.value), access=self.access)
        result.value = [a and b for a, b in zip(self.value, other.value)]
        return result
    
    def __invert__(self):
        result = Register(0, length=len(self.value), access=self.access)
        result.value = [not b for b in self.value]
        return result
    
    def __lshift__(self, count: int):
        if count < 0:
            raise ValueError('Negative shift count not supported')
        result = Register(0, length=len(self.value), access=self.access)
        if count >= len(self.value):
            return result
        result.value = self.value[count:] + [False] * count
        return result
    
    def __rshift__(self, count: int):
        if count < 0:
            raise ValueError('Negative shift count not supported')
        result = Register(0, length=len(self.value), access=self.access)
        if count >= len(self.value):
            return result
        result.value = [False] * count + self.value[:-count]
        return result
    
    def __add__(self, value: uint):
        return Register(self.getValue(type='int')+value, length=len(self.value), access=self.access)
    
    def __sub__(self, value: uint):
        return Register(self.getValue(type='int')-value, length=len(self.value), access=self.access)



def to_bool_list(value, length: int = 128) -> List[bool]:
    """
    Convert value to a list of booleans of specified length (simulating a register).
    If the value is shorter than length, it is zero-padded on the left (most-significant side).
    If the value is longer than length, it is truncated to the least-significant bits.

    Parameters:
    - value (int, str, bytes)
    - length (int): Number of bits in the output list.
    Returns: 
    - List[bool]: List of booleans representing the bits.
    """

    nbytes = ceil(length / 8)

    if isinstance(value, int):
        raw = int(value) & ((1 << (nbytes * 8)) - 1)
        b = raw.to_bytes(nbytes, 'big')
    elif isinstance(value, (bytes, bytearray)):
        vb = bytes(value)
        if len(vb) < nbytes:
            pad = b'\x00' * (nbytes - len(vb))
            b = pad + vb
        else:
            b = vb[-nbytes:]
    elif isinstance(value, str):
        s = value.strip()
        if s.startswith('0x'):
            s = s[2:]
        if len(s) == 0:
            b = b'\x00' * nbytes
        else:
            # ensure even length
            if len(s) % 2:
                s = '0' + s
            vb = bytes.fromhex(s)
            if len(vb) < nbytes:
                pad = b'\x00' * (nbytes - len(vb))
                b = pad + vb
            else:
                b = vb[-nbytes:]
    else:
        # Assume iterable of bits
        try:
            it = list(value)
        except Exception:
            raise TypeError('Unsupported value type for to_bool_list')

        bits = [bool(x) for x in it]
        if len(bits) >= length:
            # keep least-significant (right-most) bits
            return bits[-length:]
        # pad on the left (most-significant side)
        return [False] * (length - len(bits)) + bits

    # Convert bytes to bit list MSB-first
    bits: List[bool] = []
    for byte in b:
        for i in range(7, -1, -1):
            bits.append(bool((byte >> i) & 1))

    # bits may be longer than requested (when length not multiple of 8)
    if len(bits) > length:
        # keep least-significant (right-most) `length` bits
        return bits[-length:]
    if len(bits) < length:
        return [False] * (length - len(bits)) + bits
    return bits

