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


@pytest.mark.parametrize("loc", [0, 2, 256, 32768, 65534])
@pytest.mark.parametrize("value", [0, 1, 255, 256, 1023, 1024, 65535])
def test_set_retrieve_word(loc: int, value: int):
    mm = MainMemory()
    for i in range(2**N_BITS):
        assert mm[i] == 0

    mm.set_word(loc, value)
    for i in range(2**N_BITS):
        if i == loc:
            assert mm.get_word(i) == value
            assert mm[i] == value % 256
        elif i == loc + 1:
            assert mm[i] == value // 256
        else:
            assert mm[i] == 0


@pytest.mark.parametrize("bad_value", [-1, 256])
def test_badvalue(bad_value: int):
    mm = MainMemory()
    expected_msg = f"Value out of range: {bad_value}"
    with pytest.raises(ValueError) as ve:
        mm[0] = bad_value
    assert ve.value.args[0] == expected_msg


@pytest.mark.parametrize("bad_loc", [-1, 1, 65535])
def test_word_bad_loc_set(bad_loc: int):
    mm = MainMemory()
    expected_msg = f"Non-alighted write: {bad_loc}"
    with pytest.raises(ValueError) as ve:
        mm.set_word(bad_loc, 65535)
    assert ve.value.args[0] == expected_msg


@pytest.mark.parametrize("bad_loc", [-1, 1, 65535])
def test_word_bad_loc_get(bad_loc: int):
    mm = MainMemory()
    expected_msg = f"Non-alighted read: {bad_loc}"
    with pytest.raises(ValueError) as ve:
        mm.get_word(bad_loc)
    assert ve.value.args[0] == expected_msg


@pytest.mark.parametrize("bad_value", [-1, 65536])
def test_word_badvalue(bad_value: int):
    mm = MainMemory()
    expected_msg = f"Value out of range: {bad_value}"
    with pytest.raises(ValueError) as ve:
        mm.set_word(12, bad_value)
    assert ve.value.args[0] == expected_msg
