import pytest


import bitarray.util

from pi_backplane import _Input, _Output


N_BITS = 16
INSTR_BITS = 4


instructions = {
    "add": 0,
    "sub": 1,
    "compare": 4,
    "nand": 5,
    "xor": 6,
    "barrel": 7,
    "loadb": 8,
    "loadw": 9,
    "storeb": 10,
    "storew": 11,
    "loadpc": 12,
    "branchzero": 13,
    "halt": 14,
    "set": 15,
}


def test_smoke():
    output = _Output()
    input = _Input()

    # Set Pi outputs to high impedance
    # on A and C buses
    output.set_oe("A", True)
    output.set_oe("C", True)

    # Other buses we will write from the Pi
    output.set_oe("B", False)
    output.set_oe("Instruction", False)
    output.set_oe("Cycle", False)

    output.set_cycle(1)

    instr_bus = bitarray.util.zeros(N_BITS, endian="little")
    # Actual instruction is the first four bits

    op = "branchzero"

    instr_bus[0:3] = bitarray.util.int2ba(
        instructions[op], endian="little", length=INSTR_BITS
    )

    output.set_bus("B", 32768)
    output.set_bus("Instruction", bitarray.util.ba2int(instr_bus))
    output.send()
