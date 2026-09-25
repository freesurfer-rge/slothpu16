import pytest
from pyslothpu16_core import N_BITS
from pyslothpu16_emulator import MainMemory


@pytest.mark.parametrize("loc", [0, 1, 65535])
@pytest.mark.parametrize("value", [0, 1, 255])
def test_set_retrieve(loc: int, value: int):
    mm = MainMemory()
    for i in range(2**N_BITS):
        assert mm[i] == 0

    mm[loc] = value

    for i in range(2**N_BITS):
        if i == loc:
            assert mm[i] == value
        else:
            assert mm[i] == 0


@pytest.mark.parametrize("bad_value", [-1, 256])
def test_badvalue(bad_value: int):
    mm = MainMemory()
    expected_msg = f"Value out of range: {bad_value}"
    with pytest.raises(ValueError) as ve:
        mm[0] = bad_value
    assert ve.value.args[0] == expected_msg
