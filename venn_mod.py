"""Venn / Set Theory question generators.

All questions are numeric, using the standard 2-set and 3-set formulas.
"""


def _build_two_union(p):
    a, b, ab = p
    return {
        "prompt": f"|A|={a}, |B|={b}, |A∩B|={ab}. Find |A∪B|.",
        "answer": str(a + b - ab),
        "hint": "|A∪B| = |A| + |B| − |A∩B|",
        "qtype": "two_union",
    }


def _build_two_neither(p):
    a, b, ab = p
    neither = 100 - (a + b - ab)
    return {
        "prompt": (
            f"In a survey of 100 people: {a}% like X, {b}% like Y, "
            f"{ab}% like both. What % like neither?"
        ),
        "answer": str(neither),
        "hint": "Neither = 100 − |A∪B|",
        "qtype": "two_neither",
    }


def _build_two_intersection(p):
    a, b, union = p
    return {
        "prompt": f"|A|={a}, |B|={b}, |A∪B|={union}. Find |A∩B|.",
        "answer": str(a + b - union),
        "hint": "|A∩B| = |A| + |B| − |A∪B|",
        "qtype": "two_intersection",
    }


def _build_three_union(p):
    a, b, c, ab, bc, ca, abc = p
    return {
        "prompt": (
            f"|A|={a}, |B|={b}, |C|={c}, |A∩B|={ab}, |B∩C|={bc}, "
            f"|C∩A|={ca}, |A∩B∩C|={abc}. Find |A∪B∪C|."
        ),
        "answer": str(a + b + c - ab - bc - ca + abc),
        "hint": "|A∪B∪C| = Σ|A| − Σ|A∩B| + |A∩B∩C|",
        "qtype": "three_union",
    }


def _build_three_neither(p):
    a, b, c, ab, bc, ca, abc = p
    union = a + b + c - ab - bc - ca + abc
    return {
        "prompt": (
            f"Out of 100: |A|={a}, |B|={b}, |C|={c}, |A∩B|={ab}, "
            f"|B∩C|={bc}, |C∩A|={ca}, |A∩B∩C|={abc}. "
            f"How many like none?"
        ),
        "answer": str(100 - union),
        "hint": "Neither = 100 − |A∪B∪C|",
        "qtype": "three_neither",
    }


_TWO_PARAMS = [
    (a, b, ab)
    for a in range(30, 80, 5)
    for b in range(30, 80, 5)
    for ab in range(5, 30, 5)
    if ab <= min(a, b) and a + b - ab <= 100
]

_THREE_PARAMS = [
    (a, b, c, ab, bc, ca, abc)
    for a in (30, 40, 50)
    for b in (30, 40, 50)
    for c in (30, 40, 50)
    for ab in (5, 10, 15)
    for bc in (5, 10, 15)
    for ca in (5, 10, 15)
    for abc in (3, 5)
    if abc <= min(ab, bc, ca)
]


PARAMS = {
    "two_union":        _TWO_PARAMS,
    "two_neither":      _TWO_PARAMS,
    "two_intersection": _TWO_PARAMS,
    "three_union":      _THREE_PARAMS,
    "three_neither":    _THREE_PARAMS,
}

BUILDERS = {
    "two_union":        _build_two_union,
    "two_neither":      _build_two_neither,
    "two_intersection": _build_two_intersection,
    "three_union":      _build_three_union,
    "three_neither":    _build_three_neither,
}

LABELS = {
    "two_union":        "2-set union",
    "two_neither":      "2-set neither",
    "two_intersection": "2-set intersection",
    "three_union":      "3-set union",
    "three_neither":    "3-set neither",
}
