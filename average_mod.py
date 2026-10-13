"""Average question generators.

Subtypes:
    mean_basic    — arithmetic mean of a list
    median        — median of a list
    replacement   — replace one item, new average
    added_item    — add one item, find its value
    removed_item  — remove one item, find its value
    age_before    — average age t years ago
"""


def _fmt_num(x):
    if abs(x - round(x)) < 1e-6:
        return str(int(round(x)))
    return f"{x:.2f}".rstrip("0").rstrip(".")


def _build_mean_basic(p):
    avg = sum(p) / len(p)
    return {
        "prompt": f"Average of {', '.join(map(str, p))}? (2 decimals)",
        "answer": _fmt_num(avg),
        "hint": "Average = sum / count",
        "qtype": "mean_basic",
        "tolerance": 0.05,
    }


def _build_median(p):
    nums = sorted(p)
    n = len(nums)
    med = nums[n // 2] if n % 2 else (nums[n // 2 - 1] + nums[n // 2]) / 2
    return {
        "prompt": f"Median of {', '.join(map(str, p))}? (2 decimals)",
        "answer": _fmt_num(med),
        "hint": "Sort, then take the middle value (or mean of two middles).",
        "qtype": "median",
        "tolerance": 0.05,
    }


def _build_replacement(p):
    N, A, x, y = p
    new_avg = A + (y - x) / N
    return {
        "prompt": (
            f"Average of {N} items is {A}. If {x} is replaced by {y}, "
            f"new average? (2 decimals)"
        ),
        "answer": _fmt_num(new_avg),
        "hint": "New avg = old avg + (new − old)/N",
        "qtype": "replacement",
        "tolerance": 0.05,
    }


def _build_added_item(p):
    N, A, x = p
    new_item = A + (N + 1) * x
    return {
        "prompt": (
            f"Average of {N} items is {A}. A new item is added so the "
            f"new average becomes {A + x}. Find the new item."
        ),
        "answer": _fmt_num(new_item),
        "hint": "New item = A + (N+1) × x",
        "qtype": "added_item",
        "tolerance": 0.05,
    }


def _build_removed_item(p):
    N, A, x = p
    removed = A - (N - 1) * x
    return {
        "prompt": (
            f"Average of {N} items is {A}. One item is removed so the "
            f"new average becomes {A + x}. Find the removed item."
        ),
        "answer": _fmt_num(removed),
        "hint": "Removed = A − (N−1) × x",
        "qtype": "removed_item",
        "tolerance": 0.05,
    }


def _build_age_before(p):
    N, A, t = p
    return {
        "prompt": (
            f"Average age of {N} members is {A} years. "
            f"What was it {t} years ago?"
        ),
        "answer": str(A - t),
        "hint": "Each member is t years younger t years ago.",
        "qtype": "age_before",
    }


_MEAN_PARAMS = [
    (2, 4, 6, 8), (3, 6, 9, 12, 15), (5, 10, 15, 20),
    (10, 20, 30, 40, 50), (7, 14, 21), (1, 2, 3, 4, 5, 6),
    (12, 24, 36, 48), (100, 200, 300),
]

_MEDIAN_PARAMS = [
    (3, 1, 4, 1, 5), (2, 4, 6), (7, 3, 9, 1),
    (10, 20, 30, 40), (5, 6, 7, 8, 9, 10),
    (2, 3, 5, 7, 11, 13, 17),
]

_REPLACEMENT_PARAMS = [
    (N, A, x, y)
    for N in (5, 10, 15, 20, 25)
    for A in (20, 30, 40, 50, 60)
    for x in (10, 20, 30)
    for y in (40, 50, 60, 70, 80)
    if x != y
]

_ADDED_PARAMS = [
    (N, A, x)
    for N in (5, 10, 15, 20, 25)
    for A in (20, 30, 40, 50, 60)
    for x in (-5, -3, 2, 3, 5, 7, 10)
]

_REMOVED_PARAMS = [
    (N, A, x)
    for N in (5, 10, 15, 20, 25)
    for A in (20, 30, 40, 50, 60)
    for x in (-5, -3, 2, 3, 5, 7, 10)
]

_AGE_PARAMS = [
    (N, A, t)
    for N in (4, 5, 6, 8, 10)
    for A in (20, 25, 30, 35, 40)
    for t in (3, 5, 8, 10, 12)
    if A - t > 0
]

PARAMS = {
    "mean_basic":   _MEAN_PARAMS,
    "median":       _MEDIAN_PARAMS,
    "replacement":  _REPLACEMENT_PARAMS,
    "added_item":   _ADDED_PARAMS,
    "removed_item": _REMOVED_PARAMS,
    "age_before":   _AGE_PARAMS,
}

BUILDERS = {
    "mean_basic":   _build_mean_basic,
    "median":       _build_median,
    "replacement":  _build_replacement,
    "added_item":   _build_added_item,
    "removed_item": _build_removed_item,
    "age_before":   _build_age_before,
}

LABELS = {
    "mean_basic":   "Arithmetic mean",
    "median":       "Median",
    "replacement":  "Replacement effect",
    "added_item":   "Added item value",
    "removed_item": "Removed item value",
    "age_before":   "Average age t years ago",
}
