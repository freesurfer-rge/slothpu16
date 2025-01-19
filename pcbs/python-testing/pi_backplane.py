from typing import List, Union

import bitarray
import bitarray.util

import RPi.GPIO as GPIO

BUS_WIDTH = 16
CYCLE_WIDTH = 5


class _Output:
    def __init__(self):
        self.n_pins = 80

        self._outputs = [False for _ in range(self.n_pins)]

        # SPI bus clock (SRCLK)
        self._clk_out = 23
        # SPI bus data (DATA)
        self._copi = 19
        # SPI bus select (RCLK)
        self._select_out = 24

        self._enables = dict(A=8, B=3, C=5, Cycle=10, Instruction=7, Clock=11, Reset=12)

        self._buses = dict(
            A=[48 + i for i in range(BUS_WIDTH)],
            B=[32 + i for i in range(BUS_WIDTH)],
            C=[16 + i for i in range(BUS_WIDTH)],
            Instruction=[0 + i for i in range(BUS_WIDTH)],
        )
        self._cycle = [64 + i for i in reversed(range(CYCLE_WIDTH))]

        # Now start the GPIO bits
        GPIO.setmode(GPIO.BOARD)

        # Set up SPI basics
        GPIO.setup(self._clk_out, GPIO.OUT)
        GPIO.output(self._clk_out, GPIO.LOW)
        GPIO.setup(self._copi, GPIO.OUT)
        GPIO.setup(self._copi, GPIO.LOW)
        GPIO.setup(self._select_out, GPIO.OUT)
        GPIO.output(self._select_out, GPIO.HIGH)

        # Now the enables
        for p in self._enables.values():
            GPIO.setup(p, GPIO.OUT)
            GPIO.output(p, GPIO.HIGH)

    def send(self):
        # Prepare to send
        GPIO.output(self._select_out, GPIO.LOW)
        for op in self._outputs:
            GPIO.output(self._copi, op)
            GPIO.output(self._clk_out, GPIO.LOW)
            GPIO.output(self._clk_out, GPIO.HIGH)
        # Clock everything into output stages
        GPIO.output(self._select_out, GPIO.HIGH)
        # Idle clk_out low
        GPIO.output(self._clk_out, GPIO.LOW)

    def set_oe(self, target: str, value: bool):
        GPIO.output(self._enables[target], value)

    def set_bus(self, target: str, value: Union[int, bitarray.bitarray]):
        if isinstance(value, int):
            assert value >= 0 and value < 2 ** BUS_WIDTH
            send_values = bitarray.util.int2ba(value, length=BUS_WIDTH, endian="little")
        else:
            send_values = value

        for i in range(BUS_WIDTH):
            bus_idx = self._buses[target][i]
            self._outputs[bus_idx] = send_values[BUS_WIDTH - i - 1]

    def set_cycle(self, step: int):
        # Negative values mean 'turn all off'
        assert step < CYCLE_WIDTH

        # Ensure everything is off
        for i in range(CYCLE_WIDTH):
            self._outputs[self._cycle[i]] = False

        # Turn on desired step
        if step >= 0:
            self._outputs[self._cycle[step]] = True


class _Input:
    def __init__(self):
        self.n_pins = 80

        self._inputs = [False for _ in range(self.n_pins)]
        self._bus_starts = dict(A=16, B=32, C=48, Instruction=64)
        self._cycle_start = 8

        # Designate the pins
        self._clk_in = 40
        self._cipo = 35
        self._select_in = 26
        self._load_in = 32

        # Board setup
        GPIO.setmode(GPIO.BOARD)

        GPIO.setup(self._clk_in, GPIO.OUT)
        GPIO.setup(self._select_in, GPIO.OUT)
        GPIO.output(self._select_in, GPIO.HIGH)
        GPIO.setup(self._load_in, GPIO.OUT)
        GPIO.setup(self._cipo, GPIO.IN)

    def recv(self):
        # Load the data
        GPIO.output(self._load_in, GPIO.LOW)
        GPIO.output(self._load_in, GPIO.HIGH)

        # Clock everything in
        GPIO.output(self._select_in, GPIO.LOW)
        for i in range(self.n_pins):
            self._inputs[i] = GPIO.input(self._cipo) == 1
            GPIO.output(self._clk_in, GPIO.LOW)
            GPIO.output(self._clk_in, GPIO.HIGH)
        GPIO.output(self._select_in, GPIO.HIGH)

    def read_bus(self, bus: str) -> int:
        idx = self._bus_starts[bus]
        byte_0 = list(reversed(self._inputs[idx : idx + BUS_WIDTH // 2]))
        byte_1 = list(reversed(self._inputs[idx + BUS_WIDTH // 2 : idx + BUS_WIDTH]))
        ba = bitarray.bitarray(byte_0 + byte_1, endian="little")
        return bitarray.util.ba2int(ba)

    def read_cycle(self) -> int:
        vals = list(
            reversed(self._inputs[self._cycle_start : self._cycle_start + CYCLE_WIDTH])
        )
        step = -1
        for i in range(CYCLE_WIDTH):
            if vals[i]:
                assert step < 0, "Two steps set!"
                step = i
        return step
