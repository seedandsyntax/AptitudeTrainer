"""Clock question generators.

Families:
    angle_at_time      — smaller angle between hands at a given time
    reflex_at_time     — reflex angle (360 − smaller)
    hour_position      — hour hand position from 12 o'clock
    minute_position    — minute hand position from 12 o'clock
    time_at_angle      — when hands make a given angle in an hour slot
    coincide           — when hands coincide
    opposite           — when hands point opposite
    gain_lose          — clock gains/loses time
    timezone           — longitude-based local time shift
"""

import random


# ------------------------------------------------------------------
# Core math
# ------------------------------------------------------------------
def _hour_pos(h, m):
    """Hour hand angle from 12 o'clock, degrees."""
    return ((h % 12) * 30 + m * 0.5) % 360


def _min_pos(m):
    """Minute hand angle from 12 o'clock, degrees."""
    return (m * 6) % 360


def _small_angle(h, m):
    """Smaller angle between hands at time h:m."""
    diff = abs(_hour_pos(h, m) - _min_pos(m))
    if diff > 180:
        diff = 360 - diff
    return diff


def _solve_for_angle(h, target):
    """Return sorted list of t in [0, 60) with smaller angle == target."""
    sols = []
    for sign in (1, -1):
        for k in (-1, 0, 1):
            # 30h − 5.5t = sign × target + 360k
            t = (30 * h - sign * target - 360 * k) / 5.5
            if 0 <= t < 60:
                sols.append(round(t, 4))
    unique = []
    for t in sols:
        if not any(abs(t - u) < 0.01 for u in unique):
            unique.append(t)
    unique.sort()
    return unique


def _fmt_num(x):
    if abs(x - round(x)) < 1e-6:
        return str(int(round(x)))
    return f"{x:.1f}"


# ------------------------------------------------------------------
# Builders
# ------------------------------------------------------------------
def _build_angle_at_time(p):
    h, m = p
    angle = _small_angle(h, m)
    return {
        "prompt": f"Angle between hands at {h}:{m:02d}?",
        "answer": _fmt_num(angle),
        "hint": f"Angle = |30×{h} − 5.5×{m}|",
        "qtype": "angle_at_time",
        "tolerance": 0.01,
    }


def _build_reflex_at_time(p):
    h, m = p
    angle = _small_angle(h, m)
    reflex = 360 - angle
    return {
        "prompt": f"Reflex angle between hands at {h}:{m:02d}?",
        "answer": _fmt_num(reflex),
        "hint": f"Smaller = |30×{h} − 5.5×{m}|; reflex = 360 − smaller",
        "qtype": "reflex_at_time",
        "tolerance": 0.01,
    }


def _build_hour_position(p):
    h, m = p
    pos = _hour_pos(h, m)
    return {
        "prompt": f"Hour hand position from 12 o'clock at {h}:{m:02d} (degrees)?",
        "answer": _fmt_num(pos),
        "hint": "Hour hand = 30×H + 0.5×M",
        "qtype": "hour_position",
        "tolerance": 0.01,
    }


def _build_minute_position(p):
    h, m = p
    pos = _min_pos(m)
    return {
        "prompt": f"Minute hand position from 12 o'clock at {h}:{m:02d}?",
        "answer": _fmt_num(pos),
        "hint": "Minute hand = 6×M",
        "qtype": "minute_position",
        "tolerance": 0.01,
    }


def _build_time_at_angle(p):
    h, angle, idx, t, total = p
    if total == 1:
        which = "the"
    elif idx == 0:
        which = "the earlier"
    else:
        which = "the later"
    return {
        "prompt": (
            f"Between {h}:00 and {h + 1}:00, hands make {angle}° at "
            f"{'two times' if total == 2 else 'one time'}. "
            f"Enter {which} solution as minutes past {h} (2 decimals)."
        ),
        "answer": _fmt_num(t),
        "hint": f"Solve |30×{h} − 5.5t| = {angle} for t ∈ [0, 60)",
        "qtype": "time_at_angle",
        "tolerance": 0.05,
    }


def _build_coincide(p):
    h, t = p
    return {
        "prompt": (
            f"Between {h}:00 and {h + 1}:00, at what minute past {h} "
            f"do the hands coincide? (2 decimals)"
        ),
        "answer": _fmt_num(t),
        "hint": "Set 30×H − 5.5t = 0 → t = 60H / 11",
        "qtype": "coincide",
        "tolerance": 0.05,
    }


