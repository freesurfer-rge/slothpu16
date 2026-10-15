from pyslothpu16_core import AsmInstruction, OpCode
from pyslothpu16_emulator import SlothPU16
from textual.app import ComposeResult
from textual.containers import Vertical
from textual.widgets import Static


class SlothPU16Widget:  # noqa: B903
    def __init__(self, spu16: SlothPU16) -> None:
        self._spu16 = spu16


class ProgramCounter(Static, SlothPU16Widget):
    def __init__(self, spu16: SlothPU16) -> None:
        SlothPU16Widget.__init__(self, spu16)
        super().__init__(
            self._display_text(),
            id="program-counter",
        )
        self.border_title = "Program Counter"

    def refresh_value(self) -> None:
        self.update(self._display_text())

    def _display_text(self) -> str:
        return f"Program Counter: {self._spu16.program_counter}"


class InstructionRegister(Vertical, SlothPU16Widget):
    def __init__(self, spu16: SlothPU16) -> None:
        SlothPU16Widget.__init__(self, spu16)
        super().__init__(
            id="instruction-register",
        )
        self.border_title = "Instruction Register"

    def _display_values(self) -> dict[str, str]:
        instruction = AsmInstruction.from_int(self._spu16.instruction_register)

        values = {
            "opcode": f"Opcode: {instruction.opcode.name}",
            "r-a": f"A: {self._format_register(instruction.r_A)}",
            "r-b": f"B: {self._format_register(instruction.r_B)}",
            "r-c": f"C: {self._format_register(instruction.r_C)}",
            "value": "Value to set: -",
        }
        if instruction.opcode == OpCode.SET:
            values["value"] = f"Value to set: {instruction.value_to_set}"

        return values

    def compose(self) -> ComposeResult:
        for field, text in self._display_values().items():
            yield Static(text, id=self._get_fieldname(field))

    def refresh_value(self) -> None:
        for field, text in self._display_values().items():
            self.query_one(f"#{self._get_fieldname(field)}", Static).update(text)

    def _get_fieldname(self, base: str) -> str:
        return f"instruction-{base}"

    @staticmethod
    def _format_register(register: int | None) -> str:
        return f"{register}" if register is not None else "-"
