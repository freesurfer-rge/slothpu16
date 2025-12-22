# Python Scripts

This directory contains a mix of Python scripts (unfortunately... this should be fixed).
There are two broad categories:
- Tests for PCBs
- The driver program for running SlothPU16 for real (along with some sample programs)

## Testing

The test programs are not meant to be run as a 'whole directory' by `pytest`, but instead run individually when the appropriate board is connected.
Furthermore, whether the individual daughter cards are being tested via their connectors (and the Tester board with its *different* twin 2x20 pin headers) or entire modules, it is probably best to *run the appropriate test file* once **before connecting the target board** (the test run can be cancelled once tests have actuall started running).
This is to ensure that the appropriate outputs have been set to high impedance, to avoid the problem of connecting two CMOS outputs together.

## Running SlothPU16

To make sure that two CMOS outputs get connected together, run the [`prepare_connect.py`](./prepare_connect.py
) script first, to put all of the output shift registers into high impedance mode.
Once this is done, the backplane can be connected.
To run a program, use the [`run_slothpu16.py`](./run_slothpu16.py) script, providing one of the [sample programs](./programs/) as an input file.