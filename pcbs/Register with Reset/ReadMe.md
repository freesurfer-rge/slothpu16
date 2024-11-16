# Register with Reset

This is a 16-bit register, which will reset to zero on power on, or when the RESET line is pulled low.

Notes:

- Diodes (but not LEDs) appeared to be back-to-front in placement files
- Had to resize vias, since smallest ones are extra cost
- RESET needs to be low for about 0.1 sec to be effective. On return high, need to wait about 0.1 sec before register will be effective again
- There is still some oddness around the RESET line on the r1 board; I've noticed that when the final test completes, there's often one LED left on. But a manual reset gets rid of it

Errata:

- The CLK and RESET lines block each other, since the clock signal to the registers is the result of ORing the two (well, delay-inverted-output for RESET) together. UPDATE for *r1*, the RESET and CLK lines are ANDed together to produce the 'clock' side of the reset, so a low on RESET will inhibit the clock, and should largely avoid this issue.