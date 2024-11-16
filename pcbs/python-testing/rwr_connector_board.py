import time

from typing import Dict, List, Union

import bitarray.util

from tester_board import TesterBoard


class RWRConnectorBoard:
    def __init__(self):
        """Initialise with an internal Testerboard."""
        self._tb = TesterBoard()

        # Start with all outputs disabled
        self._tb.enable_outputs([False for _ in range(5)])

        # Set all outputs low except for Reset
        self._outputs = [i==self.Output_Pins["Reset"] for i in range(self._tb.n_pins)]
        self.send()
        self._tb.enable_outputs([True for _ in range(5)])

        # Read in the inputs
        self.recv()

    @property
    def Output_Pins(self) -> Dict[str, Union[int, List[int]]]:
        op = dict(
            RegIn=[2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17],
            Reset=19,
            Clock=21,
            OE=39,
        )
        return op

    @property
    def Input_Pins(self) -> Dict[str, Union[int, List[int]]]:
        ip = dict(
            RegOut=[22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37],
        )
        return ip

    def recv(self):
        self._inputs = self._tb.recv()

    def send(self):
        self._tb.send(self._outputs)

    def write_register(self, value: int):
        assert isinstance(value, int)
        assert value >= 0
        assert value < 65536

        converted = bitarray.util.int2ba(value, length=16, endian="little")
        for i, curr_bit in enumerate(converted):
            self._outputs[self.Output_Pins["RegIn"][i]] = curr_bit
        self.send()

    def read_register(self) -> int:
        time.sleep(0.001)
        self.recv()
        vals = []
        for p in self.Input_Pins["RegOut"]:
            vals.append(self._inputs[p])

        value = bitarray.util.ba2int(bitarray.bitarray(vals, endian="little"))
        return value

    def Reset(self):
        self._outputs[self.Output_Pins["Reset"]] = False
        self.send()
        time.sleep(0.5)
        self._outputs[self.Output_Pins["Reset"]] = True
        self.send()

    def OE(self, value: bool):
        self._outputs[self.Output_Pins["OE"]] = value
        self.send()

    def Clock(self, value: bool):
        self._outputs[self.Output_Pins["Clock"]] = value
        self.send()
