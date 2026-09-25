from pyslothpu16_core import N_BITS


class MainMemory:
    def __init__(self):
        self._locs: list[int] = [0] * (2**N_BITS)

    def __getitem__(self, key: int) -> int:
        return self._locs[key]

    def __setitem__(self, key: int, value: int):
        if value < 0 or value > 255:
            raise ValueError(f"Value out of range: {value}")
        self._locs[key] = value
