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

    def _clock_high(self):
        self._outputs[self.Output_Pins["Clock"]] = True
        self.send()

    def _clock_low(self):
        self._outputs[self.Output_Pins["Clock"]] = False
        self.send()

    def Clock(self):
        self._clock_high()
        time.sleep(0.001)
        self._clock_low()

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

all_vals = pwr_2_off + pwr_2_off_2 + others


class TestRegisterFile:
    def test_smoke(self):
        rfcb = RegisterFileConnectorBoard()

        rfcb.Active(False)
        # We go to 16 since these are 'notionally' a
        # bank of 16 registers.
        # Since we only have a single board being tested
        # R8-15 will not be present and always 'read'
        # as zero
        for i in range(16):
            rfcb.R_C(i)
            rfcb.write_C(i)
            rfcb.Clock()

        for i in range(16):
            rfcb.R_A(i)
            b_loc = (i + 1) % 16
            rfcb.R_B(b_loc)

            A_val = rfcb.read_A()
            if i < 8:
                assert A_val == i
            else:
                assert A_val == 0

            B_val = rfcb.read_B()
            if b_loc < 8:
                assert B_val == b_loc
            else:
                assert B_val == 0

    def _check_register(self, i_r, value: int, expected: int):
        # Again, we have the 'low' 8 of a 16 entry file
        if i_r >= 8:
            assert value == 0
        else:
            assert value == expected

    @pytest.mark.parametrize("value", all_vals)
    @pytest.mark.parametrize("reg", range(16))
    @pytest.mark.parametrize("base_val_offset", [0, 1, 127])
    def test_write_single(self, reg: int, value: int, base_val_offset: int):
        rfcb = RegisterFileConnectorBoard()

        rfcb.Active(False)
        # Remember that we have the 'low' 8 of a 16 entry
        # register file
        NUM_REGISTERS = 16

        # Set up
        base_vals = [((2 ** i)+base_val_offset) % 256 for i in range(NUM_REGISTERS)]
        for i in range(NUM_REGISTERS):
            rfcb.R_C(i)
            rfcb.write_C(base_vals[i])
            rfcb.Clock()

        # Set the 'target' register (which may be
        # 'off board')
        rfcb.R_C(reg)
        rfcb.write_C(value)
        rfcb.Clock()

        for i_A in range(NUM_REGISTERS):
            rfcb.R_A(i_A)
            for i_B in range(NUM_REGISTERS):
                rfcb.R_B(i_B)

                A_val = rfcb.read_A()
                B_val = rfcb.read_B()

                if i_A == reg:
                    self._check_register(i_A, A_val, value)
                else:
                    self._check_register(i_A, A_val, base_vals[i_A])

                if i_B == reg:
                    self._check_register(i_B, B_val, value)
                else:
                    self._check_register(i_B, B_val, base_vals[i_B])

                # When board is inactive, should always
                # read '0' (from Tester board pull downs)
                rfcb.Active(True)
                A_val = rfcb.read_A()
                B_val = rfcb.read_B()
                assert A_val == 0
                assert B_val == 0
                rfcb.Active(False)

    def test_no_write_inactive(self):
        rfcb = RegisterFileConnectorBoard()

        rfcb.Active(False)
        # We go to 16 since these are 'notionally' a
        # bank of 16 registers.
        # Since we only have a single board being tested
        # R8-15 will not be present and always 'read'
        # as zero
        for i in range(16):
            rfcb.R_C(i)
            rfcb.write_C(127 + i)
            rfcb.Clock()

        for i in range(16):
            rfcb.R_A(i)
            A_val = rfcb.read_A()
            if i < 8:
                assert A_val == 127 + i
            else:
                assert A_val == 0

        # Make board inactive
        rfcb.Active(True)

        # Write again (should have no effect)
        for i in range(16):
            rfcb.R_C(i)
            rfcb.write_C(i + 8)
            rfcb.Clock()

        # Make active again
        rfcb.Active(False)

        # Read values, which should not
        # be changed
        for i in range(16):
            rfcb.R_A(i)
            A_val = rfcb.read_A()
            if i < 8:
                assert A_val == 127 + i
            else:
                assert A_val == 0
