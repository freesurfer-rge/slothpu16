import pytest
from pyslothpu16_core import AsmInstruction, OpCode


@pytest.mark.parametrize(
    ["oc", "rA", "rB", "rC"],
    [
        (OpCode.ADD, 1, 2, 3),
        (OpCode.SUB, 4, 5, 6),
        (OpCode.LOADB, 1, None, 4),
        (OpCode.LOADW, 2, None, 14),
        (OpCode.LOADPC, None, None, 15),
        (OpCode.SET, 11, 12, 13),
        (OpCode.HALT, None, None, None),
    ],
)
def test_smoke_construct(oc: OpCode, rA: int | None, rB: int | None, rC: int | None):
    _ = AsmInstruction(oc, r_A=rA, r_B=rB, r_C=rC)


@pytest.mark.parametrize(
    ["oc", "rA", "rB", "rC"],
    [
        (OpCode.ADD, -1, 2, 3),
        (OpCode.SUB, 16, 5, 6),
        (OpCode.LOADB, -1, None, 4),
        (OpCode.LOADW, 16, None, 14),
        (OpCode.SET, -1, 12, 13),
    ],
)
def test_rA_out_of_range(oc: OpCode, rA: int, rB: int | None, rC: int | None):
    with pytest.raises(ValueError) as ve:
        _ = AsmInstruction(oc, r_A=rA, r_B=rB, r_C=rC)
    assert ve.value.args[0] == f"Invalid Instruction: {oc.name} {rA} {rB} {rC}"


def test_bad_halt():
    with pytest.raises(ValueError) as ve:
        _ = AsmInstruction(OpCode.HALT, r_A=0, r_B=None, r_C=None)
    assert ve.value.args[0] == "Invalid Instruction: HALT 0 None None"
