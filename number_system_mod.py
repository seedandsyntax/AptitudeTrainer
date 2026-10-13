"""Number System question generators."""


def _last_digit_pow(base, exp):
    b = base % 10
    if b in (0, 1, 5, 6):
        return b
    if b == 4:
        return 4 if exp % 2 else 6
    if b == 9:
        return 9 if exp % 2 else 1
    cycles = {2: [2, 4, 8, 6], 3: [3, 9, 7, 1],
              7: [7, 9, 3, 1], 8: [8, 4, 2, 6]}
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
    return {
        "prompt": f"Last digit of {base}^{exp}?",
        "answer": str(_last_digit_pow(base, exp)),
        "hint": "Use unit-digit cycles: 2→2468, 3→3971, 7→7931, 8→8426.",
        "qtype": "last_digit",
    }


def _build_zeroes_factorial(p):
    n = p[0]
    total, k = 0, 5
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
    return {
        "prompt": f"Remainder of ({a} × {b}) ÷ {m}?",
        "answer": str((a * b) % m),
        "hint": "Reduce each factor mod m, multiply, reduce again.",
        "qtype": "remainder_prod",
    }


def _build_unit_digit_sum(p):
    b1, e1, b2, e2 = p
    ans = (_last_digit_pow(b1, e1) + _last_digit_pow(b2, e2)) % 10
    return {
        "prompt": f"Last digit of {b1}^{e1} + {b2}^{e2}?",
        "answer": str(ans),
        "hint": "Find each unit digit, then add mod 10.",
        "qtype": "unit_digit_sum",
    }


def _build_last_two_digits(p):
    base, exp = p
    ans = pow(base, exp, 100)
    return {
        "prompt": f"Last two digits of {base}^{exp}? (2-digit form)",
        "answer": f"{ans:02d}",
        "hint": "Ends-in-1: tens = units digit of (tens × exp-units). "
                "Ends-in-3/7/9: transform to 1. Even: transform to 24.",
        "qtype": "last_two_digits",
    }


def _build_negative_remainder(p):
    b, m = p
    sign = (-1) ** b
    ans = (sign * (m - 1)) % m
    return {
        "prompt": f"Remainder of ({m-1}^{b}) ÷ {m}?",
        "answer": str(ans),
        "hint": f"Treat {m-1} as −1. (−1)^k alternates.",
        "qtype": "negative_remainder",
    }


def _build_cutting_remainder(p):
    a, b, m = p
    from math import gcd
    k = gcd(a, m)
    a2, m2 = a // k, m // k
    r2 = (a2 * b) % m2
    ans = (r2 * k) % m
    return {
        "prompt": f"Remainder of ({a} × {b}) ÷ {m} using cutting concept?",
        "answer": str(ans),
        "hint": f"Divide numerator and divisor by their HCF = {k}.",
        "qtype": "cutting_remainder",
    }


def _build_plus1_remainder(p):
    a, n = p
    return {
        "prompt": f"Remainder of ({a+1}^{n}) ÷ {a}?",
        "answer": "1",
        "hint": "(A+1)^N ÷ A always leaves remainder 1.",
        "qtype": "plus1_remainder",
    }


def _build_minus1_remainder(p):
    a, n = p
    ans = 1 if n % 2 == 0 else a
    return {
        "prompt": f"Remainder of ({a}^{n}) ÷ {a+1}?",
        "answer": str(ans),
        "hint": "A^N mod (A+1): even N → 1, odd N → A.",
        "qtype": "minus1_remainder",
    }


_LAST_DIGIT_PARAMS = [
    (b, e) for b in (2, 3, 4, 7, 8, 9, 12, 13, 17, 18, 22, 23, 27, 28)
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
    (a, b, m) for a in range(12, 45, 3) for b in range(15, 50, 5)
    for m in (7, 11, 13)
]

_UNIT_SUM_PARAMS = [
    (b1, e1, b2, e2)
    for b1 in (2, 3, 4, 7, 8, 9) for e1 in (2, 3, 4, 5, 6, 7, 8, 9)
    for b2 in (2, 3, 4, 7, 8, 9) for e2 in (2, 3, 4, 5, 6, 7, 8, 9)
]

_LAST_TWO_PARAMS = [
    (b, e)
    for b in (11, 21, 31, 41, 51, 61, 71, 81, 91,
              13, 23, 33, 43, 53, 63, 73, 83, 93,
              17, 27, 37, 47, 57, 67, 77, 87, 97,
              19, 29, 39, 49, 59, 69, 79, 89, 99,
              12, 22, 32, 42, 52, 62, 72, 82, 92,
              14, 24, 34, 44, 54, 64, 74, 84, 94,
              16, 26, 36, 46, 56, 66, 76, 86, 96,
              18, 28, 38, 48, 58, 68, 78, 88, 98)
    for e in range(2, 16)
]

_NEG_REMAINDER_PARAMS = [
    (b, m) for m in (10, 20, 30, 40, 50, 100) for b in range(2, 11)
]

_CUTTING_PARAMS = [
    (a, b, m)
    for a in (20, 24, 30, 36, 40, 48, 60)
    for b in (3, 7, 11, 13)
    for m in (8, 12, 16, 24)
    if a != m
]

_PLUS1_PARAMS = [(a, n) for a in (4, 5, 6, 7, 8, 9, 10, 12, 15)
                 for n in range(2, 15)]

_MINUS1_PARAMS = [(a, n) for a in (3, 4, 5, 6, 7, 8, 9, 10, 11)
                  for n in range(2, 15)]


PARAMS = {
    "last_digit":         _LAST_DIGIT_PARAMS,
    "zeroes_factorial":   _ZEROES_PARAMS,
    "num_divisors":       _DIVISOR_PARAMS,
    "sum_divisors":       _DIVISOR_PARAMS,
    "remainder_prod":     _REMAINDER_PARAMS,
    "unit_digit_sum":     _UNIT_SUM_PARAMS,
    "last_two_digits":    _LAST_TWO_PARAMS,
    "negative_remainder": _NEG_REMAINDER_PARAMS,
    "cutting_remainder":  _CUTTING_PARAMS,
    "plus1_remainder":    _PLUS1_PARAMS,
    "minus1_remainder":   _MINUS1_PARAMS,
}

BUILDERS = {
    "last_digit":         _build_last_digit,
    "zeroes_factorial":   _build_zeroes_factorial,
    "num_divisors":       _build_num_divisors,
    "sum_divisors":       _build_sum_divisors,
    "remainder_prod":     _build_remainder_prod,
    "unit_digit_sum":     _build_unit_digit_sum,
    "last_two_digits":    _build_last_two_digits,
    "negative_remainder": _build_negative_remainder,
    "cutting_remainder":  _build_cutting_remainder,
    "plus1_remainder":    _build_plus1_remainder,
    "minus1_remainder":   _build_minus1_remainder,
}

LABELS = {
    "last_digit":         "Last digit of a^b",
    "zeroes_factorial":   "Trailing zeroes in n!",
    "num_divisors":       "Number of divisors",
    "sum_divisors":       "Sum of divisors",
    "remainder_prod":     "Remainder of a×b mod m",
    "unit_digit_sum":     "Last digit of a^b + c^d",
    "last_two_digits":    "Last two digits of a^b",
    "negative_remainder": "Negative remainder (−1 rule)",
    "cutting_remainder":  "Cutting concept (HCF)",
    "plus1_remainder":    "(A+1)^N mod A",
    "minus1_remainder":   "A^N mod (A+1)",
}
