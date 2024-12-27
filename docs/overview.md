# Overview

The goal is to create a functional computer from (mainly) 7400-series logic.
This is to be a pedagogical exercise, with ample provision of blinkenlights.
Speed is not a primary concern.
The basic architectural parameters are:

- Load/Store design
- 16-bit instructions, addressing and computation
- Minimal specialised registers

This project is based on an [earlier attempt](https://github.com/freesurfer-rge/slothpu/), which tried to keep to an 8-bit design, but ended up an unwieldly hybrid.
That experience indicated that 16-bit was the minimum for a clean and consistent design.
Two main considerations lead to this.
Firstly, the 256 'addressable locations' of a fully 8-bit machine aren't really enough to contain an interesting program and its data (recall that the 'classic' 6502 machines generally had 32 kiB of RAM, indicating that 16-bit addressing was available).
Secondly, a load/store design with minimal specialised registers (such as a designated 'result' register) is going to require three registers for most instructions - two operands and a result.
Three registers, each identified by at least two bits will consume six bits of an 8-bit instruction, only permitting four instructions.
This is _adequate_ for creating a computer, but extremely limiting.