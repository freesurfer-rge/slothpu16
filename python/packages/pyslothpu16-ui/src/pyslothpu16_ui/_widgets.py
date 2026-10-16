from bitarray.util import int2ba
from pyslothpu16_core import N_BITS, AsmInstruction, OpCode
from pyslothpu16_emulator import SlothPU16
from rich.text import Text
from textual.app import ComposeResult
from textual.containers import Vertical
from textual.widgets import DataTable, Static


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


class RegisterFile(Vertical, SlothPU16Widget):
    def __init__(self, spu16: SlothPU16) -> None:
        SlothPU16Widget.__init__(self, spu16)
        super().__init__(
            id="register-file",
        )
        self.border_title = "Register File"

    def compose(self) -> ComposeResult:
        for r_i, text in enumerate(self._display_values()):
            yield Static(text, id=self._get_fieldname(r_i))

    def refresh_value(self) -> None:
        for r_i, text in enumerate(self._display_values()):
            self.query_one(f"#{self._get_fieldname(r_i)}", Static).update(text)

    def _display_values(self) -> list[str]:
        result = [
            f"{i:>2d}: {self._format_register(r)}" for (i, r) in enumerate(self._spu16.registers)
        ]
        return result

    @staticmethod
    def _get_fieldname(reg: int) -> str:
        return f"register-{reg}"

    @staticmethod
    def _format_register(reg: int) -> str:
        ba = int2ba(reg, length=N_BITS, endian="little")
        return f"{ba.to01()} {reg:>5d}"


class MainMemory(DataTable, SlothPU16Widget):
    BYTES_PER_ROW = 8

    def __init__(self, spu16: SlothPU16) -> None:
        SlothPU16Widget.__init__(self, spu16)
        super().__init__(
            id="main-memory",
        )
        self.border_title = "Main Memory"
        self._values = list(self._spu16.memory)
        assert len(self._values) % MainMemory.BYTES_PER_ROW == 0

    def on_mount(self) -> None:
        self.add_columns(*[str(i) for i in range(self.BYTES_PER_ROW)])
        for idx in range(0, len(self._values), self.BYTES_PER_ROW):
            label = Text(str(idx))
            row_strs = [self._format_byte(v) for v in self._values[idx : idx + self.BYTES_PER_ROW]]
            self.add_row(*row_strs, label=label)

    @staticmethod
    def _format_byte(value: int) -> str:
        # ba = int2ba(value, length=8, endian="little")
        return f"{value:>3d}"
