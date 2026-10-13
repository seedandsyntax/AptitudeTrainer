"""Coding-decoding question generators.

Six word-based subtypes use GENERATORS (word → dict).
Two non-word subtypes (comparison, substitution) use PARAMS + BUILDERS.
"""

import random


WORDS = [
    "GARDEN", "SILENT", "ROCKET", "PLANET", "CAMERA", "WINDOW", "ORANGE",
    "YELLOW", "PENCIL", "SYSTEM", "NUMBER", "LAPTOP", "FRIEND", "MOTHER",
    "FATHER", "SCHOOL", "STUDENT", "TEACHER", "MUSIC", "EFFORT", "WINTER",
    "SUMMER", "SPRING", "AUTUMN", "FOREST", "RIVER", "MOUNTAIN", "VALLEY",
    "ISLAND", "DESERT", "CASTLE", "BRIDGE", "TEMPLE", "MARKET", "STATION",
]

FILLER = ["la", "che", "ne", "pa", "da", "ko", "rat", "lo", "to",
          "pe", "do", "ga", "mi", "re", "bo"]

_SAMPLE_WORDS = ["failure", "key", "success", "money", "gold", "silver",
                 "water", "fire", "earth", "wind", "light", "dark"]


def _lhs(ch):
    return ord(ch) - 64


def _rhs(ch):
    return 27 - _lhs(ch)


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


def _build_prompt(target, encoder, n_examples):
    pool = [w for w in WORDS if w != target]
    examples = random.sample(pool, n_examples)
    clauses = [f"{e} is coded as {encoder(e)}" for e in examples]
    joined = ", and ".join(clauses)
    return f"If {joined}, then code for {target} is?"


def _n_examples():
    return 1 if random.random() < 0.6 else 2


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


# ------------------------------------------------------------------
# Non-word subtypes
# ------------------------------------------------------------------
def _build_comparison(p):
    words, codes, seed = p
    rng = random.Random(seed)
    c1 = codes[0:3][:]
    c2 = codes[0:1] + codes[3:5]
    c3 = codes[1:2] + codes[3:4] + codes[5:6]
    rng.shuffle(c1)
    rng.shuffle(c2)
    rng.shuffle(c3)
    prompt = (
        f"In a certain code:\n"
        f"  '{words[0]} {words[1]} {words[2]}' is written as "
        f"'{' '.join(c1)}'\n"
        f"  '{words[0]} {words[3]} {words[4]}' is written as "
        f"'{' '.join(c2)}'\n"
        f"  '{words[1]} {words[3]} {words[5]}' is written as "
        f"'{' '.join(c3)}'\n"
        f"What is the code for '{words[0]}'?"
    )
    return {
        "prompt": prompt,
        "answer": codes[0],
        "hint": "Find the code common to the first two sentences.",
        "qtype": "comparison",
    }


_SUBSTITUTION_CHAINS = [
    ["cat", "dog", "rat", "bat", "cow"],
    ["sun", "moon", "star", "sky", "sea"],
    ["red", "blue", "green", "yellow", "pink"],
    ["king", "queen", "prince", "princess", "duke"],
    ["rice", "wheat", "barley", "oats", "corn"],
    ["car", "bus", "train", "plane", "ship"],
]


def _build_substitution(p):
    chain = p[0]
    lines = [
        f"In a certain language, {a} is called {b}."
        for a, b in zip(chain[:-1], chain[1:])
    ]
    prompt = "\n".join(lines) + (
        f"\nWhat is '{chain[0]}' called in this language?"
    )
    return {
        "prompt": prompt,
        "answer": chain[1].lower(),
        "hint": "Direct lookup: the first substitution is the answer.",
        "qtype": "substitution",
    }


# ------------------------------------------------------------------
# Public dicts
# ------------------------------------------------------------------
GENERATORS = {
    "reverse_digits":      gen_reverse_digits,
    "digit_sum":           gen_digit_sum,
    "sum_position_digits": gen_sum_position_digits,
    "shift_alternate":     gen_shift_alternate,
    "split_reverse_shift": gen_split_reverse_shift,
    "rhs_replace":         gen_rhs_replace,
}

WORD_BASED = set(GENERATORS.keys())

_COMPARISON_PARAMS = []
for seed in range(60):
    rng = random.Random(seed)
    _COMPARISON_PARAMS.append(
        (rng.sample(_SAMPLE_WORDS, 6), rng.sample(FILLER, 6), seed)
    )

_SUBSTITUTION_PARAMS = [(chain,) for chain in _SUBSTITUTION_CHAINS]

PARAMS = {
    "comparison":   _COMPARISON_PARAMS,
    "substitution": _SUBSTITUTION_PARAMS,
}

BUILDERS = {
    "comparison":   _build_comparison,
    "substitution": _build_substitution,
}

LABELS = {
    "reverse_digits":      "Reverse digits",
    "digit_sum":           "Digit sum",
    "sum_position_digits": "Sum of position digits",
    "shift_alternate":     "Shift +1,+2 alternating",
    "split_reverse_shift": "Split + reverse halves + shift +2",
    "rhs_replace":         "RHS position replacement",
    "comparison":          "Comparison across sentences",
    "substitution":        "Word substitution chain",
}
