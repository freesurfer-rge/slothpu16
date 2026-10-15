from pyslothpu16_emulator import SlothPU16
from textual.app import App, ComposeResult
from textual.containers import Horizontal, ScrollableContainer, Vertical
from textual.widgets import Footer, Header

from ._widgets import InstructionRegister, ProgramCounter


class SlothPU16App(App[None]):
    CSS_PATH = "app.tcss"
    BINDINGS = [("space", "step", "Step")]

    def __init__(
        self,
        slothpu16: SlothPU16,
    ) -> None:
        super().__init__()
        self._slothpu16 = slothpu16

    def action_step(self) -> None:
        """Advance the emulator and refresh the register display."""
        self._slothpu16.advance()
        self.query_one(ProgramCounter).refresh_value()
        self.query_one(InstructionRegister).refresh_value()

    def compose(self) -> ComposeResult:
        """Compose the application layout."""
        yield Header()

        with Horizontal(id="main-divide"):
            with Vertical(id="register-area"):
                yield ProgramCounter(self._slothpu16)
                yield InstructionRegister(self._slothpu16)
            with ScrollableContainer(id="main-memory"):
                pass

        yield Footer()
