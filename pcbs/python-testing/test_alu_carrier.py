import pytest

import bitarray.util

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

N_BITS = 16


def add_result(A_val: int, B_val: int) -> int:
    sum = A_val + B_val
    if sum >= 2 ** N_BITS:
        sum -= 2 ** N_BITS
    return sum


def sub_result(A_val: int, B_val: int) -> int:
    diff = A_val - B_val
    if diff < 0:
        diff += 2 ** N_BITS
    return diff


def cmp_result(A_val: int, B_val: int) -> int:
    if A_val < B_val:
        return 1
    elif A_val > B_val:
        return 4
    else:
        return 2

def nand_result(A_val: int, B_val: int) -> int:
    A = bitarray.util.int2ba(A_val, length=N_BITS, endian="little")
    B = bitarray.util.int2ba(B_val, length=N_BITS, endian="little")
    C = ~(A & B)
    return bitarray.util.ba2int(C)


def xor_result(A_val: int, B_val: int) -> int:
    A = bitarray.util.int2ba(A_val, length=N_BITS, endian="little")
    B = bitarray.util.int2ba(B_val, length=N_BITS, endian="little")
    C = A ^ B
    return bitarray.util.ba2int(C)

instructions = {"add": 0, "sub": 1, "compare": 4, "nand":5, "xor":6}
result_fns = {"add": add_result, "sub": sub_result, "compare": cmp_result, "nand": nand_result, "xor":xor_result}


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
def test_adder(A, B):
    run_test(A, B, "add")


@pytest.mark.parametrize("A", bus_vals)
@pytest.mark.parametrize("B", bus_vals)
def test_subtractor(A, B):
    run_test(A, B, "sub")


@pytest.mark.parametrize("A", bus_vals)
@pytest.mark.parametrize("B", bus_vals)
def test_comparator(A, B):
    run_test(A, B, "compare")

@pytest.mark.parametrize("A", bus_vals)
@pytest.mark.parametrize("B", bus_vals)
def test_nand(A, B):
    run_test(A, B, "nand")

    
@pytest.mark.parametrize("A", bus_vals)
@pytest.mark.parametrize("B", bus_vals)
def test_xor(A, B):
    run_test(A, B, "xor")
