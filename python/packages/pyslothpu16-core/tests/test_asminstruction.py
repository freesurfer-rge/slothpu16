import pytest
from pyslothpu16_core import AsmInstruction, OpCode

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
        assert str(instr) == f"{oc.name} R{rA} R{rB} R{rC}"

    @pytest.mark.parametrize("oc", _THREE_REG_INSTRS)
    def test_rA_missing(self, oc: OpCode):
        with pytest.raises(ValueError) as ve:
            _ = AsmInstruction(oc, r_A=None, r_B=0, r_C=1)
        assert ve.value.args[0] == f"Invalid Instruction: {oc.name} None R0 R1"

    @pytest.mark.parametrize("oc", _THREE_REG_INSTRS)
    @pytest.mark.parametrize("rA", [-1, 16])
    def test_rA_invalid(self, oc: OpCode, rA: int):
        with pytest.raises(ValueError) as ve:
            _ = AsmInstruction(oc, r_A=rA, r_B=0, r_C=1)
        assert ve.value.args[0] == f"Invalid Instruction: {oc.name} R{rA} R0 R1"

    @pytest.mark.parametrize("oc", _THREE_REG_INSTRS)
    def test_rB_missing(self, oc: OpCode):
        with pytest.raises(ValueError) as ve:
            _ = AsmInstruction(oc, r_A=0, r_B=None, r_C=1)
        assert ve.value.args[0] == f"Invalid Instruction: {oc.name} R0 None R1"

    @pytest.mark.parametrize("oc", _THREE_REG_INSTRS)
    @pytest.mark.parametrize("rB", [-1, 16])
    def test_rB_invalid(self, oc: OpCode, rB: int):
        with pytest.raises(ValueError) as ve:
            _ = AsmInstruction(oc, r_A=0, r_B=rB, r_C=1)
        assert ve.value.args[0] == f"Invalid Instruction: {oc.name} R0 R{rB} R1"

    @pytest.mark.parametrize("oc", _THREE_REG_INSTRS)
    def test_rC_missing(self, oc: OpCode):
        with pytest.raises(ValueError) as ve:
            _ = AsmInstruction(oc, r_A=0, r_B=1, r_C=None)
        assert ve.value.args[0] == f"Invalid Instruction: {oc.name} R0 R1 None"

    @pytest.mark.parametrize("oc", _THREE_REG_INSTRS)
    @pytest.mark.parametrize("rC", [-1, 16])
    def test_rC_invalid(self, oc: OpCode, rC: int):
        with pytest.raises(ValueError) as ve:
            _ = AsmInstruction(oc, r_A=0, r_B=1, r_C=rC)
        assert ve.value.args[0] == f"Invalid Instruction: {oc.name} R0 R1 R{rC}"


class TestSetInstruction:
    @pytest.mark.parametrize("rA", [0, 1, 15])
    @pytest.mark.parametrize("rB", [0, 1, 15])
    @pytest.mark.parametrize("rC", [0, 1, 15])
    def test_smoke(self, rA: int, rB: int, rC: int):
        instr = AsmInstruction(OpCode.SET, r_A=rA, r_B=rB, r_C=rC)
        assert str(instr) == f"SET R{rA} R{rB} R{rC}"
        assert instr.value_to_set == rA + (16 * rB)


_TWO_REG_INSTRS = [OpCode.LOADB, OpCode.LOADW]


