from pyslothpu16_core import N_BITS, REG_BITS


class RegisterFile:
    def __init__(self):
        self._locs: list[int] = [0] * (2**REG_BITS)

    def __getitem__(self, key: int) -> int:
        return self._locs[key]

    def __setitem__(self, key: int, value: int) -> None:
        if value < 0 or value >= 2**N_BITS:
            raise ValueError(f"Value out of range: {value}")
        self._locs[key] = value
