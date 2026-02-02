# Multi-string shift-or matching

Assume that we access the positions rightmost, both for characters in a pattern, and bits and bytes in a register.

Each character is encoded as **1** byte.
A super-character is of from 9 to 15 bits (taking lower bits of the next character).
Super-character masks are of **8** bytes.
State masks are of **16** bytes.
There are **8** buckets.
Patterns have length at most **8**.

The $8p+b$ bit in the mask of a super-character $c$ is set to 0 if either

1. There is a pattern in the $b$-th bucket that has $c$ at position $p$.
2. The $b$-bucket has patterns of length less than $p+1$ (padding byte).