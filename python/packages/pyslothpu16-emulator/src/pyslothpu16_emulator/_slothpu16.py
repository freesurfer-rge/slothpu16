from pathlib import Path

from pyslothpu16_core import N_BITS, AsmInstruction, OpCode

from ._mainmemory import MainMemory, mainmemory_from_file
from ._registerfile import RegisterFile


class SlothPU16:
    def __init__(self, *, asm_file: Path | None = None):
        self._rf = RegisterFile()

        if asm_file:
            self._memory = mainmemory_from_file(asm_file)
        else:
            self._memory = MainMemory()

        self.instruction_register = 0
        self.program_counter = 0
        self._halted = False

        self.load_instruction()

    @property
    def halted(self) -> bool:
        return self._halted

    @property
    def memory(self) -> MainMemory:
        return self._memory

    @property
    def registers(self) -> RegisterFile:
        return self._rf

    @property
    def instruction_register(self) -> int:
        return self._ir

    @instruction_register.setter
    def instruction_register(self, value: int) -> None:
        if value < 0 or value >= 2**N_BITS:
            raise ValueError(f"IR value out of range: {value}")
        self._ir = value

    @property
    def program_counter(self) -> int:
        return self._pc

    @program_counter.setter
    def program_counter(self, value: int) -> None:
        if value < 0 or value >= 2**N_BITS:
            raise ValueError(f"PC value out of range: {value}")
        if value % 2 != 0:
            raise ValueError(f"PC value not aligned {value}")
        self._pc = value

    def load_instruction(self) -> None:
        if self.halted:
            return
        instr = self.memory.get_word(self.program_counter)
        self.instruction_register = instr

    def execute_instruction(self) -> None:
        if self.halted:
            return

        instr = AsmInstruction.from_int(self.instruction_register)

        inhibit_pc_update = False
        match instr.opcode:
            case OpCode.ADD:
                assert instr.r_A is not None
                assert instr.r_B is not None
                assert instr.r_C is not None
                c = self.registers[instr.r_A] + self.registers[instr.r_B]
                c = c % (2**N_BITS)
                self.registers[instr.r_C] = c

            case OpCode.SUB:
                assert instr.r_A is not None
                assert instr.r_B is not None
                assert instr.r_C is not None
                c = self.registers[instr.r_A] - self.registers[instr.r_B]
                if c < 0:
                    c += 2**N_BITS
                self.registers[instr.r_C] = c

            case OpCode.LOADB:
                assert instr.r_A is not None
                assert instr.r_C is not None
                val = self.memory[self.registers[instr.r_A]]
                self.registers[instr.r_C] = val

            case OpCode.SET:
                assert instr.r_C is not None
                assert instr.value_to_set is not None
                self.registers[instr.r_C] = instr.value_to_set

            case OpCode.HALT:
                self._halted = True
                inhibit_pc_update = True

            case _:
                raise NotImplementedError(f"{instr}")

        if inhibit_pc_update:
            return

        self.program_counter += 2
