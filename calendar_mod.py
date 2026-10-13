"""Calendar question generators.

Subtypes:
    day_of_week       — given a date, find the day of the week
    day_shift         — today is X, what day is N days later/earlier
    odd_days          — odd days in a range of years
    calendar_repeat   — after how many years does year Y's calendar repeat
"""

import datetime


_DAY_NAMES = [
    "monday", "tuesday", "wednesday", "thursday",
    "friday", "saturday", "sunday",
]


def _is_leap(y):
    return (y % 4 == 0 and y % 100 != 0) or (y % 400 == 0)


def _build_day_of_week(p):
    y, m, d = p
    wd = datetime.date(y, m, d).weekday()
    return {
        "prompt": f"What day of the week was {d:02d}/{m:02d}/{y}?",
        "answer": _DAY_NAMES[wd],
        "hint": "Use odd days = past years + current year, mod 7.",
        "qtype": "day_of_week",
    }


def _build_day_shift(p):
    start_day, shift = p
    start_idx = _DAY_NAMES.index(start_day)
    end_idx = (start_idx + shift) % 7
    direction = "later" if shift > 0 else "earlier"
    return {
        "prompt": (
            f"If today is {start_day.capitalize()}, what day is it "
            f"{abs(shift)} days {direction}?"
        ),
        "answer": _DAY_NAMES[end_idx],
        "hint": f"Shift = {shift} mod 7; move that many steps.",
        "qtype": "day_shift",
    }


def _build_odd_days(p):
    y1, y2 = p
    total = 0
    for y in range(y1, y2):
        total += 2 if _is_leap(y) else 1
    return {
        "prompt": f"Number of odd days from year {y1} to {y2 - 1} inclusive?",
        "answer": str(total % 7),
        "hint": "Sum odd days: leap = 2, ordinary = 1. Then mod 7.",
        "qtype": "odd_days",
    }


def _build_calendar_repeat(p):
    y = p[0]
    if _is_leap(y):
        delta = 28
    elif not _is_leap(y + 6):
        delta = 6
    else:
        delta = 11
    return {
        "prompt": f"After how many years does the calendar of {y} repeat?",
        "answer": str(delta),
        "hint": "Leap → 28 years. Ordinary → 6 or 11.",
        "qtype": "calendar_repeat",
    }


# ------------------------------------------------------------------
# Parameter enumeration
# ------------------------------------------------------------------
_DATES = [
    (1998, 8, 15), (2000, 1, 1), (2001, 9, 11), (2004, 2, 29),
    (2010, 6, 20), (2012, 12, 21), (2016, 3, 15), (2020, 1, 26),
    (2021, 8, 15), (2022, 1, 1), (2023, 7, 4), (2024, 2, 29),
    (1980, 5, 10), (1975, 11, 30), (1969, 7, 20), (1950, 1, 26),
    (1947, 8, 15), (1990, 10, 2), (1985, 4, 1), (2005, 11, 11),
]

_DAY_SHIFT_PARAMS = [
    (start, shift)
    for start in _DAY_NAMES
    for shift in (-100, -50, -30, -20, -10, -7, -3, 3, 5, 10, 15, 20, 30, 50, 100, 200, 365, 400)
]

_ODD_DAYS_PARAMS = [
    (y1, y2)
    for y1 in (1990, 1995, 2000, 2005, 2010, 2015, 2020)
    for y2 in (y1 + 5, y1 + 10, y1 + 15, y1 + 20)
]

_REPEAT_PARAMS = [(y,) for y in range(1980, 2031)]


PARAMS = {
    "day_of_week":     _DATES,
    "day_shift":       _DAY_SHIFT_PARAMS,
    "odd_days":        _ODD_DAYS_PARAMS,
    "calendar_repeat": _REPEAT_PARAMS,
}

BUILDERS = {
    "day_of_week":     _build_day_of_week,
    "day_shift":       _build_day_shift,
    "odd_days":        _build_odd_days,
    "calendar_repeat": _build_calendar_repeat,
}

LABELS = {
    "day_of_week":     "Day of the week for a date",
    "day_shift":       "Day shift by N days",
    "odd_days":        "Odd days in a year range",
    "calendar_repeat": "Calendar repetition interval",
}
