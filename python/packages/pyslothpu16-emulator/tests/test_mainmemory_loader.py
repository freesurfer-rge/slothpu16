from pathlib import Path

from pyslothpu16_core import AsmInstruction, OpCode
from pyslothpu16_emulator import mainmemory_from_file


def test_set_one_register(sample_program_dir: Path):
    target = sample_program_dir / "set_one_register.slothpu16"
    assert target.exists(), f"Not found: {target}"

    result = mainmemory_from_file(target)

    instr0 = AsmInstruction.from_int(result.get_word(0))
    assert instr0.opcode == OpCode.SET
    assert instr0.value_to_set == 1
    assert instr0.r_C == 0

    instr0 = AsmInstruction.from_int(result.get_word(2))
    assert instr0.opcode == OpCode.HALT
