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

        self._enables = dict(
            A = 8,
            B = 3,
            C = 5,
            Cycle = 10,
            Instruction = 7,
            Clock = 11,
            Reset = 12
            )

        self._buses = dict(
            A=[16 + i for i in range(BUS_WIDTH)]
            )

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
            
    def _send(self):
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
            assert value >=0 and value < 2**BUS_WIDTH
            send_values = bitarray.util.int2ba(value, length=BUS_WIDTH, endian="little")
        else:
            send_values = value

        for i in range(BUS_WIDTH):
            bus_idx = self._buses[target][i]
            self._outputs[bus_idx] = send_values[i]

        self._send()
        
