import pytest

import bitarray.util

from pi_backplane import _Input, _Output


N_BITS = 16

# bus_vals = [0, 1]

N_BITS = 16
pwr_2 = [2 ** x for x in range(N_BITS)]
pwr_2_off = [((2 ** N_BITS) - 1) - 2 ** x for x in range(N_BITS)]
pwr_2_off_2 = [((2 ** N_BITS) - 2) - 2 ** x for x in range(N_BITS)]
others = [
    0,
    23,
    1065,
    2999,
    5132,
    7111,
    9147,
    11298,
    13221,
    17984,
    35632,
    43211,
    47231,
    65321,
]

bus_vals = pwr_2 + pwr_2_off + pwr_2_off_2 + others

# bus_vals = [0, 1]


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
    print(f"exp {C}")
    return bitarray.util.ba2int(C)


def xor_result(A_val: int, B_val: int) -> int:
    A = bitarray.util.int2ba(A_val, length=N_BITS, endian="little")
    B = bitarray.util.int2ba(B_val, length=N_BITS, endian="little")
    C = A ^ B
    return bitarray.util.ba2int(C)


def barrel_result(A_val: int, B_val: int) -> int:
    A = bitarray.util.int2ba(A_val, length=N_BITS, endian="little")
    expected = bitarray.util.zeros(N_BITS, endian="little")

    for i in range(N_BITS):
        expected[(i + B_val) % N_BITS] = A[i]
    return bitarray.util.ba2int(expected)


instructions = {"add": 0, "sub": 1, "compare": 4, "nand": 5, "xor": 6, "barrel": 7}
result_fns = {
    "add": add_result,
    "sub": sub_result,
    "compare": cmp_result,
    "nand": nand_result,
    "xor": xor_result,
    "barrel": barrel_result,
}


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
            print(f"act {bitarray.util.int2ba(c_val, length=N_BITS, endian='little')}")
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


@pytest.mark.parametrize("A", bus_vals)
@pytest.mark.parametrize("B", range(20))
def test_barrel(A, B):
    run_test(A, B, "barrel")
