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


# Note that we skip 'set' here
_THREE_REG_INSTRS = [
    OpCode.ADD,
    OpCode.SUB,
    OpCode.COMPARE,
    OpCode.NAND,
    OpCode.XOR,
    OpCode.NAND,
    OpCode.BARREL,
    OpCode.STOREB,
    OpCode.STOREW,
]


class TestThreeRegisterInstructions:
    @pytest.mark.parametrize("oc", _THREE_REG_INSTRS)
    @pytest.mark.parametrize("rA", [0, 1, 15])
    @pytest.mark.parametrize("rB", [0, 1, 15])
    @pytest.mark.parametrize("rC", [0, 1, 15])
    def test_smoke(self, oc: OpCode, rA: int, rB: int, rC: int):
        instr = AsmInstruction(oc, r_A=rA, r_B=rB, r_C=rC)
        assert str(instr) == f"{oc.name} {rA} {rB} {rC}"

    @pytest.mark.parametrize("oc", _THREE_REG_INSTRS)
    def test_rA_missing(self, oc: OpCode):
        with pytest.raises(ValueError) as ve:
            _ = AsmInstruction(oc, r_A=None, r_B=0, r_C=1)
        assert ve.value.args[0] == f"Invalid Instruction: {oc.name} None 0 1"

    @pytest.mark.parametrize("oc", _THREE_REG_INSTRS)
    @pytest.mark.parametrize("rA", [-1, 16])
    def test_rA_invalid(self, oc: OpCode, rA: int):
        with pytest.raises(ValueError) as ve:
            _ = AsmInstruction(oc, r_A=rA, r_B=0, r_C=1)
        assert ve.value.args[0] == f"Invalid Instruction: {oc.name} {rA} 0 1"

    @pytest.mark.parametrize("oc", _THREE_REG_INSTRS)
    def test_rB_missing(self, oc: OpCode):
        with pytest.raises(ValueError) as ve:
            _ = AsmInstruction(oc, r_A=0, r_B=None, r_C=1)
        assert ve.value.args[0] == f"Invalid Instruction: {oc.name} 0 None 1"

    @pytest.mark.parametrize("oc", _THREE_REG_INSTRS)
    @pytest.mark.parametrize("rB", [-1, 16])
    def test_rB_invalid(self, oc: OpCode, rB: int):
        with pytest.raises(ValueError) as ve:
            _ = AsmInstruction(oc, r_A=0, r_B=rB, r_C=1)
        assert ve.value.args[0] == f"Invalid Instruction: {oc.name} 0 {rB} 1"

    @pytest.mark.parametrize("oc", _THREE_REG_INSTRS)
    def test_rC_missing(self, oc: OpCode):
        with pytest.raises(ValueError) as ve:
            _ = AsmInstruction(oc, r_A=0, r_B=1, r_C=None)
        assert ve.value.args[0] == f"Invalid Instruction: {oc.name} 0 1 None"

    @pytest.mark.parametrize("oc", _THREE_REG_INSTRS)
    @pytest.mark.parametrize("rC", [-1, 16])
    def test_rC_invalid(self, oc: OpCode, rC: int):
        with pytest.raises(ValueError) as ve:
            _ = AsmInstruction(oc, r_A=0, r_B=1, r_C=rC)
        assert ve.value.args[0] == f"Invalid Instruction: {oc.name} 0 1 {rC}"


class TestSetInstruction:
    @pytest.mark.parametrize("rA", [0, 1, 15])
    @pytest.mark.parametrize("rB", [0, 1, 15])
    @pytest.mark.parametrize("rC", [0, 1, 15])
    def test_smoke(self, rA: int, rB: int, rC: int):
        instr = AsmInstruction(OpCode.SET, r_A=rA, r_B=rB, r_C=rC)
        assert str(instr) == f"SET {rA} {rB} {rC}"
        assert instr.value_to_set == rA + (16 * rB)


_TWO_REG_INSTRS = [OpCode.LOADB, OpCode.LOADW]


