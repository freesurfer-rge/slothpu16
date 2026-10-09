from pathlib import Path

from pyslothpu16_core import N_BITS, AsmInstruction


class MainMemory:
    def __init__(self):
        self._locs: list[int] = [0] * (2**N_BITS)

    def __getitem__(self, key: int) -> int:
        return self._locs[key]

    def __setitem__(self, key: int, value: int) -> None:
        if value < 0 or value > 255:
            raise ValueError(f"Value out of range: {value}")
        self._locs[key] = value

    def get_word(self, key: int) -> int:
        if key % 2 != 0:
            raise ValueError(f"Non-alighted read: {key}")

        lb = self._locs[key]
        ub = self._locs[key + 1]

        return lb + (256 * ub)

    def set_word(self, key: int, value: int) -> None:
        if key % 2 != 0:
            raise ValueError(f"Non-alighted write: {key}")
        if value < 0 or value >= 2**N_BITS:
            raise ValueError(f"Value out of range: {value}")

        ub, lb = divmod(value, 256)
        self[key] = lb
        self[key + 1] = ub


def mainmemory_from_file(file_path: Path) -> MainMemory:
    result = MainMemory()

    with open(file_path, "r", encoding="utf-8-sig") as asm_file:
        instr_count = 0
        for line in asm_file:
            stripped_line = line.strip()
            if len(stripped_line) == 0 or stripped_line[0] == "#":
                continue
            trimmed_line = stripped_line.split("#")[0]
            asm_instr = AsmInstruction.from_str(trimmed_line)
            result.set_word(2 * instr_count, asm_instr.to_int())
            instr_count += 1

    return result
