import pytest

from pi_backplane import _Input, _Output

bus_vals = [0, 1, 2989, 32767, 32768, 32769, 45534, 65535]

instructions = {
    "compare" : 4
    }

@pytest.mark.parametrize("A", bus_vals)
@pytest.mark.parametrize("B", bus_vals)
def test_comparator(A, B):
    output = _Output()
    input = _Input()

    output.set_oe("A", False)
    output.set_oe("B", False)
    output.set_oe("Instruction", False)
    output.set_oe("Cycle", False)

    output.set_bus("A", A)
    output.set_bus("B", B)
    output.set_bus("Instruction", instructions["compare"])
    output.send()

    active_cycles = [2, 3]
    for c in range(5):
        output.set_cycle(c)
        input.recv()

        c_val = input.read_bus("C")
        if c in active_cycles:
            if A < B:
                assert c_val == 1
            elif A > B:
                assert c_val == 4
            else:
                assert c== 2
        else:
            assert c_val == 0
