from typing import Dict, List, Union

import bitarray
import bitarray.util
import pytest

from tester_board import TesterBoard

N_BITS = 16
OUT_BITS = 8


class ComparatorALUBoard:
    def __init__(self):
        """Initialise with an internal Testerboard."""
        self._tb = TesterBoard()

        # Start with all outputs disabled
        self._tb.enable_outputs([False for _ in range(5)])

        # Set all outputs low
        self._outputs = [0 for _ in range(self._tb.n_pins)]
        self.send()
        self._tb.enable_outputs([True for _ in range(5)])

        # Except Compare
        self.Compare(True)

        self.recv()

    @property
    def Output_Pins(self) -> Dict[str, Union[int, List[int]]]:
        op = dict(
            A=[0 + i for i in range(N_BITS)],
            B=[16 + i for i in range(N_BITS)],
            COMPARE=33,
        )
        return op

    @property
    def Input_Pins(self) -> Dict[str, Union[int, List[int]]]:
        ip = dict(C=[32 + i for i in range(OUT_BITS)])
        return ip

    def recv(self):
        self._inputs = self._tb.recv()

    def send(self):
        self._tb.send(self._outputs)

    def _write_bus(self, value: bitarray.bitarray, name: str):
        assert len(value) == N_BITS

        for i, curr_bit in enumerate(value):
            self._outputs[self.Output_Pins[name][i]] = value[i]
        self.send()

    def write_A(self, value: bitarray.bitarray):
        self._write_bus(value, "A")

    def write_B(self, value: bitarray.bitarray):
        self._write_bus(value, "B")

    def Compare(self, value: bool):
        self._outputs[self.Output_Pins["COMPARE"]] = value
        self.send()

    def read_C(self) -> bitarray.bitarray:
        self.recv()
        result = bitarray.bitarray(OUT_BITS, endian="little")
        for i, pin in enumerate(self.Input_Pins["C"]):
            result[i] = self._inputs[pin]

        return result


pwr_2 = [2 ** x for x in range(N_BITS)]
pwr_2_off = [(2 ** N_BITS) - 1 - 2 ** x for x in range(N_BITS)]
pwr_2_off_2 = [(2 ** N_BITS) - 2 - 2 ** x for x in range(N_BITS)]
others = [0, 23, 52, 81, 88, 231, 1877, 2798, 4131, 7931, 15158, 25873, 29787, 30001]

all_vals = pwr_2 + pwr_2_off + pwr_2_off_2 + others


class TestCompare:
    @pytest.mark.parametrize("a", all_vals)
    @pytest.mark.parametrize("b", all_vals)
    def test_compare(self, a: int, b: int):
        ccb = ComparatorALUBoard()

        a_bits = bitarray.util.int2ba(a, length=N_BITS, endian="little")
        b_bits = bitarray.util.int2ba(b, length=N_BITS, endian="little")

        expected = bitarray.util.int2ba(2, length=OUT_BITS, endian="little")
        if a < b:
            expected = bitarray.util.int2ba(1, length=OUT_BITS, endian="little")
        if a > b:
            expected = bitarray.util.int2ba(4, length=OUT_BITS, endian="little")

        # We are active low for this
        ccb.Compare(False)

        ccb.write_A(a_bits)
        ccb.write_B(b_bits)

        actual = ccb.read_C()

        assert expected == actual

        # Make sure we turn off
        ccb.Compare(True)
        zeros = bitarray.util.int2ba(0, length=OUT_BITS, endian="little")
        assert zeros == ccb.read_C()
