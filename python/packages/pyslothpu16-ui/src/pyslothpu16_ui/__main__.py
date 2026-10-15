from pyslothpu16_emulator import SlothPU16

from .app import SlothPU16App
from .cli import parse_args


def main() -> None:
    """Entry point for the replay viewer TUI application."""
    args = parse_args()

    spu16 = SlothPU16(asm_file=args.asm_file)

    app = SlothPU16App(spu16)
    app.title = "SlothPU Emulator"
    app.run()


if __name__ == "__main__":
    main()
