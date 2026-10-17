from pathlib import Path

import pytest
from pyslothpu16_emulator import SlothPU16
from pyslothpu16_ui._widgets import ProgramCounter
from pyslothpu16_ui.app import SlothPU16App


@pytest.mark.asyncio
async def test_program_counter_updates_after_step(sample_program_dir: Path) -> None:
    asm_file = sample_program_dir / "set_one_register.slothpu16"
    app = SlothPU16App(SlothPU16(asm_file=asm_file))

    async with app.run_test() as pilot:
        counter = app.query_one(ProgramCounter)
        assert str(counter.render()) == "Program Counter: 0"

        await pilot.press("space")

        assert str(counter.render()) == "Program Counter: 2"
