from pyslothpu16_core import AsmInstruction, OpCode
from pyslothpu16_emulator import SlothPU16


def test_smoke(sample_program_dir) -> None:
    smoke_program = sample_program_dir / "set_one_register.slothpu16"
    assert smoke_program.exists(), f"Not found: {smoke_program}"
    target = SlothPU16(asm_file=smoke_program)

    nxt_instr = AsmInstruction.from_int(target.instruction_register)
    assert nxt_instr.opcode == OpCode.SET
    assert nxt_instr.value_to_set == 1
    assert nxt_instr.r_C == 0
