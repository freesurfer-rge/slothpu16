from pyslothpu16_emulator import SlothPU16
from textual.app import App, ComposeResult
from textual.containers import Horizontal, ScrollableContainer, Vertical
from textual.widgets import Footer, Header, RichLog, Static, TabbedContent, TabPane


class SlothPU16App(App[None]):
    def __init__(
        self,
        slothpu16: SlothPU16,
    ) -> None:
        super().__init__()
        self._slothpu16 = slothpu16

    def compose(self) -> ComposeResult:
        """Compose the application layout."""
        yield Header()

        with Horizontal(id="main-divide"):
            with Vertical(id='register-area'):
                pass
            with ScrollableContainer(id="main-memory"):
                pass

        yield Footer()