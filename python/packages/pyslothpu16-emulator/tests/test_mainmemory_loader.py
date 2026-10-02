from pathlib import Path

from pyslothpu16_core import AsmInstruction, OpCode
from pyslothpu16_emulator import mainmemory_from_file

SAMPLE_PROGRAM_DIR = Path(__file__).parent / "sample_programs"


def test_set_one_register():
    target = SAMPLE_PROGRAM_DIR / "set_one_register.slothpu16"
    assert target.exists(), f"Not found: {target}"

    result = mainmemory_from_file(target)

    instr0 = AsmInstruction.from_int(result.get_word(0))
    assert instr0.opcode == OpCode.SET
    assert instr0.value_to_set == 1
    assert instr0.r_C == 0

    instr0 = AsmInstruction.from_int(result.get_word(2))
    assert instr0.opcode == OpCode.HALT
