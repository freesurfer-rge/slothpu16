# SlothPU16 PCBs

This directory contains the KiCAD files which constitute SlothPU16.
They do rely on [my KiCAD components library](https://github.com/freesurfer-rge/kicad-components), and [one board](https://github.com/freesurfer-rge/slothpu/tree/main/pcbs/Tester) from the original SlothPU.

## General Description

SlothPU16 consists of five modules connected via a backplane:

- The Arithmetic Logic Unit (ALU)
- The Register File
- The Instruction Register
- The Program Counter
- The Pi Backplane Connector

The modules connect to the backplane (and backplane units connect to each other) with a common bus made from two 2x20 pin headers.
With the exception of the Pi Backplane Connector, each of these modules consists of a *carrier* board, which accepts daughter boards via edge connectors.
For testing the daughter boards, *connector* PCBs are provided, which allow each to be tested via the [tester board from the original SlothPU](https://github.com/freesurfer-rge/slothpu/tree/main/pcbs/Tester).
The carrier boards which constitute an entire functional module can also be tested in isolation by use of the Pi Backplane connector.

## The Common Bus

The common bus consists of two 2x20 pin headers, offering a total of 80 potential connections.
Not all of the pins are used, but the bus carries:

- The 16-bit A, B and C operand buses
- The 16-bit instruction bus
- Clock and Reset lines
- Signal lines for the individual clock cycles (Instruction Read, Instruction Store, Decode/Execute, Commit, PC Update)