class TestTwoRegisterInstructions:
    @pytest.mark.parametrize("oc", _TWO_REG_INSTRS)
    @pytest.mark.parametrize("rA", [0, 1, 15])
    @pytest.mark.parametrize("rC", [0, 1, 15])
    def test_smoke(self, oc: OpCode, rA: int, rC: int):
        instr = AsmInstruction(oc, r_A=rA, r_B=None, r_C=rC)
        assert str(instr) == f"{oc.name} {rA} None {rC}"

    @pytest.mark.parametrize("oc", _TWO_REG_INSTRS)
    def test_rB_not_none(self, oc: OpCode):
        with pytest.raises(ValueError) as ve:
            _ = AsmInstruction(oc, r_A=0, r_B=1, r_C=2)
        assert ve.value.args[0] == f"Invalid Instruction: {oc.name} 0 1 2"

    @pytest.mark.parametrize("oc", _TWO_REG_INSTRS)
    def test_rA_missing(self, oc: OpCode):
        with pytest.raises(ValueError) as ve:
            _ = AsmInstruction(oc, r_A=None, r_B=None, r_C=1)
        assert ve.value.args[0] == f"Invalid Instruction: {oc.name} None None 1"

    @pytest.mark.parametrize("oc", _TWO_REG_INSTRS)
    @pytest.mark.parametrize("rA", [-1, 16])
    def test_rA_invalid(self, oc: OpCode, rA: int):
        with pytest.raises(ValueError) as ve:
            _ = AsmInstruction(oc, r_A=rA, r_B=None, r_C=1)
        assert ve.value.args[0] == f"Invalid Instruction: {oc.name} {rA} None 1"

    @pytest.mark.parametrize("oc", _TWO_REG_INSTRS)
    def test_rB_present(self, oc: OpCode):
        with pytest.raises(ValueError) as ve:
            _ = AsmInstruction(oc, r_A=2, r_B=1, r_C=3)
        assert ve.value.args[0] == f"Invalid Instruction: {oc.name} 2 1 3"

    @pytest.mark.parametrize("oc", _TWO_REG_INSTRS)
    def test_rC_missing(self, oc: OpCode):
        with pytest.raises(ValueError) as ve:
            _ = AsmInstruction(oc, r_A=0, r_B=None, r_C=None)
        assert ve.value.args[0] == f"Invalid Instruction: {oc.name} 0 None None"

    @pytest.mark.parametrize("oc", _TWO_REG_INSTRS)
    @pytest.mark.parametrize("rC", [-1, 16])
    def test_rC_invalid(self, oc: OpCode, rC: int):
        with pytest.raises(ValueError) as ve:
            _ = AsmInstruction(oc, r_A=0, r_B=None, r_C=rC)
        assert ve.value.args[0] == f"Invalid Instruction: {oc.name} 0 None {rC}"


class TestLoadPC:
    @pytest.mark.parametrize("rC", [0, 1, 15])
    def test_smoke(self, rC: int):
        instr = AsmInstruction(OpCode.LOADPC, r_A=None, r_B=None, r_C=rC)
        assert str(instr) == f"LOADPC None None {rC}"

    def test_rA_present(self):
        with pytest.raises(ValueError) as ve:
            _ = AsmInstruction(OpCode.LOADPC, r_A=1, r_B=None, r_C=2)
        assert ve.value.args[0] == "Invalid Instruction: LOADPC 1 None 2"

    def test_rB_present(self):
        with pytest.raises(ValueError) as ve:
            _ = AsmInstruction(OpCode.LOADPC, r_A=None, r_B=1, r_C=2)
        assert ve.value.args[0] == "Invalid Instruction: LOADPC None 1 2"

    def test_rC_missing(self):
        with pytest.raises(ValueError) as ve:
            _ = AsmInstruction(OpCode.LOADPC, r_A=None, r_B=None, r_C=None)
        assert ve.value.args[0] == "Invalid Instruction: LOADPC None None None"

    @pytest.mark.parametrize("rC", [-1, 16])
    def test_rC_invalid(self, rC: int):
        with pytest.raises(ValueError) as ve:
            _ = AsmInstruction(OpCode.LOADPC, r_A=None, r_B=None, r_C=rC)
        assert ve.value.args[0] == f"Invalid Instruction: LOADPC None None {rC}"
