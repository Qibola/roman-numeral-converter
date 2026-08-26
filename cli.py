"""Command-line interface for the converter.

Day 3: one command that works in both directions, because the input itself
says which direction is wanted -- digits go one way, letters go the other.

    python cli.py 1994 MCMXCIV
"""

import argparse
import sys

from roman import RomanError, int_to_roman, roman_to_int


def convert(token):
    """Convert one argument, picking the direction from what it looks like.

    A token made only of digits is an integer to spell out; anything else is
    treated as a numeral to read. Raises RomanError on bad input.

    >>> convert("1994")
    'MCMXCIV'
    >>> convert("MCMXCIV")
    '1994'
    """
    text = token.strip()
    if not text:
        raise RomanError("Expected a number or a numeral, but got an empty value.")

    # lstrip("-") so that "-5" is still recognised as a number and reaches
    # int_to_roman's range check, rather than being read as a numeral and
    # reported as a bad character.
    if text.lstrip("+-").isdigit():
        return int_to_roman(int(text))
    return str(roman_to_int(text))


def main(argv=None):
    """Run the CLI. Returns the process exit code."""
    parser = argparse.ArgumentParser(
        description="Convert between Roman numerals and integers. "
        "The direction is detected from each value: digits are spelled "
        "out as numerals, letters are read back as numbers.",
        epilog="examples: %(prog)s 1994    |    %(prog)s MCMXCIV xiv",
    )
    parser.add_argument(
        "values",
        nargs="+",
        metavar="VALUE",
        help="an integer (1-3999) or a Roman numeral; repeatable",
    )
    parser.add_argument(
        "-q",
        "--quiet",
        action="store_true",
        help="print only the results, without the 'input -> ' prefix",
    )
    args = parser.parse_args(argv)

    failed = False
    for token in args.values:
        try:
            result = convert(token)
        except RomanError as exc:
            print("error: {}".format(exc), file=sys.stderr)
            failed = True
            continue
        if args.quiet:
            print(result)
        else:
            print("{} -> {}".format(token.strip(), result))

    # One bad value fails the whole command, but the good ones are still
    # printed first -- handy when converting a long list.
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
