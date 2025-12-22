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
With the exception of the Pi Backplane Connector, each of these modules consists of a *carrier* board, which accepts daughter boards via 44-contact edge connectors.
For testing the daughter boards, *connector* PCBs are provided, which allow each to be tested via the [tester board from the original SlothPU](https://github.com/freesurfer-rge/slothpu/tree/main/pcbs/Tester).
The carrier boards which constitute an entire functional module can also be tested in isolation by use of the Pi Backplane connector.

## The Common Bus

The common bus consists of two 2x20 pin headers, offering a total of 80 potential connections.
Not all of the pins are used, but the bus carries:

- The 16-bit A, B and C operand buses
- The 16-bit instruction bus
- Clock and Reset lines
- Signal lines for the individual clock cycles (Instruction Read, Instruction Store, Decode/Execute, Commit, PC Update)

## The Arithmetic Logic Unit

The ALU consists of its [carrier board](./ALU%20Carrier/) and the following daughter cards:

- [Barrel shifter](./Barrel%20Shifter/)
- [NAND/XOR](./NAND%20XOR/)
- [Comparator](./Comparator/)
- [Adder/Subtractor](./Adder%20Subtractor/)

With the exception of the comparator, two of each of these cards are required.
For testing purposes, the barrel shifter has its [own connector](./Barrel%20Shifter%20Connector/), while the other three share a [common connector](./ALU%20Test%20Connector/).
Note that *only one* of the daughter cards should plugged into the common ALU test connector at a time - no effort is made to prevent outputs from different daughter cards being connected.

## The Register File

The [Register File Carrier](./Register%20File%20Carrier/) accepts four identical copies of the [Register File](./Register%20File/).
Each Register file contains eight 8-bit registers, with one write port (from the C bus) and two read ports (the A & B buses).
A [connector](./Register%20File%20Connector/) allows the individual Register Files to be tested.

## The Instruction Register