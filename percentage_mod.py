"""Percentage question generators.

Subtypes:
    successive_change — net % change after +a% then +b%
    apply_change      — original V, apply a% then b%, find new value
    reverse_change    — after a% increase, value is V, find original
    consumption_rate  — expenditure fixed, rate changes by x%
    product_change    — A × B = C, A and B change, find C's change
"""


def _fmt_num(x):
    if abs(x - round(x)) < 1e-6:
        return str(int(round(x)))
    return f"{x:.2f}".rstrip("0").rstrip(".")


def _build_successive_change(p):
    a, b = p
    net = a + b + a * b / 100
    return {
        "prompt": (
            f"A quantity changes by {a}% and then by {b}%. "
            f"Net percentage change? (2 decimals)"
        ),
        "answer": _fmt_num(net),
        "hint": "Net = a + b + ab/100",
        "qtype": "successive_change",
        "tolerance": 0.05,
    }


def _build_apply_change(p):
    v, a, b = p
    final = v * (1 + a / 100) * (1 + b / 100)
    return {
        "prompt": (
            f"Starting value {v} changes by {a}% then by {b}%. "
            f"Final value? (2 decimals)"
        ),
        "answer": _fmt_num(final),
        "hint": "Multiply by (1 + a/100)(1 + b/100)",
        "qtype": "apply_change",
        "tolerance": 0.05,
    }


def _build_reverse_change(p):
    a, v = p
    orig = v / (1 + a / 100)
    return {
        "prompt": (
            f"After a {a}% increase, a value becomes {v}. "
            f"Original value? (2 decimals)"
        ),
        "answer": _fmt_num(orig),
        "hint": "Original = final / (1 + a/100)",
        "qtype": "reverse_change",
        "tolerance": 0.05,
    }


def _build_consumption_rate(p):
    x = p[0]
    pct = -100 * x / (100 + x)
    return {
        "prompt": (
            f"Expenditure is fixed. Rate rises by {x}%. "
            f"By what % does consumption fall? (2 decimals)"
        ),
        "answer": _fmt_num(pct),
        "hint": "C ∝ 1/R. Change = −100x / (100 + x)",
        "qtype": "consumption_rate",
        "tolerance": 0.05,
    }


def _build_product_change(p):
    a, b = p
    net = a + b + a * b / 100
    return {
        "prompt": (
            f"For A × B = C: if A changes by {a}% and B by {b}%, "
            f"net % change in C? (2 decimals)"
        ),
        "answer": _fmt_num(net),
        "hint": "Same successive-change formula.",
        "qtype": "product_change",
        "tolerance": 0.05,
    }


_PCTS = [-50, -40, -30, -25, -20, -15, -10, -5, 5, 10, 15, 20, 25, 30, 40, 50, 75, 100]

PARAMS = {
    "successive_change": [(a, b) for a in _PCTS for b in _PCTS],
    "apply_change":      [(v, a, b)
                          for v in (100, 200, 500, 800, 1000, 1500, 2000)
                          for a in (-20, -10, 5, 10, 20, 25)
                          for b in (-20, -10, 5, 10, 20, 25)],
    "reverse_change":    [(a, v)
                          for a in (10, 20, 25, 33, 50, 100)
                          for v in (110, 120, 200, 500, 1000, 2000)],
    "consumption_rate":  [(x,) for x in (5, 10, 15, 20, 25, 30, 40, 50, 60, 75, 100)],
    "product_change":    [(a, b) for a in _PCTS for b in _PCTS],
}

BUILDERS = {
    "successive_change": _build_successive_change,
    "apply_change":      _build_apply_change,
    "reverse_change":    _build_reverse_change,
    "consumption_rate":  _build_consumption_rate,
    "product_change":    _build_product_change,
}

LABELS = {
    "successive_change": "Successive change",
    "apply_change":      "Apply two changes",
    "reverse_change":    "Reverse a change",
    "consumption_rate":  "Fixed expenditure (C × R)",
    "product_change":    "Product change (A × B)",
}
