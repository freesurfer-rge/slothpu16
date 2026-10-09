import pytest
from bitarray.util import ba2int, int2ba, zeros
from pyslothpu16_core import N_BITS, REG_BITS, AsmInstruction, Compare, OpCode
from pyslothpu16_emulator import SlothPU16


def test_smoke(sample_program_dir) -> None:
    smoke_program = sample_program_dir / "set_one_register.slothpu16"
    assert smoke_program.exists(), f"Not found: {smoke_program}"
    target = SlothPU16(asm_file=smoke_program)

    assert not target.halted

    nxt_instr = AsmInstruction.from_int(target.instruction_register)
    assert nxt_instr.opcode == OpCode.SET
    assert nxt_instr.value_to_set == 1
    assert nxt_instr.r_C == 0

    target.execute_instruction()

    assert not target.halted
    assert target.registers[0] == 1
    assert target.program_counter == 2

    target.load_instruction()
    target.execute_instruction()
    assert target.halted
    assert target.program_counter == 2

    target.load_instruction()
    assert target.halted
    assert target.program_counter == 2

    target.execute_instruction()
    assert target.halted
    assert target.program_counter == 2


class TestAdd:
    @pytest.mark.parametrize("rA", [0, 1, 15])
    @pytest.mark.parametrize("rB", [2, 3, 14])
    @pytest.mark.parametrize("rC", [10, 11, 12])
    @pytest.mark.parametrize("a", [0, 1, 255, 65535])
    @pytest.mark.parametrize("b", [0, 1, 255, 65535])
    def test_smoke(self, rA: int, rB: int, rC: int, a: int, b: int) -> None:
        c = (a + b) % 2**N_BITS

        target = SlothPU16()
        for i in range(2**REG_BITS):
            target.registers[i] = 1024
        target.registers[rA] = a
        target.registers[rB] = b

        instr = AsmInstruction(OpCode.ADD, r_A=rA, r_B=rB, r_C=rC)
        target.instruction_register = instr.to_int()

        target.execute_instruction()
        assert target.registers[rA] == a
        assert target.registers[rB] == b
        assert target.registers[rC] == c


class TestSub:
    @pytest.mark.parametrize("rC", [0, 1, 15])
    @pytest.mark.parametrize("rB", [2, 3, 14])
    @pytest.mark.parametrize("rA", [10, 11, 12])
    @pytest.mark.parametrize("a", [0, 1, 255, 65535])
    @pytest.mark.parametrize("b", [0, 1, 255, 65535])
    def test_smoke(self, rA: int, rB: int, rC: int, a: int, b: int) -> None:
        c = a - b
        if c < 0:
            c += 2**N_BITS

        target = SlothPU16()
        for i in range(2**REG_BITS):
            target.registers[i] = 1024
        target.registers[rA] = a
        target.registers[rB] = b

        instr = AsmInstruction(OpCode.SUB, r_A=rA, r_B=rB, r_C=rC)
        target.instruction_register = instr.to_int()

        target.execute_instruction()
        assert target.registers[rA] == a
        assert target.registers[rB] == b
        assert target.registers[rC] == c


class TestCompare:
    @pytest.mark.parametrize("rC", [0, 1, 15])
    @pytest.mark.parametrize("rB", [2, 3, 14])
    @pytest.mark.parametrize("rA", [10, 11, 12])
    @pytest.mark.parametrize("a", [0, 1, 255, 65535])
    @pytest.mark.parametrize("b", [0, 1, 255, 65535])
    def test_smoke(self, rA: int, rB: int, rC: int, a: int, b: int) -> None:
        c = Compare.EQUAL
        if a < b:
            c = Compare.LESSTHAN
        elif a > b:
            c = Compare.GREATERTHAN

        target = SlothPU16()
        for i in range(2**REG_BITS):
            target.registers[i] = 1024
        target.registers[rA] = a
        target.registers[rB] = b

        instr = AsmInstruction(OpCode.COMPARE, r_A=rA, r_B=rB, r_C=rC)
        target.instruction_register = instr.to_int()

        target.execute_instruction()
        assert target.registers[rA] == a
        assert target.registers[rB] == b
        assert target.registers[rC] == c


