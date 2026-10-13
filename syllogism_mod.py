"""Syllogism question generators.

Subtype:
    two_premise — two premises, two candidate conclusions, ask which follow.

Answer codes:
    1  = only I follows
    2  = only II follows
    12 = both follow
    0  = neither follows
"""


TERMS = ["A", "B", "C"]
PREM_TYPES = ["all", "no", "some", "some_not"]

_LABEL = {
    "all":      "All {x} are {y}",
    "no":       "No {x} are {y}",
    "some":     "Some {x} are {y}",
    "some_not": "Some {x} are not {y}",
}


def _in_term(region, term_idx):
    return (region >> term_idx) & 1


def _satisfies(state, stmt_type, x_idx, y_idx):
    if stmt_type == "all":
        return not any(
            _in_term(r, x_idx) and not _in_term(r, y_idx) and r in state
            for r in range(1, 8)
        )
    if stmt_type == "no":
        return not any(
            _in_term(r, x_idx) and _in_term(r, y_idx) and r in state
            for r in range(1, 8)
        )
    if stmt_type == "some":
        return any(
            _in_term(r, x_idx) and _in_term(r, y_idx) and r in state
            for r in range(1, 8)
        )
    if stmt_type == "some_not":
        return any(
            _in_term(r, x_idx) and not _in_term(r, y_idx) and r in state
            for r in range(1, 8)
        )
    return False


_MODELS = [
    frozenset(i + 1 for i in range(7) if (mask >> i) & 1)
    for mask in range(1 << 7)
]


def _satisfying_models(premises):
    return [
        state for state in _MODELS
        if all(_satisfies(state, t, x, y) for t, x, y in premises)
    ]


def _follows(models, stmt_type, x_idx, y_idx):
    return bool(models) and all(
        _satisfies(m, stmt_type, x_idx, y_idx) for m in models
    )


def _describe(stmt_type, x_idx, y_idx):
    return _LABEL[stmt_type].format(x=TERMS[x_idx], y=TERMS[y_idx])


def _build(p):
    p1_type, p2_type, c1_type, c2_type = p

    premises = [(p1_type, 0, 1), (p2_type, 1, 2)]
    models = _satisfying_models(premises)
    if not models:
        return None

    f1 = _follows(models, c1_type, 0, 2)
    f2 = _follows(models, c2_type, 0, 2)

    if f1 and f2:
        ans = "12"
    elif f1:
        ans = "1"
    elif f2:
        ans = "2"
    else:
        ans = "0"

    prompt = (
        f"Statements:\n"
        f"  1. {_describe(p1_type, 0, 1)}.\n"
        f"  2. {_describe(p2_type, 1, 2)}.\n"
        f"Conclusions:\n"
        f"  I.  {_describe(c1_type, 0, 2)}.\n"
        f"  II. {_describe(c2_type, 0, 2)}.\n"
        f"Answer with: 1 (only I), 2 (only II), 12 (both), 0 (neither)."
    )

    return {
        "prompt": prompt,
        "answer": ans,
        "hint": (
            "Enumerate every model satisfying both premises, then check "
            "if the conclusion holds in all of them."
        ),
        "qtype": "two_premise",
    }


def _enumerate_params():
    conc_pairs = [(a, b) for a in PREM_TYPES for b in PREM_TYPES if a != b]
    out = []
    for p1 in PREM_TYPES:
        for p2 in PREM_TYPES:
            for c1, c2 in conc_pairs:
                if _build((p1, p2, c1, c2)) is not None:
                    out.append((p1, p2, c1, c2))
    return out


PARAMS = {
    "two_premise": _enumerate_params(),
}

BUILDERS = {
    "two_premise": _build,
}

LABELS = {
    "two_premise": "Two premises, two conclusions",
}
