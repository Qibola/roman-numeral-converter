"""Convert between Roman numerals and integers.

Day 1: the integer -> numeral direction, plus the shared error type.
"""

# Ordered largest-first, with the six subtractive pairs sitting just above
# the value they subtract from. Greedy subtraction over this table is what
# makes 4 come out as "IV" instead of "IIII".
VALUES = (
    (1000, "M"),
    (900, "CM"),
    (500, "D"),
    (400, "CD"),
    (100, "C"),
    (90, "XC"),
    (50, "L"),
    (40, "XL"),
    (10, "X"),
    (9, "IX"),
    (5, "V"),
    (4, "IV"),
    (1, "I"),
)

MIN_VALUE = 1
MAX_VALUE = 3999


class RomanError(ValueError):
    """Raised on input this converter can't represent. Subclasses ValueError."""


def int_to_roman(number):
    """Return the Roman numeral for an integer between 1 and 3999.

    >>> int_to_roman(4)
    'IV'
    >>> int_to_roman(1994)
    'MCMXCIV'
    """
    if isinstance(number, bool) or not isinstance(number, int):
        raise RomanError(
            "Expected a whole number, but got {!r}.".format(number)
        )
    if number < MIN_VALUE or number > MAX_VALUE:
        raise RomanError(
            "Roman numerals only cover {} to {}, but got {}.".format(
                MIN_VALUE, MAX_VALUE, number
            )
        )

    parts = []
    remaining = number
    for value, numeral in VALUES:
        count, remaining = divmod(remaining, value)
        parts.append(numeral * count)
    return "".join(parts)


if __name__ == "__main__":
    for n in (1, 4, 9, 14, 40, 90, 400, 1987, 1994, 3999):
        print("{:>4} -> {}".format(n, int_to_roman(n)))
