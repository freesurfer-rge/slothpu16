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

## Arithmetic Logic Unit

The ALU is only active on the Decode/Execute and Commit stages of the computational cycle.
During these two stages, the ALU will take its inputs from the A & B buses, and place the appropriate output on the C bus.
The instructions are:

- `0000` Add (A+B)
- `1000` Subtract  (A-B)
- `0010` Compare (three bits of C will indicate, A<B, A=B or A>B)
- `1010` NAND (A NAND B)
- `0110` XOR (A XOR B)
- `1110` Barrel shift (shift A by n bits, where n is the bottom four bits of B)

Note that in all cases i<sub>3</sub> = 0.

## Non-ALU instructions

The following instructions can be active on the Decode/Execute, Commit and PC Update stages of the computational cycle.
Inputs will still be from A & B buses except for the Set instruction, but the output may be written to C bus, memory, or the program counter

- `0001` Load Byte given by address on bus A, putting the result (with high byte 0) on bus C
- `1001` Load 2-Byte word given by address on bus A (must be 2-byte aligned), putting result on bus C
- `0101` (*) Store low byte on bus B to the address on bus A.
- `1101` (*) Store bus B to the address on bus A
- `0011` Place program counter on bus C (A & B ignored)
- `1011` (*) If value on bus B is zero, PC will update to value on bus A (which must be two-byte aligned). Otherwise PC will update as normal
- `0111` Halt. PC Update inhibited. Buses A, B and C ignored
- `1111` Set constant. The low byte of bus C is set to the value of the 8 bits which usually identify the A and B buses. The A & B buses

The instructions marked (*) have to suppress the update of the Register File. In a similar vein, the 'Set' instruction must suppress the output on buses A & B from the Register File