class TestTwoRegisterInstructions:
    @pytest.mark.parametrize("oc", _TWO_REG_INSTRS)
    @pytest.mark.parametrize("rA", [0, 1, 15])
    @pytest.mark.parametrize("rC", [0, 1, 15])
    def test_smoke(self, oc: OpCode, rA: int, rC: int):
        instr = AsmInstruction(oc, r_A=rA, r_B=None, r_C=rC)
        assert str(instr) == f"{oc.name} R{rA} None R{rC}"

    @pytest.mark.parametrize("oc", _TWO_REG_INSTRS)
    def test_rB_not_none(self, oc: OpCode):
        with pytest.raises(ValueError) as ve:
            _ = AsmInstruction(oc, r_A=0, r_B=1, r_C=2)
        assert ve.value.args[0] == f"Invalid Instruction: {oc.name} R0 R1 R2"

    @pytest.mark.parametrize("oc", _TWO_REG_INSTRS)
    def test_rA_missing(self, oc: OpCode):
        with pytest.raises(ValueError) as ve:
            _ = AsmInstruction(oc, r_A=None, r_B=None, r_C=1)
        assert ve.value.args[0] == f"Invalid Instruction: {oc.name} None None R1"

    @pytest.mark.parametrize("oc", _TWO_REG_INSTRS)
    @pytest.mark.parametrize("rA", [-1, 16])
    def test_rA_invalid(self, oc: OpCode, rA: int):
        with pytest.raises(ValueError) as ve:
            _ = AsmInstruction(oc, r_A=rA, r_B=None, r_C=1)
        assert ve.value.args[0] == f"Invalid Instruction: {oc.name} R{rA} None R1"

    @pytest.mark.parametrize("oc", _TWO_REG_INSTRS)
    def test_rB_present(self, oc: OpCode):
        with pytest.raises(ValueError) as ve:
            _ = AsmInstruction(oc, r_A=2, r_B=1, r_C=3)
        assert ve.value.args[0] == f"Invalid Instruction: {oc.name} R2 R1 R3"

    @pytest.mark.parametrize("oc", _TWO_REG_INSTRS)
    def test_rC_missing(self, oc: OpCode):
        with pytest.raises(ValueError) as ve:
            _ = AsmInstruction(oc, r_A=0, r_B=None, r_C=None)
        assert ve.value.args[0] == f"Invalid Instruction: {oc.name} R0 None None"

    @pytest.mark.parametrize("oc", _TWO_REG_INSTRS)
    @pytest.mark.parametrize("rC", [-1, 16])
    def test_rC_invalid(self, oc: OpCode, rC: int):
        with pytest.raises(ValueError) as ve:
            _ = AsmInstruction(oc, r_A=0, r_B=None, r_C=rC)
        assert ve.value.args[0] == f"Invalid Instruction: {oc.name} R0 None R{rC}"


class TestLoadPC:
    @pytest.mark.parametrize("rC", [0, 1, 15])
    def test_smoke(self, rC: int):
        instr = AsmInstruction(OpCode.LOADPC, r_A=None, r_B=None, r_C=rC)
        assert str(instr) == f"LOADPC None None R{rC}"

    def test_rA_present(self):
        with pytest.raises(ValueError) as ve:
            _ = AsmInstruction(OpCode.LOADPC, r_A=1, r_B=None, r_C=2)
        assert ve.value.args[0] == "Invalid Instruction: LOADPC R1 None R2"

    def test_rB_present(self):
        with pytest.raises(ValueError) as ve:
            _ = AsmInstruction(OpCode.LOADPC, r_A=None, r_B=1, r_C=2)
        assert ve.value.args[0] == "Invalid Instruction: LOADPC None R1 R2"

    def test_rC_missing(self):
        with pytest.raises(ValueError) as ve:
            _ = AsmInstruction(OpCode.LOADPC, r_A=None, r_B=None, r_C=None)
        assert ve.value.args[0] == "Invalid Instruction: LOADPC None None None"

    @pytest.mark.parametrize("rC", [-1, 16])
    def test_rC_invalid(self, rC: int):
        with pytest.raises(ValueError) as ve:
            _ = AsmInstruction(OpCode.LOADPC, r_A=None, r_B=None, r_C=rC)
        assert ve.value.args[0] == f"Invalid Instruction: LOADPC None None R{rC}"


class TestHalt:
    def test_smoke(self):
        instr = AsmInstruction(OpCode.HALT, r_A=None, r_B=None, r_C=None)
        assert str(instr) == "HALT None None None"

    def test_rA_present(self):
        with pytest.raises(ValueError) as ve:
            _ = AsmInstruction(OpCode.HALT, r_A=1, r_B=None, r_C=None)
        assert ve.value.args[0] == "Invalid Instruction: HALT R1 None None"

    def test_rB_present(self):
        with pytest.raises(ValueError) as ve:
            _ = AsmInstruction(OpCode.HALT, r_A=None, r_B=1, r_C=None)
        assert ve.value.args[0] == "Invalid Instruction: HALT None R1 None"

    def test_rC_present(self):
        with pytest.raises(ValueError) as ve:
            _ = AsmInstruction(OpCode.HALT, r_A=None, r_B=None, r_C=2)
        assert ve.value.args[0] == "Invalid Instruction: HALT None None R2"
