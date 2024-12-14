import time

from typing import Dict, List, Union

import bitarray
import bitarray.util
import pytest

from tester_board import TesterBoard

N_BITS = 8
N_SEL = 4


class RegisterFileConnectorBoard:
    def __init__(self):
        """Initialise with an internal Testerboard."""
        self._tb = TesterBoard()

        # Start with all outputs disabled
        self._tb.enable_outputs([False for _ in range(5)])

        # Set all outputs low
        self._outputs = [0 for _ in range(self._tb.n_pins)]
        self.send()
        self._tb.enable_outputs([True for _ in range(5)])

        # Except Active
        self.Active(False)

        self.recv()

    @property
    def Output_Pins(self) -> Dict[str, Union[int, List[int]]]:
        op = dict(
            C=[i + 32 for i in range(N_BITS)],
            R_A=[i + 10 for i in range(N_SEL)],
            R_B=[i + 6 for i in range(N_SEL)],
            R_C=[i for i in range(N_SEL)],
            Clock=5,
            Active=4,
        )
        return op

    @property
    def Input_Pins(self) -> Dict[str, Union[int, List[int]]]:
        ip = dict(A=[i + 8 for i in range(N_BITS)], B=[i + 16 for i in range(N_BITS)])
        return ip

    def recv(self):
        self._inputs = self._tb.recv()

    def send(self):
        self._tb.send(self._outputs)

    def Active(self, value: bool):
        self._outputs[self.Output_Pins["Active"]] = value
        self.send()

    def Clock(self):
        self._outputs[self.Output_Pins["Clock"]] = True
        self.send()
        time.sleep(0.001)
        self._outputs[self.Output_Pins["Clock"]] = False
        self.send()

    def _read_bus(self, bus_id: str) -> int:
        self.recv()
        result = bitarray.bitarray(N_BITS, endian="little")
        for i, pin in enumerate(self.Input_Pins[bus_id]):
            result[i] = self._inputs[pin]

        return bitarray.util.ba2int(result)

    def read_A(self) -> int:
        return self._read_bus("A")

    def read_B(self) -> int:
        return self._read_bus("B")

    def write_C(self, value: int):
        assert value >= 0 and value < 256

        converted = bitarray.util.int2ba(value, length=N_BITS, endian="little")
        for i, curr_bit in enumerate(converted):
            self._outputs[self.Output_Pins["C"][i]] = converted[i]
        self.send()

    def _select_register(self, target: int, bus: str):
        # Note that the boards are supposed to be used in pairs, so
        # 16 targets, not 8
        assert target >= 0 and target < 16

        converted = bitarray.util.int2ba(target, length=N_SEL, endian="little")
        for i, curr_bit in enumerate(converted):
            self._outputs[self.Output_Pins[bus][i]] = converted[i]
        self.send()

    def R_A(self, target: int):
        self._select_register(target, "R_A")

    def R_B(self, target: int):
        self._select_register(target, "R_B")

    def R_C(self, target: int):
        self._select_register(target, "R_C")


pwr_2 = [2 ** x for x in range(N_BITS)]


class TestRegisterFile:
    def test_smoke(self):
        rfcb = RegisterFileConnectorBoard()

        rfcb.Active(False)
        for i in range(8):
            rfcb.R_C(i)
            rfcb.write_C(i)
            rfcb.Clock()
