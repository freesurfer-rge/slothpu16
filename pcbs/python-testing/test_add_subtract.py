from typing import Dict, List, Union

import bitarray
import bitarray.util
import pytest

from tester_board import TesterBoard

N_BITS = 8


class AddSubtractALUBoard:
    def __init__(self):
        """Initialise with an internal Testerboard."""
        self._tb = TesterBoard()

        # Start with all outputs disabled
        self._tb.enable_outputs([False for _ in range(5)])

        # Set all outputs low
        self._outputs = [0 for _ in range(self._tb.n_pins)]
        self.send()
        self._tb.enable_outputs([True for _ in range(5)])

        # Except Add and Subtract
        self.Add(True)
        self.Subtract(True)

        self.recv()

    @property
    def Output_Pins(self) -> Dict[str, Union[int, List[int]]]:
        op = dict(
            A=[0 + i for i in range(N_BITS)],
            B=[16 + i for i in range(N_BITS)],
            CarryIn=32,
            ADD=34,
            SUB=35,
        )
        return op

    @property
    def Input_Pins(self) -> Dict[str, Union[int, List[int]]]:
        ip = dict(C=[32 + i for i in range(N_BITS)], CarryOut=15)
        return ip

    def recv(self):
        self._inputs = self._tb.recv()

    def send(self):
        self._tb.send(self._outputs)

    def _write_bus(self, value: int, name: str):
        assert value >= 0 and value < 2 ** N_BITS

        converted = bitarray.util.int2ba(value, length=N_BITS, endian="little")
        for i, curr_bit in enumerate(converted):
            self._outputs[self.Output_Pins[name][i]] = converted[i]
        self.send()

    def write_A(self, value: int):
        self._write_bus(value, "A")

    def write_B(self, value: int):
        self._write_bus(value, "B")

    def carry_in(self, value: bool):
        self._outputs[self.Output_Pins["CarryIn"]] = value
        self.send()

    def Add(self, value: bool):
        self._outputs[self.Output_Pins["ADD"]] = value
        self.send()

    def Subtract(self, value: bool):
        self._outputs[self.Output_Pins["SUB"]] = value
        self.send()

    def read_C(self) -> int:
        self.recv()
        result = bitarray.bitarray(N_BITS, endian="little")
        for i, pin in enumerate(self.Input_Pins["C"]):
            result[i] = self._inputs[pin]

        return bitarray.util.ba2int(result)

    def carry_out(self) -> bool:
        self.recv()
        result = self._inputs[self.Input_Pins["CarryOut"]]
        return result


pwr_2 = [2 ** x for x in range(N_BITS)]
pwr_2_off = [255 - 2 ** x for x in range(N_BITS)]
pwr_2_off_2 = [256 - 2 ** x for x in range(N_BITS)]
others = [
    0,
    23,
    52,
    81,
    88,
    231,
]

all_vals = pwr_2 + pwr_2_off + pwr_2_off_2 + others


class TestAddSubtract:
    @pytest.mark.parametrize("a", all_vals)
    @pytest.mark.parametrize("b", all_vals)
    def test_add(self, a: int, b: int):
        ascb = AddSubtractALUBoard()

        expected = a + b
        expected_carry = False
        if expected >= 2 ** N_BITS:
            expected_carry = True
            expected -= 2 ** N_BITS

        # We are active low
        ascb.Add(False)

        ascb.write_A(a)
        ascb.write_B(b)
        ascb.carry_in(False)

        actual = ascb.read_C()
        actual_carry = ascb.carry_out()
        assert actual == expected
        assert actual_carry == expected_carry

        # And the inactive state
        ascb.Add(True)
        assert 0 == ascb.read_C()

    @pytest.mark.parametrize("a", all_vals)
    @pytest.mark.parametrize("b", all_vals)
    def test_subtract(self, a: int, b: int):
        ascb = AddSubtractALUBoard()

        expected = a - b
        expected_carry = True
        if expected < 0:
            expected_carry = False
            expected += 2 ** N_BITS

        # We are active low
        ascb.Subtract(False)

        ascb.write_A(a)
        ascb.write_B(b)
        ascb.carry_in(True)

        actual = ascb.read_C()
        actual_carry = ascb.carry_out()
        assert actual == expected
        assert actual_carry == expected_carry

        # And the inactive state
        ascb.Subtract(True)
        assert 0 == ascb.read_C()