def _build_opposite(p):
    h, t = p
    return {
        "prompt": (
            f"Between {h}:00 and {h + 1}:00, at what minute past {h} "
            f"do the hands point opposite? (2 decimals)"
        ),
        "answer": _fmt_num(t),
        "hint": "Set |30×H − 5.5t| = 180",
        "qtype": "opposite",
        "tolerance": 0.05,
    }


def _build_gain_lose(p):
    rate, direction = p
    hours = 720 / rate
    return {
        "prompt": (
            f"A clock {direction}s {rate} minutes every hour. "
            f"After how many hours will it next show correct time?"
        ),
        "answer": _fmt_num(hours),
        "hint": "Drift needed = 12 hours = 720 min. Time = 720 / rate.",
        "qtype": "gain_lose",
        "tolerance": 0.1,
    }


def _build_timezone(p):
    lon_a, lon_b = p
    diff_deg = lon_b - lon_a
    minutes_diff = diff_deg * 4
    return {
        "prompt": (
            f"Place A at {lon_a}°E, place B at {lon_b}°E. "
            f"If it is 12:00 at A, what is the local time at B "
            f"in hours relative to A? (2 decimals, signed)"
        ),
        "answer": _fmt_num(minutes_diff / 60),
        "hint": "1° longitude = 4 min. East gains, West loses.",
        "qtype": "timezone",
        "tolerance": 0.02,
    }


# ------------------------------------------------------------------
# Parameter enumeration
# ------------------------------------------------------------------
_HOURS = list(range(1, 13))
_MIN_STEPS = [0, 10, 20, 30, 40, 50]

_ANGLE_PARAMS = [(h, m) for h in _HOURS for m in _MIN_STEPS]

_TIME_AT_ANGLE_PARAMS = []
for h in _HOURS:
    for angle in (30, 60, 90, 120, 150):
        sols = _solve_for_angle(h, angle)
        nontrivial = [t for t in sols if t > 0.01]
        total = len(nontrivial)
        for idx, t in enumerate(nontrivial):
            _TIME_AT_ANGLE_PARAMS.append((h, angle, idx, t, total))

_COINCIDE_PARAMS = []
for h in _HOURS:
    t = 60 * h / 11
    if 0.01 < t < 60:
        _COINCIDE_PARAMS.append((h, round(t, 4)))

_OPPOSITE_PARAMS = []
for h in _HOURS:
    for t in _solve_for_angle(h, 180):
        if 0.01 < t < 60:
            _OPPOSITE_PARAMS.append((h, round(t, 4)))

_GAIN_LOSE_PARAMS = [
    (rate, d)
    for rate in (1, 2, 3, 4, 5, 6, 8, 10, 12, 15, 20, 30)
    for d in ("gain", "lose")
]

_TIMEZONE_PARAMS = [
    (a, b)
    for a in (-90, -60, -30, 0, 15, 30, 45, 60, 90, 120)
    for b in (-90, -60, -30, 0, 15, 30, 45, 60, 90, 120)
    if a != b
]


PARAMS = {
    "angle_at_time":   _ANGLE_PARAMS,
    "reflex_at_time":  _ANGLE_PARAMS,
    "hour_position":   _ANGLE_PARAMS,
    "minute_position": _ANGLE_PARAMS,
    "time_at_angle":   _TIME_AT_ANGLE_PARAMS,
    "coincide":        _COINCIDE_PARAMS,
    "opposite":        _OPPOSITE_PARAMS,
    "gain_lose":       _GAIN_LOSE_PARAMS,
    "timezone":        _TIMEZONE_PARAMS,
}

BUILDERS = {
    "angle_at_time":   _build_angle_at_time,
    "reflex_at_time":  _build_reflex_at_time,
    "hour_position":   _build_hour_position,
    "minute_position": _build_minute_position,
    "time_at_angle":   _build_time_at_angle,
    "coincide":        _build_coincide,
    "opposite":        _build_opposite,
    "gain_lose":       _build_gain_lose,
    "timezone":        _build_timezone,
}

LABELS = {
    "angle_at_time":   "Angle at given time",
    "reflex_at_time":  "Reflex angle at given time",
    "hour_position":   "Hour hand position",
    "minute_position": "Minute hand position",
    "time_at_angle":   "Time when hands make angle",
    "coincide":        "Hands coincide",
    "opposite":        "Hands opposite",
    "gain_lose":       "Gaining / losing time",
    "timezone":        "Longitude time shift",
}
