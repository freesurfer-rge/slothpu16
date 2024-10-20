# Register with Reset

This is a 16-bit register, which will reset to zero on power on, or when the RESET line is pulled low.

Notes:

- Diodes (but not LEDs) appeared to be back-to-front in placement files
- Had to resize vias, since smallest ones are extra cost
- RESET needs to be low for about 0.1 sec to be effective. On return high, need to wait about 0.1 sec before register will be effective again

Errata:

The CLK and RESET lines block each other, since the clock signal to the registers is the result of ORing the two (well, delay-inverted-output for RESET) together.

In any future revision, board should be revised to remove this limitation (at least so that a high clock line doesn't block RESET).