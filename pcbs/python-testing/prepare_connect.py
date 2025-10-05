# Prepares the Pi Backplane to be connected
# Sets all outputs to high impedance
# Sets all clock lines low
# Sets reset line high

from pi_backplane import _Output

def main():
    output = _Output()

    buses = ["A", "B", "C", "Instruction", "Clock", "Reset"]
    for b in buses:
        output.set_oe(b, True)

    output.set_cycle(-1)
    output.set_clock(False)
    output.set_reset(True)
    output.send()
    print("Ready to connect Pi Backplane")


if __name__ == "__main__":
    main()
