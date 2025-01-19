import pytest

from pi_backplane import _Input, _Output

bus_vals = [0, 1, 32768, 45534, 65535]
cycle_vals = list(range(-1, 5))


@pytest.mark.parametrize("A", bus_vals)
@pytest.mark.parametrize("B", bus_vals)
@pytest.mark.parametrize("C", bus_vals)
@pytest.mark.parametrize("Instruction", bus_vals)
@pytest.mark.parametrize("Cycle", cycle_vals)
def test_buses(A, B, C, Instruction, Cycle):
    output = _Output()
    input = _Input()

    buses = ["A", "B", "C", "Instruction"]
    for bus in buses:
        output.set_oe(bus, False)
    output.set_oe("Cycle", False)

    output.set_bus("A", A)
    output.set_bus("B", B)
    output.set_bus("C", C)
    output.set_bus("Instruction", Instruction)
    output.set_cycle(Cycle)
    output.send()

    input.recv()
    assert input.read_bus("A") == A
    assert input.read_bus("B") == B
    assert input.read_bus("C") == C
    assert input.read_bus("Instruction") == Instruction
    assert input.read_cycle() == Cycle

    # Now isolate individual buses
    for target_bus in buses:
        for b in buses:
            output.set_oe(b, False)
        output.set_oe(target_bus, True)

        input.recv()
        assert input.read_bus("A") == (A if target_bus != "A" else 0)
        assert input.read_bus("B") == (B if target_bus != "B" else 0)
        assert input.read_bus("C") == (C if target_bus != "C" else 0)
        assert input.read_bus("Instruction") == (
            Instruction if target_bus != "Instruction" else 0
        )
        assert input.read_cycle() == Cycle

    # And the cycle bus
    for bus in buses:
        output.set_oe(bus, False)
    output.set_oe("Cycle", True)

    input.recv()
    assert input.read_bus("A") == A
    assert input.read_bus("B") == B
    assert input.read_bus("C") == C
    assert input.read_bus("Instruction") == Instruction
    assert input.read_cycle() == -1


def test_clock():
    output = _Output()
    input = _Input()

    output.set_oe("Clock", False)

    output.set_clock(True)
    output.send()
    input.recv()
    assert input.read_clock() == True

    output.set_clock(False)
    output.send()
    input.recv()
    assert input.read_clock() == False

    output.set_clock(True)
    output.send()
    input.recv()
    assert input.read_clock() == True

    # Should be pulled down by LED on isolation
    output.set_oe("Clock", True)
    input.recv()
    assert input.read_clock() == False


def test_reset():
    output = _Output()
    input = _Input()

    output.set_oe("Reset", False)

    output.set_reset(True)
    output.send()
    input.recv()
    assert input.read_reset() == True

    output.set_reset(False)
    output.send()
    input.recv()
    assert input.read_reset() == False

    output.set_reset(True)
    output.send()
    input.recv()
    assert input.read_reset() == True

    # Should be pulled down by LED on isolation
    output.set_oe("Reset", True)
    input.recv()
    assert input.read_clock() == False
