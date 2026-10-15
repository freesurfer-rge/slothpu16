import argparse

from pathlib import Path

def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    """Parse command-line arguments.

    Args:
        argv: Argument list (defaults to ``sys.argv[1:]``).

    Returns:
        Parsed namespace with ``asm_file`` attribute.
    """
    parser = argparse.ArgumentParser(
        prog="pyslothpu16-ui",
        description="A TUI for the SlothPU16 emulator",
    )
    parser.add_argument(
        "asm_file",
        type=Path,
        help="Path to an assembler file containing the target program",
    )
    return parser.parse_args(argv)