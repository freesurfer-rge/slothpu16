import argparse
import logging
import pathlib
import shutil

from ._invoke_gcc import preprocess_c_file

_DESC = "A simple C compiler, based on that in Nora Sandler's book."

_DEFAULT_WORKING_DIR = "temp-nqcc"

_WORKING_DIR_DESC = f"""\
Directory to store intermediate files. By default
this will be '{_DEFAULT_WORKING_DIR}' in the same
directory as the target file. This directory will
be DELETED and recreated before any other tooling
runs.
"""

logging.basicConfig(level=logging.INFO)
_logger = logging.getLogger("nqcc")

def parse_args():
    parser = argparse.ArgumentParser(
        prog="pyslothpu-nqcc",
        description=_DESC,
        add_help=True,
    )

    preprocessor_group = parser.add_argument_group(title="Preprocessor arguments")
    preprocessor_group.add_argument(
        "-D",
        action="append",
        dest="define_list",
        default=[],
        help="Preprocessor macros (-D NAME or -D NAME=VALUE)."
        + " Repeat as many -D values as necessary",
    )

    parser.add_argument("--working-dir", type=pathlib.Path, required=False, help=_WORKING_DIR_DESC)
    parser.add_argument("target", type=pathlib.Path, help="Path to target C file")

    args = parser.parse_args()

    if not args.working_dir:
        args.working_dir = args.target.parent / _DEFAULT_WORKING_DIR

    return args

def main():
    args = parse_args()

    assert args.target.exists(), f"Target {args.target} does not exist!"

    if args.working_dir.exists():
        _logger.warning("Deleting working directory %s", args.working_dir)
        shutil.rmtree(args.working_dir)
    args.working_dir.mkdir()


    _logger.info("Running preprocessor")
    preprocessed_file_path = preprocess_c_file(
        args.target, args.working_dir, macro_defines=args.define_list
    )

    with open(preprocessed_file_path, "r") as f:
        c_source = f.read()


if __name__ == "__main__":
    main()