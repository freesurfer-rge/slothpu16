import pytest

from pi_backplane import _Input, _Output

bus_vals = [
    0,
    1,
    127,
    128,
    129,
    1533,
    2989,
    32767,
    32768,
    32769,
    45534,
    60235,
    61233,
    65534,
    65535,
]


def cmp_result(A_val: int, B_val: int) -> int:
    if A_val < B_val:
        return 1
    elif A_val > B_val:
        return 4
    else:
        return 2


instructions = {"compare": 4}
result_fns = {"compare": cmp_result}


def run_test(A: int, B: int, instr: str):
    output = _Output()
    input = _Input()

    output.set_oe("A", False)
    output.set_oe("B", False)
    output.set_oe("Instruction", False)
    output.set_oe("Cycle", False)

    output.set_bus("A", A)
    output.set_bus("B", B)
    output.set_bus("Instruction", instructions[instr])
    output.send()

    active_cycles = [2, 3]
    for cyc in range(5):
        output.set_cycle(cyc)
        output.send()
        input.recv()

        c_val = input.read_bus("C")
        if cyc in active_cycles:
            assert c_val == result_fns[instr](A, B)
        else:
            assert c_val == 0


@pytest.mark.parametrize("A", bus_vals)
@pytest.mark.parametrize("B", bus_vals)
def test_comparator(A, B):
    run_test(A, B, "compare")
