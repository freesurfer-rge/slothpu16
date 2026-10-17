from pathlib import Path

import pytest
from textual.widgets import Static

from pyslothpu16_emulator import SlothPU16
from pyslothpu16_ui._widgets import RegisterFile
from pyslothpu16_ui.app import SlothPU16App


@pytest.mark.asyncio
async def test_register_file_updates_after_step(sample_program_dir: Path) -> None:
    asm_file = sample_program_dir / "set_one_register.slothpu16"
    app = SlothPU16App(SlothPU16(asm_file=asm_file))

    async with app.run_test() as pilot:
        register_file = app.query_one(RegisterFile)
        register_0 = register_file.query_one("#register-0", Static)
        assert str(register_0.render()) == " 0: 0000000000000000     0"

        await pilot.press("space")

        assert str(register_0.render()) == " 0: 1000000000000000     1"
