from pathlib import Path

from bitarray.util import ba2int, int2ba, zeros
from pyslothpu16_core import N_BITS, AsmInstruction, Compare, OpCode

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

    def execute_instruction(self) -> None:  # noqa: C901
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

            case OpCode.COMPARE:
                assert instr.r_A is not None
                assert instr.r_B is not None
                assert instr.r_C is not None
                c = Compare.EQUAL
                if self.registers[instr.r_A] < self.registers[instr.r_B]:
                    c = Compare.LESSTHAN
                elif self.registers[instr.r_A] > self.registers[instr.r_B]:
                    c = Compare.GREATERTHAN
                self.registers[instr.r_C] = c

            case OpCode.NAND:
                assert instr.r_A is not None
                assert instr.r_B is not None
                assert instr.r_C is not None
                a = int2ba(self.registers[instr.r_A], length=N_BITS, endian="little")
                b = int2ba(self.registers[instr.r_B], length=N_BITS, endian="little")
                c = ~(a & b)
                self.registers[instr.r_C] = ba2int(c)

            case OpCode.XOR:
                assert instr.r_A is not None
                assert instr.r_B is not None
                assert instr.r_C is not None
                a = int2ba(self.registers[instr.r_A], length=N_BITS, endian="little")
                b = int2ba(self.registers[instr.r_B], length=N_BITS, endian="little")
                c = a ^ b
                self.registers[instr.r_C] = ba2int(c)

            case OpCode.BARREL:
                assert instr.r_A is not None
                assert instr.r_B is not None
                assert instr.r_C is not None

                b_red = self.registers[instr.r_B] % N_BITS
                a = int2ba(self.registers[instr.r_A], length=N_BITS, endian="little")
                c = zeros(N_BITS, endian="little")

                for i in range(N_BITS):
                    c[(i + b_red) % N_BITS] = a[i]

                self.registers[instr.r_C] = ba2int(c)

            case OpCode.LOADB:
                assert instr.r_A is not None
                assert instr.r_C is not None
                val = self.memory[self.registers[instr.r_A]]
                self.registers[instr.r_C] = val

            case OpCode.LOADW:
                assert instr.r_A is not None
                assert instr.r_C is not None
                val = self.memory.get_word(self.registers[instr.r_A])
                self.registers[instr.r_C] = val

            case OpCode.STOREB:
                assert instr.r_A is not None
                assert instr.r_B is not None
                store_value = self.registers[instr.r_B] % 256
                self.memory[self.registers[instr.r_A]] = store_value

            case OpCode.STOREW:
                assert instr.r_A is not None
                assert instr.r_B is not None
                store_value = self.registers[instr.r_B]
                self.memory.set_word(self.registers[instr.r_A], store_value)

            case OpCode.SET:
                assert instr.r_C is not None
                assert instr.value_to_set is not None
                self.registers[instr.r_C] = instr.value_to_set

            case OpCode.LOADPC:
                assert instr.r_C is not None
                self.registers[instr.r_C] = self.program_counter

            case OpCode.HALT:
                self._halted = True
                inhibit_pc_update = True

            case _:
                raise NotImplementedError(f"{instr}")

        if inhibit_pc_update:
            return

        self.program_counter += 2
