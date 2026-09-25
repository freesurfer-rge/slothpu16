from enum import IntEnum, unique

N_BITS = 16
INSTR_BITS = 4
REG_BITS = 4


@unique
class OpCode(IntEnum):
    ADD = 0
    SUB = 1
    COMPARE = 4
    NAND = 5
    XOR = 6
    BARREL = 7
    LOADB = 8
    LOADW = 9
    STOREB = 10
    STOREW = 11
    LOADPC = 12
    BRANCHZERO = 13
    HALT = 14
    SET = 15

    @classmethod
    def from_str(cls, value: str) -> "OpCode":
        for oc in OpCode:
            if value.lower() == oc.name.lower():
                return oc
        raise ValueError(f"Invalid opcode: {value}")
