from ._constants import N_BITS, REG_BITS
from ._opcode import OpCode


def _get_reg_string(reg_value: int | None) -> str:
    if reg_value is None:
        return "None"
    return f"R{reg_value}"


def _parse_reg_string(target: str) -> int:
    if target[0] != "R":
        raise ValueError(f"Parse error: {target}")
    reg_id = int(target[1:])
    return reg_id


class AsmInstruction:
    def __init__(self, op: OpCode, *, r_A: int | None, r_B: int | None, r_C: int | None):
        self._op = op
        self._rA = r_A
        self._rB = r_B
        self._rC = r_C

        self.validate()

    @property
    def opcode(self) -> OpCode:
        return self._op

    @property
    def r_A(self) -> int | None:
        return self._rA

    @property
    def r_B(self) -> int | None:
        return self._rB

    @property
    def r_C(self) -> int | None:
        return self._rC

    @property
    def value_to_set(self) -> int | None:
        if self.opcode != OpCode.SET:
            raise ValueError(f"No value to set: {self}")
        if self.r_A is not None and self.r_B is not None:
            return self.r_A + ((2**REG_BITS) * self.r_B)
        return None

    def validate(self) -> None:
        match self.opcode:
            case OpCode.HALT:
                if self.r_A is not None or self.r_B is not None or self.r_C is not None:
                    raise ValueError(f"Invalid Instruction: {self}")
            case OpCode.LOADPC:
                if self.r_A is not None or self.r_B is not None:
                    raise ValueError(f"Invalid Instruction: {self}")
                self.validate_reg_in_range(self.r_C)
            case OpCode.LOADB | OpCode.LOADW:
                if self.r_B is not None:
                    raise ValueError(f"Invalid Instruction: {self}")
                self.validate_reg_in_range(self.r_A)
                self.validate_reg_in_range(self.r_C)
            case _:
                self.validate_reg_in_range(self.r_A)
                self.validate_reg_in_range(self.r_B)
                self.validate_reg_in_range(self.r_C)

    def validate_reg_in_range(self, reg_value: int | None) -> None:
        if reg_value is None or reg_value < 0 or reg_value >= 2**REG_BITS:
            raise ValueError(f"Invalid Instruction: {self}")

    def __str__(self) -> str:
        a_str = _get_reg_string(self.r_A)
        b_str = _get_reg_string(self.r_B)
        c_str = _get_reg_string(self.r_C)
        return f"{self.opcode.name} {a_str} {b_str} {c_str}"

    def to_int(self) -> int:
        instr_val = int(self.opcode)
        rA_val = (2**REG_BITS) * (self.r_A if self.r_A else 0)
        rB_val = (2 ** (2 * REG_BITS)) * (self.r_B if self.r_B else 0)
        rC_val = (2 ** (3 * REG_BITS)) * (self.r_C if self.r_C else 0)
        return instr_val + rA_val + rB_val + rC_val

    @classmethod
    def from_int(cls, source: int) -> "AsmInstruction":
        if source < 0 or source >= 2**N_BITS:
            raise ValueError(f"Int out of range: {source}")

        reg_block, op_val = divmod(source, 2**REG_BITS)
        oc = OpCode(op_val)

        reg_block, rA = divmod(reg_block, 2**REG_BITS)
        rC, rB = divmod(reg_block, 2**REG_BITS)

        match oc:
            case OpCode.HALT:
                if reg_block != 0:
                    raise ValueError(f"Bad regblock: {oc} {rA} {rB} {rC}")
                return AsmInstruction(oc, r_A=None, r_B=None, r_C=None)
            case OpCode.LOADPC:
                if rA != 0 or rB != 0:
                    raise ValueError(f"Bad regblock: {oc} {rA} {rB} {rC}")
                return AsmInstruction(oc, r_A=None, r_B=None, r_C=rC)
            case OpCode.LOADB | OpCode.LOADW:
                if rB != 0:
                    raise ValueError(f"Bad regblock: {oc} {rA} {rB} {rC}")
                return AsmInstruction(oc, r_A=rA, r_B=None, r_C=rC)
            case _:
                # No need to special case set here
                return AsmInstruction(oc, r_A=rA, r_B=rB, r_C=rC)

    @classmethod
    def from_str(cls, source: str) -> "AsmInstruction":  # noqa: C901
        trimmed = source.strip()
        items = trimmed.split()

        oc = OpCode[items[0].upper()]
        match oc:
            case OpCode.HALT:
                if len(items) > 1:
                    raise ValueError(f"Parse error: {source}")
                return AsmInstruction(oc, r_A=None, r_B=None, r_C=None)
            case OpCode.LOADPC:
                if len(items) > 2:
                    raise ValueError(f"Parse error: {source}")
                rC = _parse_reg_string(items[1])
                return AsmInstruction(oc, r_A=None, r_B=None, r_C=rC)
            case OpCode.LOADB | OpCode.LOADW:
                if len(items) > 3:
                    raise ValueError(f"Parse error: {source}")
                rA = _parse_reg_string(items[1])
                rC = _parse_reg_string(items[2])
                return AsmInstruction(oc, r_A=rA, r_B=None, r_C=rC)
            case OpCode.SET:
                if len(items) > 3:
                    raise ValueError(f"Parse error: {source}")
                val = int(items[1])
                if val < 0 or val > 255:
                    raise ValueError(f"Parse error: {source}")
                rB, rA = divmod(val, 2**REG_BITS)
                rC = _parse_reg_string(items[2])
                return AsmInstruction(oc, r_A=rA, r_B=rB, r_C=rC)
            case _:
                if len(items) > 4:
                    raise ValueError(f"Parse error: {source}")
                rA = _parse_reg_string(items[1])
                rB = _parse_reg_string(items[2])
                rC = _parse_reg_string(items[3])
                return AsmInstruction(oc, r_A=rA, r_B=rB, r_C=rC)
