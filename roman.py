"""Convert between Roman numerals and integers.

Day 1: the integer -> numeral direction, plus the shared error type.
Day 2: the numeral -> integer direction, with validation.
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


# The seven single letters, for reading a numeral one character at a time.
LETTERS = {"I": 1, "V": 5, "X": 10, "L": 50, "C": 100, "D": 500, "M": 1000}


def roman_to_int(numeral):
    """Return the integer for a Roman numeral string.

    Accepts surrounding whitespace and lower case. Rejects anything that is
    not the one standard spelling of its value, so "IIII" and "IM" are errors.

    >>> roman_to_int("IV")
    4
    >>> roman_to_int(" mcmxciv ")
    1994
    """
    if not isinstance(numeral, str):
        raise RomanError(
            "Expected a Roman numeral string, but got {!r}.".format(numeral)
        )

    cleaned = numeral.strip().upper()
    if not cleaned:
        raise RomanError("Expected a Roman numeral, but got an empty string.")

    unknown = sorted(set(cleaned) - set(LETTERS))
    if unknown:
        raise RomanError(
            "{!r} contains characters that are not Roman numerals: {}.".format(
                numeral.strip(), ", ".join(repr(c) for c in unknown)
            )
        )

    # Read left to right. A letter smaller than the one after it is being
    # subtracted (the I in IX); otherwise it is added.
    total = 0
    for index, letter in enumerate(cleaned):
        value = LETTERS[letter]
        following = cleaned[index + 1:]
        if following and value < LETTERS[following[0]]:
            total -= value
        else:
            total += value

    # The loop above is forgiving: it happily reads "IIII" as 4 and "IM" as
    # 999. Re-spelling the total and comparing is the cheapest way to insist
    # on the one canonical form, and it reuses Day 1's table instead of
    # hand-writing repetition and ordering rules.
    if total < MIN_VALUE or total > MAX_VALUE:
        raise RomanError(
            "{!r} is not a valid Roman numeral.".format(numeral.strip())
        )
    canonical = int_to_roman(total)
    if canonical != cleaned:
        raise RomanError(
            "{!r} is not a valid Roman numeral; {} is written {}.".format(
                numeral.strip(), total, canonical
            )
        )
    return total


if __name__ == "__main__":
    for n in (1, 4, 9, 14, 40, 90, 400, 1987, 1994, 3999):
        print("{:>4} -> {}".format(n, int_to_roman(n)))

    print()
    for text in ("IV", "xiv", " MCMXCIV ", "IIII", "IM", "XVIII", "hello"):
        try:
            print("{:>10} -> {}".format(text, roman_to_int(text)))
        except RomanError as exc:
            print("{:>10} -> error: {}".format(text, exc))
