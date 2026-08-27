"""Command-line interface for the converter.

Day 3: one command that works in both directions, because the input itself
says which direction is wanted -- digits go one way, letters go the other.
Day 5: run with no values to get an interactive prompt instead.

    python cli.py 1994 MCMXCIV
    python cli.py
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


PROMPT = "roman> "

BANNER = (
    "Roman numeral converter. Type a number (1-3999) or a numeral.\n"
    "Type 'help' for help, or 'quit' (or Ctrl-D) to leave."
)

HELP = (
    "Enter 14 to spell it out, or XIV to read it back -- the direction is\n"
    "detected from what you type. Commands: help, quit."
)

QUIT_WORDS = {"q", "quit", "exit"}


def interactive(in_stream=None, out_stream=None):
    """Read values one line at a time and convert each until end of input.

    Both streams are arguments rather than hard-coded stdin/stdout so the
    loop can be driven by a StringIO in the tests. Returns the exit code.
    """
    in_stream = sys.stdin if in_stream is None else in_stream
    out_stream = sys.stdout if out_stream is None else out_stream

    print(BANNER, file=out_stream)
    while True:
        print(PROMPT, end="", file=out_stream)
        out_stream.flush()
        try:
            line = in_stream.readline()
        except KeyboardInterrupt:  # Ctrl-C: leave quietly, like Ctrl-D
            line = ""
        if not line:  # end of input (Ctrl-D, or the test's StringIO running out)
            print(file=out_stream)
            return 0

        text = line.strip()
        if not text:  # a bare Enter is not an error, just another prompt
            continue
        lowered = text.lower()
        if lowered in QUIT_WORDS:
            return 0
        if lowered == "help":
            print(HELP, file=out_stream)
            continue

        try:
            print(convert(text), file=out_stream)
        except RomanError as exc:
            # Mistakes are expected at a prompt, so report and keep going
            # instead of exiting the way the one-shot command does.
            print("error: {}".format(exc), file=out_stream)


def main(argv=None):
    """Run the CLI. Returns the process exit code."""
    parser = argparse.ArgumentParser(
        description="Convert between Roman numerals and integers. "
        "The direction is detected from each value: digits are spelled "
        "out as numerals, letters are read back as numbers. With no values, "
        "starts an interactive prompt.",
        epilog="examples: %(prog)s 1994    |    %(prog)s MCMXCIV xiv    |    %(prog)s",
    )
    parser.add_argument(
        "values",
        nargs="*",
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

    # No values on the command line means the caller has nothing to convert
    # yet, so ask for it interactively rather than printing a usage error.
    if not args.values:
        return interactive()

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
