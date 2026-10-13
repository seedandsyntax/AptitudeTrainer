"""HCF / LCM question generators.

Subtypes:
    lcm_basic                — LCM of two numbers
    hcf_basic                — HCF of two numbers
    lcm_unique_remainder     — number with unique remainder r for a,b,c
    lcm_negative_remainder   — remainders convert to same negative
    hcf_unique_remainder     — greatest number dividing a,b,c with rem r
    hcf_different_remainders — greatest number with different remainders
    hcf_same_remainder       — greatest number leaving same unknown rem
    hcf_lcm_pair             — given LCM, HCF, one number → find other
"""

import math


def _lcm(a, b):
    return a * b // math.gcd(a, b)


def _lcm3(a, b, c):
    return _lcm(_lcm(a, b), c)


def _build_lcm_basic(p):
    a, b = p
    return {
        "prompt": f"LCM of {a} and {b}?",
        "answer": str(_lcm(a, b)),
        "hint": "LCM = a × b ÷ HCF",
        "qtype": "lcm_basic",
    }


def _build_hcf_basic(p):
    a, b = p
    return {
        "prompt": f"HCF of {a} and {b}?",
        "answer": str(math.gcd(a, b)),
        "hint": "Euclidean algorithm, or prime factorization.",
        "qtype": "hcf_basic",
    }


def _build_lcm_unique_remainder(p):
    a, b, c, r = p
    L = _lcm3(a, b, c)
    return {
        "prompt": (
            f"Smallest number which when divided by {a}, {b}, {c} "
            f"leaves remainder {r} in each case?"
        ),
        "answer": str(L + r),
        "hint": "Target = LCM(a,b,c) + r",
        "qtype": "lcm_unique_remainder",
    }


def _build_lcm_negative_remainder(p):
    a, b, c, r = p
    L = _lcm3(a, b, c)
    r1, r2, r3 = a - r, b - r, c - r
    return {
        "prompt": (
            f"Smallest number which when divided by {a}, {b}, {c} leaves "
            f"remainders {r1}, {r2}, {r3} respectively?"
        ),
        "answer": str(L - r),
        "hint": "Convert remainders to same negative r; target = LCM − r",
        "qtype": "lcm_negative_remainder",
    }


def _build_hcf_unique_remainder(p):
    a, b, c, r = p
    ans = math.gcd(math.gcd(a - r, b - r), c - r)
    return {
        "prompt": (
            f"Greatest number that divides {a}, {b}, {c} leaving "
            f"remainder {r} in each case?"
        ),
        "answer": str(ans),
        "hint": "HCF(a−r, b−r, c−r)",
        "qtype": "hcf_unique_remainder",
    }


def _build_hcf_different_remainders(p):
    a, b, c, r1, r2, r3 = p
    ans = math.gcd(math.gcd(a - r1, b - r2), c - r3)
    return {
        "prompt": (
            f"Greatest number that divides {a}, {b}, {c} leaving "
            f"remainders {r1}, {r2}, {r3} respectively?"
        ),
        "answer": str(ans),
        "hint": "HCF(a−r1, b−r2, c−r3)",
        "qtype": "hcf_different_remainders",
    }


def _build_hcf_same_remainder(p):
    a, b, c = p
    ans = math.gcd(math.gcd(b - a, c - b), c - a)
    return {
        "prompt": (
            f"Greatest number that divides {a}, {b}, {c} leaving "
            f"the same remainder in each case?"
        ),
        "answer": str(ans),
        "hint": "HCF(|a−b|, |b−c|, |a−c|)",
        "qtype": "hcf_same_remainder",
    }


def _build_hcf_lcm_pair(p):
    a, L, H = p
    ans = (L * H) // a
    return {
        "prompt": (
            f"HCF of two numbers is {H} and LCM is {L}. "
            f"One number is {a}. Find the other."
        ),
        "answer": str(ans),
        "hint": "Other = (LCM × HCF) ÷ known number",
        "qtype": "hcf_lcm_pair",
    }


# ------------------------------------------------------------------
# Parameter enumeration
# ------------------------------------------------------------------
_SMALL = list(range(2, 25))


