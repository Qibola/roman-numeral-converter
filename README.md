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

...followed by a few numerals read back the other way, including some
deliberately broken ones.

To convert something, use the command line:

```bash
$ python cli.py 1994 MCMXCIV xiv
1994 -> MCMXCIV
MCMXCIV -> 1994
xiv -> 14
```

There is no `--to-roman` / `--to-int` flag, because the value itself already
says which way to go. Pass `-q` to print bare results, and `--help` for the
full usage.

Run it with no values at all and it asks instead:

```
$ python cli.py
Roman numeral converter. Type a number (1-3999) or a numeral.
Type 'help' for help, or 'quit' (or Ctrl-D) to leave.
roman> 2026
MMXXVI
roman> MMXXVI
2026
roman> IIII
error: 'IIII' is not a valid Roman numeral; 4 is written IV.
roman> quit
```

To check nothing is broken:

```bash
python -m unittest -v
```

Or import it:

```python
>>> from roman import int_to_roman, roman_to_int
>>> int_to_roman(2026)
'MMXXVI'
>>> roman_to_int("MMXXVI")
2026
>>> roman_to_int(" mcmxciv ")   # whitespace and lower case are fine
1994
```

## Roadmap

This project is built a small piece at a time. Progress:

- [x] Day 1 — Scaffold: README, `.gitignore`, core `int_to_roman()`
- [x] Day 2 — `roman_to_int()` + validation of malformed numerals
- [x] Day 3 — Command-line interface (argparse), auto-detecting direction
- [x] Day 4 — Unit tests (`unittest`) covering edge cases and round trips
- [x] Day 5 — Interactive mode + README polish

All five steps are done, so the project is finished.

## Files

| File | What it does |
| --- | --- |
| `roman.py` | The conversion code |
| `cli.py` | Command-line front end and interactive prompt |
| `test_roman.py` | The test suite |

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

## How `roman_to_int()` works

Reading a numeral is one left-to-right pass over the seven single letters:

> A letter is **subtracted** if the letter after it is larger, and **added**
> otherwise.

So `IX` is `-1 + 10 = 9`, while `XI` is `10 + 1 = 11`. That single rule handles
every well-formed numeral.

The catch is that the rule is too forgiving on its own. It reads `IIII` as 4,
`IM` as 999 and `VV` as 10 — values that are correct arithmetic but are not how
those numbers are written. Rather than hand-code the repetition limits and
which pairs may subtract from which, the function spells the total back out
with Day 1's `int_to_roman()` and compares:

```python
canonical = int_to_roman(total)
if canonical != cleaned:
    raise RomanError(...)
```

If the input isn't character-for-character the canonical spelling, it's
rejected — and because the canonical form is already in hand, the error can say
what the right spelling would have been:

```
>>> roman_to_int("IIII")
RomanError: 'IIII' is not a valid Roman numeral; 4 is written IV.
```

Validation happens in widening circles: wrong type, then empty string, then
letters that aren't numerals at all, then out-of-range totals, and only then
the canonical-spelling check. Each layer can assume the ones before it passed,
which keeps every individual check short.

## How the CLI picks a direction

`cli.py` takes one or more values and asks a single question about each:

```python
if text.lstrip("+-").isdigit():
    return int_to_roman(int(text))
return str(roman_to_int(text))
```

Digits mean "spell this out", anything else means "read this back". That is
enough to drop the mode flag entirely — `python cli.py 14 XIV` converts in both
directions in one command.

The `lstrip("+-")` matters for a small reason. Without it, `-5` fails the
`isdigit()` test, gets treated as a numeral, and comes back with the confusing
complaint that `-` is not a Roman letter. With it, `-5` is recognised as a
number and reaches `int_to_roman()`, which gives the useful message: Roman
numerals only cover 1 to 3999.

Bad values do not stop the run. Each one prints to `stderr` and the loop
carries on, so a long list still converts everything it can; the command then
exits `1` if anything failed. That split — good results on `stdout`, complaints
on `stderr`, failure in the exit code — is what lets the tool be used in a
pipeline.

