# Instructions

All instructions are one word (16-bits) long, and are word-aligned.
SlothPU16 is little-endian.

## General Format

In memory, instructions are laid out like:

```
-0--------8--------
|iiiiaaaa|bbbbcccc|
-------------------
Byte n    Byte n+1
```
where `i` denotes the actual instruction, `a` and `b` identify the operand registers (usually) and `c` identifies the result register (usually).
The individual bits are numbered 0-3 from low memory.

## List of Instructions

* ALU (i<sub>3</sub> = 0)
    - Add
    - Subtract
    - Compare
    - NAND
    - XOR
    - Barrel Shift
* Non-ALU (i<sub>3</sub> = 1)
    - Memory (i<sub>2</sub> = 0)
        - Load Byte
        - Load Word
        - Store Byte
        - Store Word
    - PC
        - Load PC
        - Branch if Zero
        - Halt
    - Other
        - Set
