from typing import Dict, List, Union

import bitarray
import bitarray.util
import pytest

from tester_board import TesterBoard

N_BITS = 16


class BarrelShifterConnectorBoard:
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
            A=list(range(N_BITS)),
            B=[i + 16 for i in range(4)],
            OE=38,
        )
        return op

    @property
    def Input_Pins(self) -> Dict[str, Union[int, List[int]]]:
        ip = dict(C=[i + 24 for i in range(N_BITS)])
        return ip

    def recv(self):
        self._inputs = self._tb.recv()

    def send(self):
        self._tb.send(self._outputs)

    def write_A(self, value: bitarray.bitarray):
        assert len(value) == N_BITS

        for i in range(N_BITS):
            self._outputs[self.Output_Pins["A"][i]] = value[i]
        self.send()

    def write_B(self, value: int):
        assert value >= 0 and value < N_BITS

        converted = bitarray.util.int2ba(value, length=4, endian="little")
        for i, curr_bit in enumerate(converted):
            self._outputs[self.Output_Pins["B"][i]] = converted[i]
        self.send()

    def read_C(self) -> bitarray.bitarray:
        self.recv()
        result = bitarray.bitarray(N_BITS, endian="little")
        for i, pin in enumerate(self.Input_Pins["C"]):
            result[i] = self._inputs[pin]
        return result

    def OE(self, value: bool):
        self._outputs[self.Output_Pins["OE"]] = value
        self.send()


pwr_2 = [2 ** x for x in range(16)]


all_A_vals = pwr_2
all_B_vals = list(range(8))


class TestBarrelShifter:
    def test_smoke(self):
        bscb = BarrelShifterConnectorBoard()

        input = bitarray.util.zeros(N_BITS, endian="little")
        expected = bitarray.util.zeros(N_BITS, endian="little")
        input[1] = True
        expected[2] = True

        bscb.write_A(input)
        bscb.write_B(1)

        bscb.OE(False)
        result = bscb.read_C()
        assert result == expected

        bscb.OE(True)
        result = bscb.read_C()
        assert result == bitarray.util.zeros(N_BITS, endian="little")

    @pytest.mark.parametrize("A_val", all_A_vals)
    @pytest.mark.parametrize("B_val", all_B_vals)
    def test_all(self, A_val, B_val):
        bscb = BarrelShifterConnectorBoard()

        A = bitarray.util.int2ba(A_val, endian="little", length=N_BITS)
        expected = bitarray.util.zeros(N_BITS, endian="little")

        for i in range(N_BITS):
            expected[(i + B_val) % N_BITS] = A[i]

        bscb.write_A(A)
        bscb.write_B(B_val)

        bscb.OE(False)
        result = bscb.read_C()
        assert result == expected

        bscb.OE(True)
        result = bscb.read_C()
        assert result == bitarray.util.zeros(N_BITS, endian="little")
