"""Coding-decoding question generators.

Each generator takes a word and returns a dict with keys:
    prompt, answer, hint, qtype
"""

import random


WORDS = [
    "GARDEN", "ROCKET", "PLANET", "CAMERA", "WINDOW", "ORANGE", "POTATO",
    "YELLOW", "PENCIL", "SYSTEM", "NUMBER", "LAPTOP", "FRIEND", "MOTHER",
    "FATHER", "SCHOOL", "STUDENT", "TEACHER", "MUSIC", "EFFORT", "WINTER",
    "SUMMER", "SPRING", "AUTUMN", "FOREST", "RIVER", "MOUNTAIN", "VALLEY",
    "ISLAND", "DESERT", "CASTLE", "BRIDGE", "TEMPLE", "MARKET", "STATION",
    "MONICA", "EVERETT", "SILENT", "WITCH", "ABYSS", "COSMOS", "WITHER"
]


def _lhs(ch):
    return ord(ch) - 64


def _rhs(ch):
    return 27 - _lhs(ch)


# ------------------------------------------------------------------
# Encoders
# ------------------------------------------------------------------
def encode_reverse_digits(word):
    return "".join(f"{_lhs(c):02d}"[::-1] for c in word)


def encode_digit_sum(word):
    total = sum(_lhs(c) for c in word)
    return str(sum(int(d) for d in str(total)))


def encode_sum_position_digits(word):
    return str(sum(sum(int(d) for d in str(_lhs(c))) for c in word))


def encode_shift_alternate(word):
    shifts = (1, 2)
    return "".join(
        chr(((_lhs(c) - 1 + shifts[i % 2]) % 26) + 65)
        for i, c in enumerate(word)
    )


def encode_split_reverse_shift(word):
    mid = (len(word) + 1) // 2
    combined = word[:mid][::-1] + word[mid:][::-1]
    return "".join(chr(((_lhs(c) - 1 + 2) % 26) + 65) for c in combined)


def encode_rhs_replace(word):
    return "".join(chr(_rhs(c) + 64) for c in word)


# ------------------------------------------------------------------
# Prompt builder
# ------------------------------------------------------------------
def _build_prompt(target, encoder, n_examples):
    """Return a dynamic prompt with 1 or 2 worked examples, distinct from target."""
    pool = [w for w in WORDS if w != target]
    examples = random.sample(pool, n_examples)
    clauses = [f"{e} is coded as {encoder(e)}" for e in examples]
    joined = ", and ".join(clauses)
    return f"If {joined}, then code for {target} is?"


def _n_examples():
    # ~60% single-example, ~40% two-example, so both formats are drilled
    return 1 if random.random() < 0.6 else 2


# ------------------------------------------------------------------
# Generators
# ------------------------------------------------------------------
def gen_reverse_digits(word):
    return {
        "prompt": _build_prompt(word, encode_reverse_digits, _n_examples()),
        "answer": encode_reverse_digits(word),
        "hint": "Reverse the digits of each letter's LHS position.",
        "qtype": "reverse_digits",
    }


def gen_digit_sum(word):
    return {
        "prompt": _build_prompt(word, encode_digit_sum, _n_examples()),
        "answer": encode_digit_sum(word),
        "hint": "Sum LHS positions, then digit-sum once.",
        "qtype": "digit_sum",
    }


def gen_sum_position_digits(word):
    return {
        "prompt": _build_prompt(word, encode_sum_position_digits, _n_examples()),
        "answer": encode_sum_position_digits(word),
        "hint": "Digit-sum each position, then add them.",
        "qtype": "sum_position_digits",
    }


def gen_shift_alternate(word):
    return {
        "prompt": _build_prompt(word, encode_shift_alternate, _n_examples()),
        "answer": encode_shift_alternate(word),
        "hint": "Shift letters by +1, +2, +1, +2, ...",
        "qtype": "shift_alternate",
    }


def gen_split_reverse_shift(word):
    return {
        "prompt": _build_prompt(word, encode_split_reverse_shift, _n_examples()),
        "answer": encode_split_reverse_shift(word),
        "hint": "Split halves, reverse each, then shift +2.",
        "qtype": "split_reverse_shift",
    }


def gen_rhs_replace(word):
    return {
        "prompt": _build_prompt(word, encode_rhs_replace, _n_examples()),
        "answer": encode_rhs_replace(word),
        "hint": "Replace each letter with its RHS-position letter.",
        "qtype": "rhs_replace",
    }


GENERATORS = {
    "reverse_digits":      gen_reverse_digits,
    "digit_sum":           gen_digit_sum,
    "sum_position_digits": gen_sum_position_digits,
    "shift_alternate":     gen_shift_alternate,
    "split_reverse_shift": gen_split_reverse_shift,
    "rhs_replace":         gen_rhs_replace,
}

LABELS = {
    "reverse_digits":      "Reverse digits",
    "digit_sum":           "Digit sum",
    "sum_position_digits": "Sum of position digits",
    "shift_alternate":     "Shift +1,+2 alternating",
    "split_reverse_shift": "Split + reverse halves + shift +2",
    "rhs_replace":         "RHS position replacement",
}
