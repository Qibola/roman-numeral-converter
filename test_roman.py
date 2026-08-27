"""Unit tests for the converter.

Day 4: the safety net. Every claim the README makes about this code should be
checked here, so a future change that breaks one of them fails loudly.

Run them with:

    python -m unittest -v
"""

import unittest

from cli import convert
from roman import MAX_VALUE, MIN_VALUE, RomanError, int_to_roman, roman_to_int


class TestIntToRoman(unittest.TestCase):
    """The integer -> numeral direction."""

    def test_single_letters(self):
        for number, expected in [
            (1, "I"), (5, "V"), (10, "X"),
            (50, "L"), (100, "C"), (500, "D"), (1000, "M"),
        ]:
            with self.subTest(number=number):
                self.assertEqual(int_to_roman(number), expected)

    def test_subtractive_pairs(self):
        # The six cases that a naive greedy loop would spell as IIII, DCCCC...
        for number, expected in [
            (4, "IV"), (9, "IX"), (40, "XL"),
            (90, "XC"), (400, "CD"), (900, "CM"),
        ]:
            with self.subTest(number=number):
                self.assertEqual(int_to_roman(number), expected)

    def test_repeated_letters(self):
        self.assertEqual(int_to_roman(3), "III")
        self.assertEqual(int_to_roman(30), "XXX")
        self.assertEqual(int_to_roman(3000), "MMM")

    def test_worked_examples(self):
        self.assertEqual(int_to_roman(14), "XIV")
        self.assertEqual(int_to_roman(1987), "MCMLXXXVII")
        self.assertEqual(int_to_roman(1994), "MCMXCIV")
        self.assertEqual(int_to_roman(2026), "MMXXVI")

    def test_boundaries(self):
        self.assertEqual(int_to_roman(MIN_VALUE), "I")
        self.assertEqual(int_to_roman(MAX_VALUE), "MMMCMXCIX")

    def test_out_of_range(self):
        for number in (0, -1, MAX_VALUE + 1, 10000):
            with self.subTest(number=number):
                with self.assertRaises(RomanError):
                    int_to_roman(number)

    def test_wrong_type(self):
        for value in (1.0, "5", None, [1]):
            with self.subTest(value=value):
                with self.assertRaises(RomanError):
                    int_to_roman(value)

    def test_bool_is_rejected(self):
        # bool subclasses int, so without an explicit guard True would be 1.
        with self.assertRaises(RomanError):
            int_to_roman(True)

    def test_error_is_a_value_error(self):
        # Callers already catching ValueError should keep working.
        with self.assertRaises(ValueError):
            int_to_roman(0)


class TestRomanToInt(unittest.TestCase):
    """The numeral -> integer direction, and its validation."""

    def test_reads_numerals(self):
        for numeral, expected in [
            ("I", 1), ("IV", 4), ("IX", 9), ("XIV", 14),
            ("MCMXCIV", 1994), ("MMMCMXCIX", 3999),
        ]:
            with self.subTest(numeral=numeral):
                self.assertEqual(roman_to_int(numeral), expected)

    def test_accepts_whitespace_and_lower_case(self):
        self.assertEqual(roman_to_int("  mcmxciv  "), 1994)
        self.assertEqual(roman_to_int("xiv"), 14)
        self.assertEqual(roman_to_int("XiV"), 14)

    def test_rejects_non_canonical_spellings(self):
        # Arithmetically these add up, but they are not how the numbers are
        # written -- the canonical-form check is what catches them.
        for numeral in ("IIII", "VV", "IM", "XXXX", "VIV", "IC"):
            with self.subTest(numeral=numeral):
                with self.assertRaises(RomanError):
                    roman_to_int(numeral)

    def test_error_suggests_the_right_spelling(self):
        with self.assertRaises(RomanError) as caught:
            roman_to_int("IIII")
        self.assertIn("IV", str(caught.exception))

    def test_rejects_empty_and_whitespace(self):
        for numeral in ("", "   ", "\t"):
            with self.subTest(numeral=repr(numeral)):
                with self.assertRaises(RomanError):
                    roman_to_int(numeral)

    def test_rejects_unknown_characters(self):
        for numeral in ("hello", "XIV!", "A", "1994"):
            with self.subTest(numeral=numeral):
                with self.assertRaises(RomanError):
                    roman_to_int(numeral)

    def test_names_the_bad_characters(self):
        with self.assertRaises(RomanError) as caught:
            roman_to_int("XIV?")
        self.assertIn("'?'", str(caught.exception))

    def test_wrong_type(self):
        for value in (14, None, ["X"]):
            with self.subTest(value=value):
                with self.assertRaises(RomanError):
                    roman_to_int(value)


class TestRoundTrip(unittest.TestCase):
    """The two directions should undo each other, for every value."""

    def test_every_number_survives_a_round_trip(self):
        for number in range(MIN_VALUE, MAX_VALUE + 1):
            numeral = int_to_roman(number)
            self.assertEqual(
                roman_to_int(numeral),
                number,
                "{} -> {} did not read back".format(number, numeral),
            )

    def test_every_numeral_is_accepted_by_its_own_speller(self):
        # A stronger claim than the above: no output of int_to_roman is ever
        # rejected as non-canonical by roman_to_int.
        for number in range(MIN_VALUE, MAX_VALUE + 1):
            numeral = int_to_roman(number)
            self.assertEqual(int_to_roman(roman_to_int(numeral)), numeral)


class TestConvert(unittest.TestCase):
    """The CLI's direction-detecting helper."""

    def test_digits_are_spelled_out(self):
        self.assertEqual(convert("1994"), "MCMXCIV")
        self.assertEqual(convert(" 14 "), "XIV")

    def test_letters_are_read_back(self):
        self.assertEqual(convert("MCMXCIV"), "1994")
        self.assertEqual(convert("xiv"), "14")

    def test_results_are_strings_both_ways(self):
        # main() prints these straight out, so neither branch may return an int.
        self.assertIsInstance(convert("14"), str)
        self.assertIsInstance(convert("XIV"), str)

    def test_negative_numbers_reach_the_range_check(self):
        # "-5" must be treated as a number, not as a numeral with a bad
        # character, so the error mentions the supported range.
        with self.assertRaises(RomanError) as caught:
            convert("-5")
        self.assertIn(str(MAX_VALUE), str(caught.exception))

    def test_empty_value(self):
        with self.assertRaises(RomanError):
            convert("   ")


if __name__ == "__main__":
    unittest.main()
