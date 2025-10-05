# Main program to drive SlothPU16

import argparse
import pathlib

from typing import List

import bitarray

def parse_arguments():
    parser = argparse.ArgumentParser(add_help=True)

    parser.add_argument("--input_file", type=pathlib.Path, required=True, help="Path to SlothPU assembler file")

    args = parser.parse_args()

    return args


def process_assembler(lines: List[str]) -> List[int]:
    COMMENT_CHAR = "#"

    result = []
    
    for l in lines:
        pruned_line = l.split(COMMENT_CHAR)[0].strip()
        if len(pruned_line)>0:
            print(f"'{pruned_line}'")

    return result

def main():
    args = parse_arguments()

    with open(args.input_file, 'r') as af:
        assembler_lines = af.readlines()
    print(f"Read {len(assembler_lines)} lines")

    start_memory = process_assembler(assembler_lines)
    

if __name__ == "__main__":
    main()
