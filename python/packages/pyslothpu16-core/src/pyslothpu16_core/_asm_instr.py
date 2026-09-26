from ._constants import REG_BITS
from ._opcode import OpCode


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

    def validate(self):
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

    def validate_reg_in_range(self, reg_value: int | None):
        if reg_value is None or reg_value < 0 or reg_value >= 2**REG_BITS:
            raise ValueError(f"Invalid Instruction: {self}")

    def __str__(self):
        return f"{self.opcode.name} {self.r_A} {self.r_B} {self.r_C}"
