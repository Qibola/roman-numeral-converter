# roman-numeral-converter

Convert between Roman numerals and integers, in both directions, in plain
Python with no dependencies.

This is a beginner learning project: it grows one small, working step at a time.

## Quick start

```bash
python roman.py
```

Right now that prints a short demo table:

```
   1 -> I
   4 -> IV
   9 -> IX
  14 -> XIV
  40 -> XL
  90 -> XC
 400 -> CD
1987 -> MCMLXXXVII
1994 -> MCMXCIV
3999 -> MMMCMXCIX
```

Or import it:

```python
>>> from roman import int_to_roman
>>> int_to_roman(2026)
'MMXXVI'
```

## Roadmap

This project is built a small piece at a time. Progress:

- [x] Day 1 — Scaffold: README, `.gitignore`, core `int_to_roman()`
- [ ] Day 2 — `roman_to_int()` + validation of malformed numerals
- [ ] Day 3 — Command-line interface (argparse), auto-detecting direction
- [ ] Day 4 — Unit tests (`unittest`) covering edge cases and round trips
- [ ] Day 5 — Interactive mode + README polish

## Files

| File | What it does |
| --- | --- |
| `roman.py` | The conversion code |

## How `int_to_roman()` works

The whole algorithm is a greedy walk down one table:

```python
VALUES = ((1000, "M"), (900, "CM"), (500, "D"), (400, "CD"), ...)
```

For each row, `divmod()` asks "how many of these fit, and what's left over?",
appends that many copies of the numeral, and carries the remainder to the next
row. Because the rows only ever get smaller, one pass is enough.

The trick is that the six **subtractive pairs** — `CM`, `CD`, `XC`, `XL`, `IX`,
`IV` — are rows in the same table, each sitting directly above the value it
subtracts from. Without them, greedy subtraction would spell 4 as `IIII` and
900 as `DCCCC`. With them, 900 is consumed by the `CM` row before the `D` row
is ever reached, so the ordinary rule handles the special cases for free.

`1994` is the example worth tracing: `M` (1000) leaves 994, `CM` (900) leaves
94, `XC` (90) leaves 4, `IV` leaves 0 — `MCMXCIV`.

## Why 1 to 3999

Standard Roman numerals have no zero, no negatives, and no symbol above `M`, so
the largest number spellable without the overline notation is `MMMCMXCIX` =
3999. Anything outside that raises `RomanError`, which subclasses `ValueError`
so callers that already catch `ValueError` keep working.

`isinstance(number, bool)` is checked first because in Python `bool` is a
subclass of `int` — without that guard, `int_to_roman(True)` would happily
return `"I"`.
