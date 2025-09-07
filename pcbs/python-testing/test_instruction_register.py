import time

import pytest

import bitarray.util

from constants import N_BITS, INSTR_BITS, INSTRUCTIONS, REG_BITS
from pi_backplane import _Input, _Output
from utils import get_instruction

SLEEP_SECS = 0.03


def prepare_instruction_register(input: _Input, output: _Output):
    # Set Pi outputs to high impedance on
    # Instruction and C buses (since that's where IR writes results)
    # Also A bus, which should be disconnected from IR
    output.set_oe("Instruction", True)
    output.set_oe("C", True)
    output.set_oe("A", True)

    # IR reads from other buses
    output.set_oe("B", False)
    output.set_oe("Cycle", False)
    output.set_oe("Reset", False)
    output.send()

    # Send reset
    output.set_reset(True)
    output.send()
    time.sleep(SLEEP_SECS)
    output.set_reset(False)
    output.send()
    time.sleep(SLEEP_SECS)
    output.set_reset(True)
    output.send()
    # This last is important, since it allows the
    # RC networks in the RwR reset logic to return
    # to 'base' state
    time.sleep(SLEEP_SECS)


@pytest.mark.parametrize("op", INSTRUCTIONS.keys())
@pytest.mark.parametrize("rA", range(2 ** REG_BITS))
@pytest.mark.parametrize("rB", [0, 7, 9, 15])
@pytest.mark.parametrize("rC", [0, 11])
def test_instruction_write(op: str, rA: int, rB: int, rC: int):
    output = _Output()
    input = _Input()

    prepare_instruction_register(input, output)

    instr = get_instruction(op, rA, rB, rC)

    # Set the cycle and instruction
    output.set_cycle(0)
    output.set_bus("B", bitarray.util.ba2int(instr))
    output.send()

    # Check outputs
    input.recv()
    assert input.read_bus("A") == 0
    assert input.read_bus("Instruction") == 0
    assert input.read_bus("C") == 0

    # Now advance the clock cycle
    output.set_cycle(1)
    output.send()

    # Check outputs again
    input.recv()
    assert input.read_bus("A") == 0
    assert input.read_bus("Instruction") == bitarray.util.ba2int(instr)
    assert input.read_bus("C") == 0

    # Advance through remaining cycles
    for cyc in range(2, 5):
        output.set_cycle(cyc)
        output.send()
        input.recv()
        assert input.read_bus("A") == 0
        assert input.read_bus("Instruction") == bitarray.util.ba2int(instr)
        expected_C = 0
        if op == "set":
            expected_C = rA + (rB * 2 ** REG_BITS)
        assert input.read_bus("C") == expected_C