## What the tests cover

`test_roman.py` is 24 tests in four groups, and the split is deliberate: three
groups test one function each, and the fourth tests the two together.

`TestIntToRoman` and `TestRomanToInt` cover the edges rather than the middle —
the boundaries (1 and 3999), just outside them (0, -1, 4000), the six
subtractive pairs, the wrong types, and the `True` case that `bool`-subclasses-
`int` would otherwise let through. They also assert on the *content* of two
error messages, because "`IIII` should have been `IV`" is a feature of this
converter, not an accident of how it fails.

`TestRoundTrip` is the group worth stealing for other projects. Instead of
listing examples, it makes one claim about the whole domain:

```python
for number in range(MIN_VALUE, MAX_VALUE + 1):
    self.assertEqual(roman_to_int(int_to_roman(number)), number)
```

All 3999 values, in a few milliseconds. This is only possible because the two
functions are inverses, and when a pair of functions has that shape the round
trip finds bugs that hand-picked cases miss — a spelling that reads back as the
wrong number has nowhere to hide. The second test in the group makes the
stronger claim that no output of `int_to_roman()` is ever rejected by
`roman_to_int()`'s canonical-form check, which is what keeps the two halves
from drifting apart.

`unittest.subTest()` does the small but real job of reporting every failing
case in a loop instead of stopping at the first, so a broken table shows all
six bad pairs in one run rather than one per fix.

Sanity-checking the suite itself: changing the `(4, "IV")` row of `VALUES` to
`(4, "IIII")` fails 11 of the 24 tests. A test suite that passes no matter what
the code does is worse than none, so it is worth breaking the code on purpose
once to watch the tests notice.

## How interactive mode works

The prompt is a `while True` loop around the same `convert()` the one-shot
command uses, so the two front ends can never disagree about what `XIV` means.
Only three things are different, and each one is a deliberate choice about what
a person at a keyboard needs.

**A typo must not end the session.** The one-shot command sets a failure flag
and exits `1`, which is right for a script. At a prompt that would throw the
user out over a mistyped letter, so `interactive()` prints the error and loops.
The mistake is the normal case here, not the exceptional one — which is also
why the error text goes to `stdout` with the results rather than to `stderr`,
where it could arrive out of order on the screen.

**Leaving has to be obvious.** `quit`, `exit`, `q` and Ctrl-D all work. Ctrl-D
is the interesting one: it isn't a keypress the loop can check for, it's simply
end of input, and `readline()` signals that by returning an empty string. A
blank line the user typed comes back as `"\n"`, which is truthy — so `if not
line` distinguishes "pressed Enter" from "no more input" with no special cases.

**The streams are arguments, not globals:**

```python
def interactive(in_stream=None, out_stream=None):
    in_stream = sys.stdin if in_stream is None else in_stream
```

This is the part worth carrying into other projects. `input()` would have been
shorter, but it reads the real keyboard, and code that reads the real keyboard
cannot be tested. Taking the streams as parameters means `TestInteractive` can
hand the loop a `StringIO` of typed lines and read back everything it printed:

```python
code = interactive(io.StringIO("IIII\n42\n"), out)
```

That single change is what makes six of the thirty tests possible — including
the one asserting that a bad line does *not* end the session, which is exactly
the behaviour most likely to get broken by a later refactor and impossible to
notice by hand. Defaulting the arguments to `None` rather than to `sys.stdin`
directly keeps that testability without capturing the stream at import time.

## Where this landed

Five days, four files, no dependencies, 30 tests. The shape that made it work
was doing the integer -> numeral direction first, because everything after it
leaned on that one table: `roman_to_int()` validates by re-spelling with it,
the CLI just picks which direction to call, the round-trip test checks all 3999
values through both, and the prompt is a loop around the CLI's converter. Each
step got smaller because the previous one had already done the thinking.
