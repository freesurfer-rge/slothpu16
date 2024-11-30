from typing import Dict, List, Union

import bitarray.util
import pytest

from tester_board import TesterBoard

class IncrementerConnectorBoard:
    def __init__(self):
        """Initialise with an internal Testerboard."""
        self._tb = TesterBoard()

        # Start with all outputs disabled
        self._tb.enable_outputs([False for _ in range(5)])

        # Set all outputs low
        self._outputs = [0 for _ in range(self._tb.n_pins)]
        self.send()
        self._tb.enable_outputs([True for _ in range(5)])

        self.recv()

    @property
    def Output_Pins(self) -> Dict[str, Union[int, List[int]]]:
        op = dict(
            IncIn=[18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33],
            Increment=[14,15,16,17],
            OE=35,
        )
        return op

    @property
    def Input_Pins(self) -> Dict[str, Union[int, List[int]]]:
        ip = dict(
            IncOut=[2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17],
        )
        return ip

    def recv(self):
        self._inputs = self._tb.recv()

    def send(self):
        self._tb.send(self._outputs)

    def write_incrementer(self, value: int):
        assert isinstance(value, int)
        assert value >= 0
        assert value < 65536

        converted = bitarray.util.int2ba(value, length=16, endian="little")
        for i, curr_bit in enumerate(converted):
            self._outputs[self.Output_Pins["IncIn"][i]] = curr_bit
        self.send()

    def read_incrementer(self) -> int:
        self.recv()
        vals = []

        for p in self.Input_Pins["IncOut"]:
            vals.append(self._inputs[p])

        value = bitarray.util.ba2int(bitarray.bitarray(vals, endian="little"))
        return value

    def write_inc_value(self, pin: int):
        assert pin>=0 and pin<=3

        for i in range(4):
            self._outputs[self.Output_Pins["Increment"][i]] = (pin==i)
        self.send()
    
    def OE(self, value: bool):
        self._outputs[self.Output_Pins["OE"]] = value
        self.send()

pwr_2 = [2 ** x for x in range(16)]
pwr_2_off = [65535 - 2 ** x for x in range(16)]
pwr_2_off_2 = [65536 - 2 ** x for x in range(16)]
others = [ 23, 52, 81, 88, 1236, 1237, 1820, 6703, 6710, 15023, 17022, 20123, 25318, 48181, 53122, 50049, 60099, 63182]

all_vals = pwr_2 + pwr_2_off+  pwr_2_off_2

class TestIncrementer:
    def test_smoke(self):
        icb = IncrementerConnectorBoard()

        icb.write_incrementer(10)
        icb.write_inc_value(0)
        icb.OE(False)
        result = icb.read_incrementer()

        assert result == 11
        icb.OE(True)
        result = icb.read_incrementer()
        assert result == 0

    @pytest.mark.parametrize("value", all_vals)
    @pytest.mark.parametrize("inc_pwr", range(4))
    def test_full(self, value:int, inc_pwr:int):
        icb = IncrementerConnectorBoard()

        inc_amt = 2**inc_pwr

        icb.write_incrementer(value)
        icb.write_inc_value(inc_pwr)
        icb.OE(False)
        result = icb.read_incrementer()
        assert result == (value + inc_amt)%65536

        icb.OE(True)
        result = icb.read_incrementer()
        assert result == 0
