# Computation Cycle

SlothPU16 uses a five stage computational cycle.
The stages are:

1. Instruction Fetch
1. Instruction Store
1. Decode/Execute
1. Commit
1. PC Update

The current stage is indicated on the 5-wire compute cycle bus.
Each wire indicates a different stage, and only one may be high at a time.
We will now describe what happens during each stage.

> *Instruction Fetch* The PC is connected to A-bus, and memory responds by placing the instruction at that (word-aligned) location onto C-bus.

> *Instruction Store* The instruction on C-bus is stored in the IR.

> *Decode/Execute* The instruction is decoded by the ALU, PC and Register File. Operands (generally GP registers) are connected to A- and B- buses, the destination (generally a GP register) is connected to C-bus, and the appropriate unit (usually the ALU) combines A and B to produce the output on C.

> *Commit* The result currently on C-bus is stored at the destination (usually)

> *PC Update* The Program Counter is incremented (usually) or changed to the branch location

The cycle is broken up like this to avoid timing issues.
For example, the *Instruction Store* could theoretically occur on the falling edge of *Instruction Fetch* (similarly, *Commit* could be on the falling edge of *Decode/Execute*).
However, this would require the instruction to remain on C-bus long enough for the IR to pick it up - before the rising edge of the next stage in the cycle reconfigures connections to the buses.