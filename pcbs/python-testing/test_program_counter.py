import time

import pytest

import bitarray.util

from pi_backplane import _Input, _Output

SLEEP_SECS = 0.1

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

instr_non_pc = [
    "add",
    "sub",
    "compare",
    "nand",
    "xor",
    "barrel",
    "loadb",
    "loadw",
    "storeb",
    "storew",
    "set",
]


def test_non_pc():

    bus_vals = dict(A=189, B=20049, C=40181)

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
    output.set_oe("Reset", False)
    output.send()

    # Reset the PC register
    output.set_reset(True)
    output.send()
    time.sleep(SLEEP_SECS)
    output.set_reset(False)
    output.send()
    time.sleep(SLEEP_SECS)
    output.set_reset(True)
    output.send()

    for k, v in bus_vals.items():
        output.set_bus(k, v)
    output.send()

    expected_pc = 0
    for op in instr_non_pc:
        print("op: ", op)
        # Instruction Fetch -------------------
        output.set_cycle(0)
        output.send()

        input.recv()
        A_bus = input.read_bus("A")
        assert A_bus == expected_pc

        # Instruction Store -------------------
        output.set_cycle(1)

        instr_bus = bitarray.util.zeros(N_BITS, endian="little")
        instr_bus[0:3] = bitarray.util.int2ba(
            instructions[op], endian="little", length=INSTR_BITS
        )
        output.set_bus("Instruction", bitarray.util.ba2int(instr_bus))
        output.send()

        input.recv()
        A_bus = input.read_bus("A")
        assert A_bus == expected_pc  # Should not change

        # Decode/Execute
        output.set_cycle(2)
        output.send()

        input.recv()
        A_bus = input.read_bus("A")
        assert A_bus == 0  # Now disconnected

        # Commit
        output.set_cycle(3)
        output.send()

        input.recv()
        A_bus = input.read_bus("A")
        assert A_bus == 0  # Now disconnected

        # PC Update
        output.set_cycle(4)
        output.send()

        input.recv()
        A_bus = input.read_bus("A")
        assert A_bus == 0  # Now disconnected

        expected_pc += 2
    input.recv()
