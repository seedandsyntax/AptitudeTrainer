"""Number System question generators.

Subtypes:
    last_digit        — last digit of a^b
    zeroes_factorial  — trailing zeroes in n!
    num_divisors      — number of divisors of n
    sum_divisors      — sum of divisors of n
    remainder_prod    — remainder of (a × b) mod m
    unit_digit_sum    — last digit of a^b + c^d
"""


def _last_digit_pow(base, exp):
    b = base % 10
    if b in (0, 1, 5, 6):
        return b
    if b == 4:
        return 4 if exp % 2 else 6
    if b == 9:
        return 9 if exp % 2 else 1
    cycles = {
        2: [2, 4, 8, 6],
        3: [3, 9, 7, 1],
        7: [7, 9, 3, 1],
        8: [8, 4, 2, 6],
    }
    return cycles[b][(exp - 1) % 4]


def _factorize(n):
    factors = {}
    d = 2
    while d * d <= n:
        while n % d == 0:
            factors[d] = factors.get(d, 0) + 1
            n //= d
        d += 1
    if n > 1:
        factors[n] = factors.get(n, 0) + 1
    return factors


def _build_last_digit(p):
    base, exp = p
    ans = _last_digit_pow(base, exp)
    return {
        "prompt": f"Last digit of {base}^{exp}?",
        "answer": str(ans),
        "hint": "Use the unit-digit cycle: 2→2468, 3→3971, 7→7931, 8→8426.",
        "qtype": "last_digit",
    }


def _build_zeroes_factorial(p):
    n = p[0]
    total = 0
    k = 5
    while k <= n:
        total += n // k
        k *= 5
    return {
        "prompt": f"Number of trailing zeroes in {n}!?",
        "answer": str(total),
        "hint": "Sum ⌊n/5⌋ + ⌊n/25⌋ + ⌊n/125⌋ + ...",
        "qtype": "zeroes_factorial",
    }


def _build_num_divisors(p):
    n = p[0]
    f = _factorize(n)
    ans = 1
    for e in f.values():
        ans *= e + 1
    return {
        "prompt": f"Number of divisors of {n}?",
        "answer": str(ans),
        "hint": "If n = ∏pᵢ^eᵢ, divisors = ∏(eᵢ+1)",
        "qtype": "num_divisors",
    }


def _build_sum_divisors(p):
    n = p[0]
    f = _factorize(n)
    ans = 1
    for prime, e in f.items():
        ans *= (prime ** (e + 1) - 1) // (prime - 1)
    return {
        "prompt": f"Sum of all divisors of {n}?",
        "answer": str(ans),
        "hint": "∏ (p^(e+1) − 1) / (p − 1)",
        "qtype": "sum_divisors",
    }


def _build_remainder_prod(p):
    a, b, m = p
    ans = (a * b) % m
    return {
        "prompt": f"Remainder of ({a} × {b}) ÷ {m}?",
        "answer": str(ans),
        "hint": "Reduce each factor mod m, then multiply and reduce again.",
        "qtype": "remainder_prod",
    }


def _build_unit_digit_sum(p):
    b1, e1, b2, e2 = p
    d1 = _last_digit_pow(b1, e1)
    d2 = _last_digit_pow(b2, e2)
    ans = (d1 + d2) % 10
    return {
        "prompt": f"Last digit of {b1}^{e1} + {b2}^{e2}?",
        "answer": str(ans),
        "hint": "Find each unit digit, then add mod 10.",
        "qtype": "unit_digit_sum",
    }


_LAST_DIGIT_PARAMS = [
    (b, e)
    for b in (2, 3, 4, 7, 8, 9, 12, 13, 17, 18, 22, 23, 27, 28)
    for e in range(2, 21)
]

_ZEROES_PARAMS = [
    (n,) for n in (10, 15, 20, 25, 30, 40, 50, 60, 75, 100, 125, 150, 200, 250)
]

_DIVISOR_PARAMS = [
    (n,) for n in (
        12, 18, 20, 24, 28, 30, 36, 40, 42, 48, 54, 56, 60, 66, 70, 72,
        78, 84, 88, 90, 96, 100, 102, 108, 120, 132, 144, 150, 180, 200,
        210, 240, 300, 360, 420, 500, 720, 1000,
    )
]

_REMAINDER_PARAMS = [
    (a, b, m)
    for a in range(12, 45, 3)
    for b in range(15, 50, 5)
    for m in (7, 11, 13)
]

_UNIT_SUM_PARAMS = [
    (b1, e1, b2, e2)
    for b1 in (2, 3, 4, 7, 8, 9)
    for e1 in (2, 3, 4, 5, 6, 7, 8, 9)
    for b2 in (2, 3, 4, 7, 8, 9)
    for e2 in (2, 3, 4, 5, 6, 7, 8, 9)
]

PARAMS = {
    "last_digit":       _LAST_DIGIT_PARAMS,
    "zeroes_factorial": _ZEROES_PARAMS,
    "num_divisors":     _DIVISOR_PARAMS,
    "sum_divisors":     _DIVISOR_PARAMS,
    "remainder_prod":   _REMAINDER_PARAMS,
    "unit_digit_sum":   _UNIT_SUM_PARAMS,
}

BUILDERS = {
    "last_digit":       _build_last_digit,
    "zeroes_factorial": _build_zeroes_factorial,
    "num_divisors":     _build_num_divisors,
    "sum_divisors":     _build_sum_divisors,
    "remainder_prod":   _build_remainder_prod,
    "unit_digit_sum":   _build_unit_digit_sum,
}

LABELS = {
    "last_digit":       "Last digit of a^b",
    "zeroes_factorial": "Trailing zeroes in n!",
    "num_divisors":     "Number of divisors",
    "sum_divisors":     "Sum of divisors",
    "remainder_prod":   "Remainder of a×b mod m",
    "unit_digit_sum":   "Last digit of a^b + c^d",
}
