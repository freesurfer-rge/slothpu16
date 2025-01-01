from typing import Dict, List, Union

import bitarray
import bitarray.util
import pytest

from tester_board import TesterBoard

N_BITS = 8

class NandXorALUBoard:
    def __init__(self):
        """Initialise with an internal Testerboard."""
        self._tb = TesterBoard()

        # Start with all outputs disabled
        self._tb.enable_outputs([False for _ in range(5)])

        # Set all outputs low
        self._outputs = [0 for _ in range(self._tb.n_pins)]
        self.send()
        self._tb.enable_outputs([True for _ in range(5)])

        # Except NAND and XOR
        self.NAND(True)
        self.XOR(True)

        self.recv()

    @property
    def Output_Pins(self) -> Dict[str, Union[int, List[int]]]:
        op = dict(
            A=[0 + i for i in range(N_BITS)],
            B=[16 + i for i in range(N_BITS)],
            NAND=36,
            XOR=37,
        )
        return op

    @property
    def Input_Pins(self) -> Dict[str, Union[int, List[int]]]:
        ip = dict(C=[32 + i for i in range(N_BITS)])
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

    def NAND(self, value: bool):
        self._outputs[self.Output_Pins["NAND"]] = value
        self.send()

    def XOR(self, value: bool):
        self._outputs[self.Output_Pins["XOR"]] = value
        self.send()

        
    def read_C(self) -> bitarray.bitarray:
        self.recv()
        result = bitarray.bitarray(N_BITS, endian="little")
        for i, pin in enumerate(self.Input_Pins["C"]):
            result[i] = self._inputs[pin]

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

all_vals = pwr_2 # + pwr_2_off + pwr_2_off_2 + others

class TestXorNand:
    @pytest.mark.parametrize("a", all_vals)
    @pytest.mark.parametrize("b", all_vals)
    def test_nand(self, a: int, b: int):
        nxcb = NandXorALUBoard()

        a_bits = bitarray.util.int2ba(a, length=N_BITS, endian="little")
        b_bits = bitarray.util.int2ba(b, length=N_BITS, endian="little")

        expected = ~(a_bits & b_bits)

        # We are active low for this
        nxcb.NAND(False)

        nxcb.write_A(a_bits)
        nxcb.write_B(b_bits)

        actual = nxcb.read_C()

        assert expected == actual

    @pytest.mark.parametrize("a", all_vals)
    @pytest.mark.parametrize("b", all_vals)
    def test_xor(self, a: int, b: int):
        nxcb = NandXorALUBoard()

        a_bits = bitarray.util.int2ba(a, length=N_BITS, endian="little")
        b_bits = bitarray.util.int2ba(b, length=N_BITS, endian="little")

        expected = a_bits ^ b_bits

        # We are active low for this
        nxcb.XOR(False)

        nxcb.write_A(a_bits)
        nxcb.write_B(b_bits)

        actual = nxcb.read_C()

        assert expected == actual
