import pytest
from pyslothpu16_core import OpCode


def test_from_str():
    target = "add"
    expected = OpCode.ADD

    assert OpCode.from_str(target) == expected


def test_from_str_unknown():
    target = "mul"

    with pytest.raises(ValueError) as ve:
        _ = OpCode.from_str(target)
    assert ve.value.args[0] == "Invalid opcode: mul"
