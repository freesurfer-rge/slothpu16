from pathlib import Path

import pytest
from pyslothpu16_emulator import SlothPU16
from pyslothpu16_ui._widgets import InstructionRegister
from pyslothpu16_ui.app import SlothPU16App
from textual.widgets import Static


@pytest.mark.asyncio
async def test_program_counter_updates_after_step(sample_program_dir: Path) -> None:
    asm_file = sample_program_dir / "set_one_register.slothpu16"
    app = SlothPU16App(SlothPU16(asm_file=asm_file))

    async with app.run_test() as pilot:
        ir = app.query_one(InstructionRegister)

        opcode_str = str(ir.query_one("#instruction-opcode", Static).render())
        assert opcode_str == "Opcode: SET"

        reg_str = str(ir.query_one("#instruction-r-a", Static).render())
        assert reg_str == "A: 1"
        reg_str = str(ir.query_one("#instruction-r-b", Static).render())
        assert reg_str == "B: 0"
        reg_str = str(ir.query_one("#instruction-r-c", Static).render())
        assert reg_str == "C: 0"

        value_string = str(ir.query_one("#instruction-value", Static).render())
        assert value_string == "Value to set: 1"

        # =============
        await pilot.press("space")

        opcode_str = str(ir.query_one("#instruction-opcode", Static).render())
        assert opcode_str == "Opcode: HALT"
