from typing import List

import RPi.GPIO as GPIO


class TesterBoard:
    def __init__(self):
        """Initialise instance and also RPi.GPIO."""
        self.n_pins = 40

        # Board pin numbers for output
        self._clk_out = 23
        self._copi = 19
        self._select_out = 24
        self._enable_out = [15, 13, 7, 5, 3]

        # Board pin numbers for input
        self._clk_in = 40
        self._select_in = 12
        self._load_in = 37
        self._cipo = 35

        # Configure the board
        GPIO.setmode(GPIO.BOARD)

        # Set up output side
        GPIO.setup(self._clk_out, GPIO.OUT)
        GPIO.setup(self._copi, GPIO.OUT)
        GPIO.setup(self._select_out, GPIO.OUT)
        GPIO.output(self._select_out, GPIO.HIGH)
        for p in self._enable_out:
            GPIO.setup(p, GPIO.OUT)
            GPIO.output(p, GPIO.LOW)

        # Setup intput side
        GPIO.setup(self._clk_in, GPIO.OUT)
        GPIO.setup(self._select_in, GPIO.OUT)
        GPIO.output(self._select_in, GPIO.HIGH)
        GPIO.setup(self._load_in, GPIO.OUT)
        GPIO.setup(self._cipo, GPIO.IN)

    def send(self, pins: List[bool]):
        """Send given array to the outputs."""
        assert len(pins) == self.n_pins

        GPIO.output(self._select_out, GPIO.LOW)
        # Pin 0 is the last clocked out
        for i in reversed(range(self.n_pins)):
            GPIO.output(self._copi, pins[i])
            GPIO.output(self._clk_out, GPIO.LOW)
            GPIO.output(self._clk_out, GPIO.HIGH)
        GPIO.output(self._select_out, GPIO.HIGH)

    def recv(self) -> List[bool]:
        """Receive all the inputs."""
        result = [False for _ in range(self.n_pins)]

        # Load the data
        GPIO.output(self._load_in, GPIO.LOW)
        GPIO.output(self._load_in, GPIO.HIGH)

        # Clock everything in
        GPIO.output(self._select_in, GPIO.LOW)
        for i in reversed(range(self.n_pins)):
            result[i] = GPIO.input(self._cipo) == 1
            GPIO.output(self._clk_in, GPIO.LOW)
            GPIO.output(self._clk_in, GPIO.HIGH)
        GPIO.output(self._select_in, GPIO.HIGH)

        return result

    def enable_outputs(self, output_banks: List[bool]):
        """Control output enabling by bank of 8 pins."""
        PINS_PER_595 = 8
        assert len(output_banks) == self.n_pins / PINS_PER_595

        # Recall that the 595 has active low output enable
        for i in range(len(output_banks)):
            GPIO.output(self._enable_out[i], not output_banks[i])
