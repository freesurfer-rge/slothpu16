import pytest

import bitarray.util

from constants import N_BITS, INSTR_BITS, REG_BITS, INSTRUCTIONS
from pi_backplane import _Input, _Output


N_REGISTERS = 16


@pytest.mark.parametrize("r_C", range(N_REGISTERS))
@pytest.mark.parametrize("target_val", [0, 16385, (2 ** N_BITS) - 1])
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
        INSTRUCTIONS[op], endian="little", length=INSTR_BITS
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


def get_instruction(opcode: str, r_A: int, r_B: int, r_C: int) -> bitarray.bitarray:
    instr_bus = bitarray.util.zeros(N_BITS, endian="little")

    # Opcode is first four bits
    instr_bus[0:3] = bitarray.util.int2ba(
        INSTRUCTIONS[opcode], endian="little", length=INSTR_BITS
    )

    # r_A set by next four bits
    instr_bus[4:7] = bitarray.util.int2ba(r_A, endian="little", length=INSTR_BITS)

    # And then r_B
    instr_bus[8:11] = bitarray.util.int2ba(r_B, endian="little", length=INSTR_BITS)

    # r_C set by the final bits of the instruction
    instr_bus[12:15] = bitarray.util.int2ba(r_C, endian="little", length=INSTR_BITS)

    return instr_bus


@pytest.mark.parametrize("r_C", range(N_REGISTERS))
@pytest.mark.parametrize(
    "target_val", [0, 144, 1037, 8195, 20125, 40008, (2 ** N_BITS) - 1]
)
@pytest.mark.parametrize("op", list(INSTRUCTIONS.keys()))
def test_compute_cycle(r_C, target_val, op):
    output = _Output()
    input = _Input()

    # We will read from A and B
    output.set_oe("A", True)
    output.set_oe("B", True)

    # We will write to Instruction, Cycle and C
    output.set_oe("Instruction", False)
    output.set_oe("Cycle", False)
    output.set_oe("C", False)

    # Set up the registers
    for r_i in range(N_REGISTERS):
        # Anything except loadb, loadw or branchzero
        setup_op = "loadpc"

        instr_bus = get_instruction(setup_op, r_i, r_i, r_i)
        output.set_bus("C", 2 ** r_i)
        output.set_bus("Instruction", bitarray.util.ba2int(instr_bus))
        output.send()

        for cyc in [3, 4]:
            output.set_cycle(cyc)
            output.send()

    # Set C to be target_val
    output.set_bus("C", target_val)
    output.send()

    # For IFETCH and ISTORE, bus A and B should be zero
    for cyc in [0, 1]:
        for r_i in range(N_REGISTERS):
            instr_bus = get_instruction(op, r_i, r_i, r_C)
            output.set_bus("Instruction", bitarray.util.ba2int(instr_bus))
            output.set_cycle(cyc)
            output.send()

            input.recv()
            assert input.read_bus("A") == 0
            assert input.read_bus("B") == 0

    # FOR EXECUTE, bus A and B should read 2**i
    cyc = 2
    for r_A in range(N_REGISTERS):
        for r_B in range(N_REGISTERS):
            instr_bus = get_instruction(op, r_A, r_B, r_C)
            output.set_bus("Instruction", bitarray.util.ba2int(instr_bus))
            output.set_cycle(cyc)
            output.send()

            input.recv()
            assert input.read_bus("A") == 2 ** r_A
            assert input.read_bus("B") == 2 ** r_B

    # On COMMIT, A & B should start picking up target_value
    # except on  storeb, storew and branchzero
    # This should be maintained for PCUPDATE
    expected_C = target_val
    if op in ["storeb", "storew", "branchzero"]:
        expected_C = 2 ** r_C
    for cyc in [3, 4]:
        for r_A in range(N_REGISTERS):
            for r_B in range(N_REGISTERS):
                instr_bus = get_instruction(op, r_A, r_B, r_C)
                output.set_bus("Instruction", bitarray.util.ba2int(instr_bus))
                output.set_cycle(cyc)
                output.send()

                input.recv()
                if r_A == r_C:
                    assert input.read_bus("A") == expected_C
                else:
                    assert input.read_bus("A") == 2 ** r_A
                if r_B == r_C:
                    assert input.read_bus("B") == expected_C
                else:
                    assert input.read_bus("B") == 2 ** r_B
    input.recv()
