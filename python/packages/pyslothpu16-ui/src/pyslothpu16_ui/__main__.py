from pyslothpu16_emulator import SlothPU16

from .cli import parse_args


def main() -> None:
    """Entry point for the replay viewer TUI application."""
    args = parse_args()

    spu16 = SlothPU16(asm_file=args.asm_file)


if __name__ == "__main__":
    main()
