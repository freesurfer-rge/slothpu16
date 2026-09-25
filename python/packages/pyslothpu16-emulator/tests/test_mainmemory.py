import pytest

from pyslothpu16_emulator import MainMemory

@pytest.mark.parametrize("bad_value", [-1, 256])
def test_badvalue(bad_value: int):
    mm = MainMemory()
    mm[0] = bad_value