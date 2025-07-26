# Program Counter

There are a variety of functions here.
Some quick notes...

During the *Instruction Fetch* and *Instruction Store* cycles, the PC Register itself should be connected to A bus.
The memory subsystem should error if the lowest bit of the PC Register is not zero (i.e. the instruction is not two-byte aligned).

The PC Register is clocked on the *PC Update* cycle.

If the instruction is `LOADPC` then the PC Register should be connected to C bus during the *Decode/Execute*, *Commit*, and *PC Update* cycles.

The PC Register should always be connected to the inputs of the incrementer.
However, the incrementer is not the only possible input to the PC Register.
For the *Decode/Execute*, *Commit*, and *PC Update* cycles, if the instruction is `BRANCHZERO` _and_ all bits of B bus are zero, then A bus should be connected to the input of the PC Register.

The '2' line of the incrementer should be set based on the `HALT` instruction.
It should be high unless the instruction is `HALT`; since the decoder will be active-low, this is very easy to achieve.