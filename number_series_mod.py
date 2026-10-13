"""Number-series question generators."""


PRIMES = [
    2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47,
    53, 59, 61, 67, 71, 73, 79, 83, 89, 97, 101, 103, 107,
    109, 113]


def _fmt(seq):
    return ", ".join(map(str, seq)) + ", ?"


def _q(seq, answer, hint, qtype, difficulty):
    return {
        "prompt": _fmt(seq),
        "answer": str(answer),
        "hint": hint,
        "qtype": qtype,
        "difficulty": difficulty,
    }


def _build_arithmetic(p):
    a, d = p
    seq = [a + d * i for i in range(5)]
    return _q(seq, a + d * 5, f"Add {d} each step.", "arithmetic", 1)


def _build_geometric(p):
    a, r = p
    seq = [a * (r ** i) for i in range(5)]
    return _q(seq, a * (r ** 5), f"Multiply by {r} each step.", "geometric", 1)


def _build_subtraction(p):
    a, d = p
    seq = [a - d * i for i in range(5)]
    return _q(seq, a - d * 5, f"Subtract {d} each step.", "subtraction", 1)


def _build_division(p):
    a, r = p
    start = a * (r ** 5)
    seq = [start // (r ** i) for i in range(5)]
    return _q(seq, a, f"Divide by {r} each step.", "division", 2)


def _build_fibonacci(p):
    a, b = p
    seq = [a, b]
    for _ in range(3):
        seq.append(seq[-1] + seq[-2])
    return _q(seq, seq[-1] + seq[-2],
              "Each term = sum of the previous two.", "fibonacci", 1)


def _build_prod_prev_two(p):
    a, b = p
    seq = [a, b]
    for _ in range(3):
        seq.append(seq[-1] * seq[-2])
    return _q(seq, seq[-1] * seq[-2],
              "Each term = product of the previous two.", "prod_prev_two", 3)


def _build_squares(p):
    start, c = p
    seq = [(start + i) ** 2 + c for i in range(5)]
    return _q(seq, (start + 5) ** 2 + c,
              "Consecutive squares" + (f" + {c}" if c else ""), "squares", 2)


def _build_cubes(p):
    start, c = p
    seq = [(start + i) ** 3 + c for i in range(4)]
    return _q(seq, (start + 4) ** 3 + c,
              "Consecutive cubes" + (f" + {c}" if c else ""), "cubes", 2)


def _build_prime(p):
    start = p[0]
    seq = PRIMES[start:start + 5]
    return _q(seq, PRIMES[start + 5], "Consecutive primes.", "prime", 2)


def _build_diff_of_diff(p):
    a, d, incr = p
    seq = [a]
    cur_d = d
    for _ in range(5):
        seq.append(seq[-1] + cur_d)
        cur_d += incr
    return _q(seq, seq[-1] + cur_d,
              f"First differences increase by {incr}.", "diff_of_diff", 3)


def _build_alt_primes(p):
    start = p[0]
    seq = PRIMES[start:start + 10:2]
    return _q(seq, PRIMES[start + 10], "Every other prime.", "alt_primes", 3)


def _build_square_plus(p):
    a = p[0]
    seq = [a]
    for i in range(1, 5):
        seq.append(seq[-1] + i ** 2)
    return _q(seq, seq[-1] + 25,
              "Add consecutive squares: +1², +2², +3², ...", "square_plus", 3)


def _build_cube_plus(p):
    a = p[0]
    seq = [a]
    for i in range(1, 4):
        seq.append(seq[-1] + i ** 3)
    return _q(seq, seq[-1] + 64,
              "Add consecutive cubes: +1³, +2³, +3³, ...", "cube_plus", 3)


def _build_twin_series(p):
    a1, d1, a2, d2 = p
    seq = [a1, a2, a1 + d1, a2 + d2, a1 + 2 * d1, a2 + 2 * d2]
    return _q(seq, a1 + 3 * d1,
              "Odd-position and even-position terms form separate series.",
              "twin_series", 4)


def _build_diff_mult(p):
    a, d, r = p
    seq = [a]
    cur_d = d
    for _ in range(4):
        seq.append(seq[-1] + cur_d)
        cur_d *= r
    return _q(seq, seq[-1] + cur_d,
              f"First differences multiply by {r}.", "diff_mult", 4)


def _build_digital_op_pool():
    pool = []
    for n in range(22, 100):
        if "0" in str(n):
            continue
        s = [n]
        for _ in range(3):
            digits = [int(d) for d in str(s[-1])]
            prod = 1
            for d in digits:
                prod *= d
            s.append(prod)
        if len(set(s[:4])) == 4:
            pool.append(s)
    return pool


_DIGITAL_OP_POOL = _build_digital_op_pool()


def _build_digital_op(p):
    s = p[0]
    return _q(s[:3], s[3],
              "Multiply the digits of the previous term.", "digital_op", 4)


def _build_tri_series(p):
    a1, d1, a2, d2, a3, d3 = p
    seq = [a1, a2, a3, a1 + d1, a2 + d2, a3 + d3]
    return _q(seq, a1 + 2 * d1,
              "Three interleaved series (positions 1,4,7 / 2,5,8 / 3,6,9).",
              "tri_series", 5)


def _build_misc_mul_add(p):
    a = p[0]
    seq = [a]
    m, c = 2, 1
    for _ in range(4):
        seq.append(seq[-1] * m + c)
        m += 1
        c += 1
    return _q(seq, seq[-1] * m + c,
              "Pattern: ×2+1, ×3+2, ×4+3, ...", "misc_mul_add", 5)


def _build_decimal_fraction(p):
    a, r0, dr = p
    seq = [a]
    mult = r0
    for _ in range(4):
        seq.append(int(round(seq[-1] * mult)))
        mult += dr
    nxt = int(round(seq[-1] * mult))
    return _q(seq, nxt,
              f"Multiply by {r0}, then +{dr} each step.",
              "decimal_fraction", 3)


def _build_alt_square_diff(p):
    a = p[0]
    seq = [a]
    n = 2
    for i in range(5):
        step = n ** 2
        seq.append(seq[-1] + step if i % 2 == 0 else seq[-1] - step)
        n += 1
    step = n ** 2
    ans = seq[-1] + step if 5 % 2 == 0 else seq[-1] - step
    return _q(seq, ans,
              "Alternately add and subtract consecutive squares: "
              "+2², −3², +4², ...",
              "alt_square_diff", 4)


_N_PRIMES = len(PRIMES)


PARAMS = {
    "arithmetic":       [(a, d) for a in range(2, 31) for d in range(2, 16)],
    "geometric":        [(a, r) for a in range(1, 11) for r in range(2, 7)],
    "subtraction":      [(a, d) for a in range(60, 200, 5) for d in range(2, 10)],
    "division":         ([(a, 2) for a in range(1, 21)]
                         + [(a, 3) for a in range(1, 8)]
                         + [(a, 4) for a in range(1, 4)]),
    "fibonacci":        [(a, b) for a in range(1, 11) for b in range(1, 11)],
    "prod_prev_two":    [(1, 2), (1, 3), (1, 4),
                         (2, 1), (2, 3), (2, 4),
                         (3, 1), (3, 2)],
    "squares":          [(s, c) for s in range(1, 11) for c in range(0, 11)],
    "cubes":            [(s, c) for s in range(1, 11) for c in range(0, 11)],
    "prime":            [(i,) for i in range(0, _N_PRIMES - 6)],
    "diff_of_diff":     [(a, d, i)
                         for a in range(1, 21)
                         for d in range(2, 11)
                         for i in range(2, 9)],
    "alt_primes":       [(i,) for i in range(0, _N_PRIMES - 11)],
    "square_plus":      [(a,) for a in range(1, 51)],
    "cube_plus":        [(a,) for a in range(1, 51)],
    "twin_series":      [(a1, d1, a2, d2)
                         for a1 in range(2, 16) for d1 in range(2, 9)
                         for a2 in range(15, 31) for d2 in range(3, 11)],
    "diff_mult":        [(a, d, r)
                         for a in range(5, 31)
                         for d in range(1, 6)
                         for r in range(2, 6)],
    "digital_op":       [(s,) for s in _DIGITAL_OP_POOL],
    "tri_series":       [(a1, d1, a2, d2, a3, d3)
                         for a1 in range(2, 11) for d1 in range(2, 7)
                         for a2 in range(10, 21) for d2 in range(3, 9)
                         for a3 in range(20, 41) for d3 in range(4, 11)],
    "misc_mul_add":     [(a,) for a in range(1, 51)],
    "decimal_fraction": [(a, r0, dr)
                         for a in (10, 20, 30, 40, 50, 60)
                         for r0 in (1, 2)
                         for dr in (1, 2)],
    "alt_square_diff":  [(a,) for a in range(5, 100, 3)],
}

BUILDERS = {
    "arithmetic":       _build_arithmetic,
    "geometric":        _build_geometric,
    "subtraction":      _build_subtraction,
    "division":         _build_division,
    "fibonacci":        _build_fibonacci,
    "prod_prev_two":    _build_prod_prev_two,
    "squares":          _build_squares,
    "cubes":            _build_cubes,
    "prime":            _build_prime,
    "diff_of_diff":     _build_diff_of_diff,
    "alt_primes":       _build_alt_primes,
    "square_plus":      _build_square_plus,
    "cube_plus":        _build_cube_plus,
    "twin_series":      _build_twin_series,
    "diff_mult":        _build_diff_mult,
    "digital_op":       _build_digital_op,
    "tri_series":       _build_tri_series,
    "misc_mul_add":     _build_misc_mul_add,
    "decimal_fraction": _build_decimal_fraction,
    "alt_square_diff":  _build_alt_square_diff,
}

LABELS = {
    "arithmetic":       "Arithmetic (+d)",
    "geometric":        "Geometric (×r)",
    "subtraction":      "Subtraction (−d)",
    "division":         "Division (÷r)",
    "fibonacci":        "Fibonacci (sum of prev 2)",
    "prod_prev_two":    "Product of prev 2",
    "squares":          "Squares (n²+c)",
    "cubes":            "Cubes (n³+c)",
    "prime":            "Primes",
    "diff_of_diff":     "Difference of differences",
    "alt_primes":       "Alternate primes",
    "square_plus":      "Add consecutive squares",
    "cube_plus":        "Add consecutive cubes",
    "twin_series":      "Twin series (2 interleaved)",
    "diff_mult":        "Differences × constant",
    "digital_op":       "Digital operation (digit product)",
    "tri_series":       "Tri series (3 interleaved)",
    "misc_mul_add":     "Misc (×2+1, ×3+2, ...)",
    "decimal_fraction": "Decimal fraction multipliers",
    "alt_square_diff":  "Alternate ± consecutive squares",
}
