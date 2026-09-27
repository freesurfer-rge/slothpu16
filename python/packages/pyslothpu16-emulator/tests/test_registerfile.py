import pytest
from pyslothpu16_core import REG_BITS
from pyslothpu16_emulator import RegisterFile


@pytest.mark.parametrize("loc", range(2**REG_BITS))
@pytest.mark.parametrize("value", [0, 1, 255, 256, 65535])
def test_set_retrieve(loc: int, value: int) -> None:
    rf = RegisterFile()
    for i in range(2**REG_BITS):
        assert rf[i] == 0

    rf[loc] = value

    for i in range(2**REG_BITS):
        if i == loc:
            assert rf[i] == value
        else:
            assert rf[i] == 0


@pytest.mark.parametrize("bad_value", [-1, 65536])
def test_badvalue(bad_value: int) -> None:
    rf = RegisterFile()
    expected_msg = f"Value out of range: {bad_value}"
    with pytest.raises(ValueError) as ve:
        rf[0] = bad_value
    assert ve.value.args[0] == expected_msg