class TestNAND:
    @pytest.mark.parametrize("rA", [0, 1, 15])
    @pytest.mark.parametrize("rB", [10, 11, 12])
    @pytest.mark.parametrize("rC", [2, 3, 14])
    def test_smoke(self, rA: int, rB: int, rC: int):
        a = 2
        b = 65533
        c = 65535

        target = SlothPU16()
        for i in range(2**REG_BITS):
            target.registers[i] = 1024
        target.registers[rA] = a
        target.registers[rB] = b

        instr = AsmInstruction(OpCode.NAND, r_A=rA, r_B=rB, r_C=rC)
        target.instruction_register = instr.to_int()

        target.execute_instruction()
        assert target.registers[rA] == a
        assert target.registers[rB] == b
        assert target.registers[rC] == c

    @pytest.mark.parametrize("rA", [0, 1, 15])
    @pytest.mark.parametrize("rB", [10, 11, 12])
    @pytest.mark.parametrize("rC", [2, 3, 14])
    def test_one_match(self, rA: int, rB: int, rC: int):
        a = 2
        b = 3
        c = 65533

        target = SlothPU16()
        for i in range(2**REG_BITS):
            target.registers[i] = 1024
        target.registers[rA] = a
        target.registers[rB] = b

        instr = AsmInstruction(OpCode.NAND, r_A=rA, r_B=rB, r_C=rC)
        target.instruction_register = instr.to_int()

        target.execute_instruction()
        assert target.registers[rA] == a
        assert target.registers[rB] == b
        assert target.registers[rC] == c


class TestXOR:
    @pytest.mark.parametrize("rA", [0, 1, 15])
    @pytest.mark.parametrize("rB", [10, 11, 12])
    @pytest.mark.parametrize("rC", [2, 3, 14])
    def test_smoke(self, rA: int, rB: int, rC: int):
        a = 2
        b = 65533
        c = 65535

        target = SlothPU16()
        for i in range(2**REG_BITS):
            target.registers[i] = 1024
        target.registers[rA] = a
        target.registers[rB] = b

        instr = AsmInstruction(OpCode.XOR, r_A=rA, r_B=rB, r_C=rC)
        target.instruction_register = instr.to_int()

        target.execute_instruction()
        assert target.registers[rA] == a
        assert target.registers[rB] == b
        assert target.registers[rC] == c

    @pytest.mark.parametrize("rA", [0, 1, 15])
    @pytest.mark.parametrize("rB", [10, 11, 12])
    @pytest.mark.parametrize("rC", [2, 3, 14])
    def test_one_match(self, rA: int, rB: int, rC: int):
        a = 2
        b = 3
        c = 1

        target = SlothPU16()
        for i in range(2**REG_BITS):
            target.registers[i] = 1024
        target.registers[rA] = a
        target.registers[rB] = b

        instr = AsmInstruction(OpCode.XOR, r_A=rA, r_B=rB, r_C=rC)
        target.instruction_register = instr.to_int()

        target.execute_instruction()
        assert target.registers[rA] == a
        assert target.registers[rB] == b
        assert target.registers[rC] == c


class TestBarrel:
    @pytest.mark.parametrize("rC", [0, 5, 15])
    @pytest.mark.parametrize("rB", [7, 8, 14])
    @pytest.mark.parametrize("rA", [9, 11, 12])
    @pytest.mark.parametrize("a", [0, 1, 254, 65535])
    @pytest.mark.parametrize("b", range(20))
    def test_smoke(self, rA: int, rB: int, rC: int, a: int, b: int) -> None:
        b_red = b % 16

        a_bits = int2ba(a, N_BITS, endian="little")
        c_bits = zeros(N_BITS, endian="little")

        for i in range(N_BITS):
            c_bits[(i + b_red) % N_BITS] = a_bits[i]

        target = SlothPU16()
        for i in range(2**REG_BITS):
            target.registers[i] = 1024
        target.registers[rA] = a
        target.registers[rB] = b

        instr = AsmInstruction(OpCode.BARREL, r_A=rA, r_B=rB, r_C=rC)
        target.instruction_register = instr.to_int()

        target.execute_instruction()
        assert target.registers[rA] == a
        assert target.registers[rB] == b
        assert target.registers[rC] == ba2int(c_bits)

    @pytest.mark.parametrize("rC", [0, 5, 15])
    @pytest.mark.parametrize("rB", [7, 8, 14])
    @pytest.mark.parametrize("rA", [9, 11, 12])
    @pytest.mark.parametrize("a", [0, 1, 254, 65535])
    def test_no_op(self, rA: int, rB: int, rC: int, a: int) -> None:
        target = SlothPU16()
        for i in range(2**REG_BITS):
            target.registers[i] = 1024
        target.registers[rA] = a
        target.registers[rB] = 0  # So no shift

        instr = AsmInstruction(OpCode.BARREL, r_A=rA, r_B=rB, r_C=rC)
        target.instruction_register = instr.to_int()

        target.execute_instruction()
        assert target.registers[rA] == a
        assert target.registers[rB] == 0
        assert target.registers[rC] == a