def _pairs():
    out = []
    for a in _SMALL:
        for b in range(a + 1, a + 20):
            out.append((a, b))
    return out


_LCM_BASIC_PARAMS = _pairs()
_HCF_BASIC_PARAMS = _pairs()

_LCM_UNIQUE_PARAMS = []
for a in (4, 6, 8, 10, 12):
    for b in (6, 9, 12, 15):
        for c in (10, 15, 20):
            for r in (1, 2, 3, 4):
                if r < min(a, b, c):
                    _LCM_UNIQUE_PARAMS.append((a, b, c, r))

_LCM_NEG_PARAMS = []
for a in (5, 6, 7, 8, 10, 12):
    for b in (7, 9, 12, 14, 15):
        for c in (11, 15, 20, 25):
            for r in (1, 2, 3):
                if r < min(a, b, c):
                    _LCM_NEG_PARAMS.append((a, b, c, r))

_HCF_UNIQUE_PARAMS = []
for a in (410, 751, 1030, 500, 700, 900, 350, 480):
    for b in (600, 800, 1000, 720, 1050):
        for c in (500, 850, 1200, 950):
            for r in (7, 10, 12, 15):
                if r < min(a, b, c):
                    _HCF_UNIQUE_PARAMS.append((a, b, c, r))

_HCF_DIFF_PARAMS = []
for a in (148, 246, 623, 240, 500, 700):
    for b in (300, 550, 800, 900):
        for c in (400, 750, 1100):
            for r1, r2, r3 in [(4, 6, 11), (5, 7, 10), (3, 8, 12)]:
                if r1 < a and r2 < b and r3 < c:
                    _HCF_DIFF_PARAMS.append((a, b, c, r1, r2, r3))

_HCF_SAME_PARAMS = []
for a in (43, 91, 183, 250, 300, 400, 700):
    for b in (100, 200, 350, 500, 600):
        for c in (250, 400, 550, 800):
            if a < b < c:
                _HCF_SAME_PARAMS.append((a, b, c))

_HCF_LCM_PAIR_PARAMS = []
for a in (12, 15, 18, 20, 24, 30, 36, 40, 45, 60):
    for b in (18, 24, 30, 36, 40, 45, 60, 72, 90):
        if a == b:
            continue
        L = _lcm(a, b)
        H = math.gcd(a, b)
        _HCF_LCM_PAIR_PARAMS.append((a, L, H))
        _HCF_LCM_PAIR_PARAMS.append((b, L, H))


PARAMS = {
    "lcm_basic":                _LCM_BASIC_PARAMS,
    "hcf_basic":                _HCF_BASIC_PARAMS,
    "lcm_unique_remainder":     _LCM_UNIQUE_PARAMS,
    "lcm_negative_remainder":   _LCM_NEG_PARAMS,
    "hcf_unique_remainder":     _HCF_UNIQUE_PARAMS,
    "hcf_different_remainders": _HCF_DIFF_PARAMS,
    "hcf_same_remainder":       _HCF_SAME_PARAMS,
    "hcf_lcm_pair":             _HCF_LCM_PAIR_PARAMS,
}

BUILDERS = {
    "lcm_basic":                _build_lcm_basic,
    "hcf_basic":                _build_hcf_basic,
    "lcm_unique_remainder":     _build_lcm_unique_remainder,
    "lcm_negative_remainder":   _build_lcm_negative_remainder,
    "hcf_unique_remainder":     _build_hcf_unique_remainder,
    "hcf_different_remainders": _build_hcf_different_remainders,
    "hcf_same_remainder":       _build_hcf_same_remainder,
    "hcf_lcm_pair":             _build_hcf_lcm_pair,
}

LABELS = {
    "lcm_basic":                "LCM of two numbers",
    "hcf_basic":                "HCF of two numbers",
    "lcm_unique_remainder":     "LCM + unique remainder",
    "lcm_negative_remainder":   "LCM − negative remainder",
    "hcf_unique_remainder":     "HCF + unique remainder",
    "hcf_different_remainders": "HCF + different remainders",
    "hcf_same_remainder":       "HCF + same unknown remainder",
    "hcf_lcm_pair":             "LCM × HCF = a × b",
}
