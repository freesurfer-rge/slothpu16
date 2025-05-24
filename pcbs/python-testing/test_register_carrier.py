import pytest

import bitarray.util

from pi_backplane import _Input, _Output


N_BITS = 16
N_REGISTERS = 16
INSTR_BITS = 4
REG_BITS = 4

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


@pytest.mark.parametrize("r_C", range(N_REGISTERS))
@pytest.mark.parametrize("target_val", [0, (2 ** N_BITS) - 1])
def test_smoke(r_C, target_val):
    output = _Output()
    input = _Input()

    # We will read from A and B
    output.set_oe("A", True)
    output.set_oe("B", True)

    # We will write to Instruction, Cycle and C
    output.set_oe("Instruction", False)
    output.set_oe("Cycle", False)
    output.set_oe("C", False)

    # Anything except loadb, loadw or branchzero
    op = "loadpc"

    instr_bus = bitarray.util.zeros(N_BITS, endian="little")
    # Actual instruction is the first four bits

    instr_bus[0:3] = bitarray.util.int2ba(
        instructions[op], endian="little", length=INSTR_BITS
    )
    reg_bits = bitarray.util.int2ba(r_C, endian="little", length=INSTR_BITS)

    # r_A set by next four bits
    instr_bus[4:7] = reg_bits

    # And then r_B
    instr_bus[8:11] = reg_bits

    # r_C set by the final bits of the instruction
    instr_bus[12:15] = reg_bits

    print("instr_bus=", instr_bus)

    # Set things up
    output.set_bus("C", target_val)
    output.set_bus("Instruction", bitarray.util.ba2int(instr_bus))
    output.send()

    # Do a simple sweep
    # This is not the full required logic
    for cyc in range(5):
        output.set_cycle(cyc)
        output.send()

    # We should now be at the end of the compute cycle (PCUPDATE)
    # Try reading from buses A and B
    input.recv()

    assert input.read_bus("A") == target_val
    assert input.read_bus("B") == target_val