class TestLoadB:
    def test_smoke(self) -> None:
        target = SlothPU16()

        mem_offset = 16384
        for i in range(3):
            target.memory[mem_offset + i] = i + 1

        rC = 15
        rA = 12

        for i in range(3):
            instr = AsmInstruction(OpCode.LOADB, r_A=rA, r_B=None, r_C=rC)
            target.instruction_register = instr.to_int()
            target.registers[rA] = mem_offset + i
            target.execute_instruction()
            assert target.registers[rC] == i + 1


class TestLoadW:
    def test_smoke(self) -> None:
        target = SlothPU16()

        mem_offset = 16384
        for i in range(3):
            target.memory[mem_offset + i] = i + 11

        rC = 14
        rA = 5

        instr = AsmInstruction(OpCode.LOADW, r_A=rA, r_B=None, r_C=rC)

        target.instruction_register = instr.to_int()
        target.registers[rA] = mem_offset
        target.execute_instruction()
        assert target.registers[rC] == 11 + (256 * 12)

        target.instruction_register = instr.to_int()
        target.registers[rA] = mem_offset + 2
        target.execute_instruction()
        assert target.registers[rC] == 13


class TestStoreB:
    @pytest.mark.parametrize("rB", [7, 8, 14])
    @pytest.mark.parametrize("rA", [9, 11, 12])
    @pytest.mark.parametrize("a", [0, 1, 254, 255, 256, 65535])
    @pytest.mark.parametrize("b", [0, 1, 254, 255, 256, 517, 65535])
    def test_smoke(self, rA: int, rB: int, a: int, b: int) -> None:
        target = SlothPU16()
        for i in range(2**REG_BITS):
            target.registers[i] = 1024
        target.registers[rA] = a
        target.registers[rB] = b

        instr = AsmInstruction(OpCode.STOREB, r_A=rA, r_B=rB, r_C=None)
        target.instruction_register = instr.to_int()

        target.execute_instruction()
        assert target.memory[a] == b % 256


class TestStoreW:
    @pytest.mark.parametrize("rB", [7, 8, 14])
    @pytest.mark.parametrize("rA", [9, 11, 12])
    @pytest.mark.parametrize("a", [0, 2, 254, 256, 32768])
    @pytest.mark.parametrize("b", [0, 1, 254, 255, 256, 517, 65535])
    def test_smoke(self, rA: int, rB: int, a: int, b: int) -> None:
        target = SlothPU16()
        for i in range(2**REG_BITS):
            target.registers[i] = 1024
        target.registers[rA] = a
        target.registers[rB] = b

        instr = AsmInstruction(OpCode.STOREW, r_A=rA, r_B=rB, r_C=None)
        target.instruction_register = instr.to_int()

        target.execute_instruction()
        assert target.memory.get_word(a) == b


class TestLoadPC:
    def test_smoke(self) -> None:
        target = SlothPU16()

        for i in range(2**REG_BITS):
            instr = AsmInstruction(OpCode.LOADPC, r_A=None, r_B=None, r_C=i)
            target.instruction_register = instr.to_int()
            target.execute_instruction()

        for i in range(2**REG_BITS):
            assert target.registers[i] == 2 * i


class TestBranchZero:
    @pytest.mark.parametrize("rB", [7, 8, 14])
    @pytest.mark.parametrize("rA", [9, 11, 12])
    @pytest.mark.parametrize("a", [0, 254, 256, 32768])
    @pytest.mark.parametrize("b", [1, 2, 254, 256, 32768, 65535])
    def test_nobranch(self, rA: int, rB: int, a: int, b: int) -> None:
        target = SlothPU16()
        for i in range(2**REG_BITS):
            target.registers[i] = 1024
        target.registers[rA] = a
        target.registers[rB] = b

        instr = AsmInstruction(OpCode.BRANCHZERO, r_A=rA, r_B=rB, r_C=None)
        target.instruction_register = instr.to_int()

        assert target.program_counter == 0
        target.execute_instruction()
        assert target.program_counter == 2

    @pytest.mark.parametrize("rB", [7, 8, 14])
    @pytest.mark.parametrize("rA", [9, 11, 12])
    @pytest.mark.parametrize("a", [0, 254, 256, 32768])
    def test_branch(self, rA: int, rB: int, a: int) -> None:
        target = SlothPU16()
        for i in range(2**REG_BITS):
            target.registers[i] = 1024
        target.registers[rA] = a
        target.registers[rB] = 0

        instr = AsmInstruction(OpCode.BRANCHZERO, r_A=rA, r_B=rB, r_C=None)
        target.instruction_register = instr.to_int()

        assert target.program_counter == 0
        target.execute_instruction()
        assert target.program_counter == a
