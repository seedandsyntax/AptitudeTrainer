"""Direction Sense question generators.

Subtypes:
    final_distance   — straight-line distance from start after a 2-leg walk
    final_distance_3 — straight-line distance from start after a 3-leg walk
    final_direction  — facing direction after a turn sequence
    shadow           — morning/evening shadow direction
    initial_facing   — given final direction and turns, find initial
"""

import itertools
import math


DIRECTIONS = ["North", "East", "South", "West"]
DIR_INDEX = {d: i for i, d in enumerate(DIRECTIONS)}


def _turn(facing, turn):
    idx = DIR_INDEX[facing]
    idx = (idx + 1) % 4 if turn == "right" else (idx - 1) % 4
    return DIRECTIONS[idx]


def _dx_dy(facing, dist):
    return {
        "North": (0, dist),
        "South": (0, -dist),
        "East":  (dist, 0),
        "West":  (-dist, 0),
    }[facing]


_PYTHAG = [
    (3, 4, 5), (6, 8, 10), (5, 12, 13), (8, 15, 17),
    (9, 12, 15), (7, 24, 25), (12, 16, 20), (20, 21, 29),
]


# ------------------------------------------------------------------
# Builders
# ------------------------------------------------------------------
def _build_final_distance(p):
    a, b, _ = p
    steps = [("East", a), ("North", b)]
    dx = sum(_dx_dy(d, n)[0] for d, n in steps)
    dy = sum(_dx_dy(d, n)[1] for d, n in steps)
    answer = int(round(math.hypot(dx, dy)))
    walk = ", ".join(f"{n} km {d}" for d, n in steps)
    return {
        "prompt": f"A person walks {walk}. How far from start (km)?",
        "answer": str(answer),
        "hint": "Draw the path, then apply Pythagoras.",
        "qtype": "final_distance",
    }


def _build_final_distance_3(p):
    a, b, c = p
    moves = [("East", a), ("North", b), ("West", c)]
    dx = sum(_dx_dy(d, n)[0] for d, n in moves)
    dy = sum(_dx_dy(d, n)[1] for d, n in moves)
    answer = int(round(math.hypot(dx, dy)))
    walk = ", ".join(f"{n} km {d}" for d, n in moves)
    return {
        "prompt": f"A person walks {walk}. How far from start (km)?",
        "answer": str(answer),
        "hint": "Sum x and y displacements, then Pythagoras.",
        "qtype": "final_distance_3",
    }


def _build_final_direction(p):
    facing, turns = p
    final = facing
    for t in turns:
        final = _turn(final, t)
    return {
        "prompt": (
            f"Start facing {facing}, then take "
            f"{', '.join(turns)}. Which direction now?"
        ),
        "answer": final.lower(),
        "hint": "Right = +90°, Left = −90°. Apply each turn.",
        "qtype": "final_direction",
    }


def _build_shadow(p):
    time_of_day, shadow_side = p
    shadow_dir = "West" if time_of_day == "morning" else "East"
    left_map = {
        "North": "West", "East": "North",
        "South": "East", "West": "South",
    }
    right_map = {
        "North": "East", "East": "South",
        "South": "West", "West": "North",
    }
    target_map = left_map if shadow_side == "left" else right_map
    ans = None
    for f, sd in target_map.items():
        if sd == shadow_dir:
            ans = f
            break
    return {
        "prompt": (
            f"On a {time_of_day}, a person's shadow falls exactly to "
            f"their {shadow_side}. Which direction are they facing?"
        ),
        "answer": ans.lower(),
        "hint": "Morning shadow = West. Evening shadow = East.",
        "qtype": "shadow",
    }


def _build_initial_facing(p):
    final_dir, turns = p
    init = final_dir
    for t in reversed(turns):
        init = _turn(init, "left" if t == "right" else "right")
    return {
        "prompt": (
            f"After taking {', '.join(turns)}, a person faces {final_dir}. "
            f"Which direction did they start facing?"
        ),
        "answer": init.lower(),
        "hint": "Reverse each turn (left ↔ right) and walk backward.",
        "qtype": "initial_facing",
    }


# ------------------------------------------------------------------
# Parameter enumeration (filtered to valid answers)
# ------------------------------------------------------------------
def _valid(params, builder):
    out = []
    for p in params:
        try:
            q = builder(p)
            if q["answer"] not in ("", "none"):
                out.append(p)
        except Exception:
            continue
    return out


_FD_PARAMS = [(a, b, c) for a, b, c in _PYTHAG]

_FD3_RAW = [(a, b, c) for a, b, c in _PYTHAG] + \
           [(b, a, c) for a, b, c in _PYTHAG]

_FINAL_DIR_RAW = []
for facing in DIRECTIONS:
    for seq_len in (2, 3):
        for turns in itertools.product(["left", "right"], repeat=seq_len):
            _FINAL_DIR_RAW.append((facing, list(turns)))

_SHADOW_PARAMS = [
    (t, s) for t in ("morning", "evening") for s in ("left", "right")
]

_INIT_RAW = []
for final in DIRECTIONS:
    for seq_len in (2, 3):
        for turns in itertools.product(["left", "right"], repeat=seq_len):
            _INIT_RAW.append((final, list(turns)))


PARAMS = {
    "final_distance":   _valid(_FD_PARAMS, _build_final_distance),
    "final_distance_3": _valid(_FD3_RAW, _build_final_distance_3),
    "final_direction":  _FINAL_DIR_RAW,
    "shadow":           _SHADOW_PARAMS,
    "initial_facing":   _INIT_RAW,
}

BUILDERS = {
    "final_distance":   _build_final_distance,
    "final_distance_3": _build_final_distance_3,
    "final_direction":  _build_final_direction,
    "shadow":           _build_shadow,
    "initial_facing":   _build_initial_facing,
}

LABELS = {
    "final_distance":   "Final distance (2-leg)",
    "final_distance_3": "Final distance (3-leg)",
    "final_direction":  "Final facing direction",
    "shadow":           "Shadow direction",
    "initial_facing":   "Initial facing from final",
}
