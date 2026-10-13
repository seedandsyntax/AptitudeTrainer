"""Sitting Arrangement question generators.

Subtypes:
    linear            — N people in a row facing north
    two_row           — boys' row + girls' row facing each other
    circular_inward   — N people around a circle facing centre
    circular_outward  — N people around a circle facing away
"""

import itertools
import random


def _linear_pool(people, N):
    pool = []
    idx = {p: i for i, p in enumerate(people)}
    for p in range(N):
        i = idx[p]
        pool.append((f"P{p+1} sits at position {i+1}",
                     lambda a, p=p, i=i: a[i] == p))
        if i == 0:
            pool.append((f"P{p+1} sits at the left end",
                         lambda a, p=p: a[0] == p))
        if i == N - 1:
            pool.append((f"P{p+1} sits at the right end",
                         lambda a, p=p: a[-1] == p))
        if i + 1 < N:
            q = people[i + 1]
            pool.append((f"P{p+1} sits immediately left of P{q+1}",
                         lambda a, p=p, q=q: a.index(q) == a.index(p) + 1))
        if i > 0:
            q = people[i - 1]
            pool.append((f"P{p+1} sits immediately right of P{q+1}",
                         lambda a, p=p, q=q: a.index(q) == a.index(p) - 1))
        if 0 < i < N - 1:
            lo, hi = people[i - 1], people[i + 1]
            pool.append((f"P{p+1} sits between P{lo+1} and P{hi+1}",
                         lambda a, p=p, x=lo, y=hi:
                             min(a.index(x), a.index(y)) < a.index(p)
                             < max(a.index(x), a.index(y))))
    return pool


def _count_linear(pool, N):
    count = 0
    for perm in itertools.permutations(range(N)):
        if all(pred(perm) for _, pred in pool):
            count += 1
            if count > 1:
                return count
    return count


def _try_linear(N, seed):
    rng = random.Random(seed)
    people = list(range(N))
    rng.shuffle(people)
    pool = _linear_pool(people, N)
    rng.shuffle(pool)
    kept = []
    for text, pred in pool:
        kept.append((text, pred))
        if _count_linear(kept, N) == 1:
            return people, kept
    return None


def _build_linear(p):
    N, seed = p
    result = _try_linear(N, seed)
    if result is None:
        return None
    people, clues = result
    rng = random.Random(seed * 31 + 7)
    k = rng.randint(0, N - 1)
    answer = people[k] + 1
    lines = [f"{N} people P1..P{N} sit in a row facing north.", "Clues:"]
    for text, _ in clues:
        lines.append(f"  - {text}")
    lines.append(f"\nWho sits at position {k+1} from the left? (person number)")
    return {
        "prompt": "\n".join(lines),
        "answer": str(answer),
        "hint": "Draw the row and place each person.",
        "qtype": "linear",
    }


def _two_row_pool(boys, girls, M):
    pool = []
    for i in range(M):
        bp, gp = boys[i], girls[i]
        pool.append((f"Boy B{bp+1} sits at position {i+1}",
                     lambda s, bp=bp, i=i: s[0][i] == bp))
        pool.append((f"Girl G{gp+1} sits at position {i+1}",
                     lambda s, gp=gp, i=i: s[1][i] == gp))
        pool.append((f"Boy B{bp+1} faces Girl G{gp+1}",
                     lambda s, bp=bp, gp=gp:
                         s[0].index(bp) == s[1].index(gp)))
        if i + 1 < M:
            bq, gq = boys[i + 1], girls[i + 1]
            pool.append((f"B{bp+1} sits immediately left of B{bq+1}",
                         lambda s, a=bp, b=bq:
                             s[0].index(b) == s[0].index(a) + 1))
            pool.append((f"G{gp+1} sits immediately left of G{gq+1}",
                         lambda s, a=gp, b=gq:
                             s[1].index(b) == s[1].index(a) + 1))
        if i > 0:
            bq, gq = boys[i - 1], girls[i - 1]
            pool.append((f"B{bp+1} sits immediately right of B{bq+1}",
                         lambda s, a=bp, b=bq:
                             s[0].index(b) == s[0].index(a) - 1))
            pool.append((f"G{gp+1} sits immediately right of G{gq+1}",
                         lambda s, a=gp, b=gq:
                             s[1].index(b) == s[1].index(a) - 1))
        if 0 < i < M - 1:
            blo, bhi = boys[i - 1], boys[i + 1]
            pool.append((f"B{bp+1} sits between B{blo+1} and B{bhi+1}",
                         lambda s, a=bp, x=blo, y=bhi:
                             min(s[0].index(x), s[0].index(y))
                             < s[0].index(a)
                             < max(s[0].index(x), s[0].index(y))))
    return pool


def _count_two_row(pool, M):
    count = 0
    for bp in itertools.permutations(range(M)):
        for gp in itertools.permutations(range(M)):
            state = (bp, gp)
            if all(pred(state) for _, pred in pool):
                count += 1
                if count > 1:
                    return count
    return count


def _try_two_row(M, seed):
    rng = random.Random(seed)
    boys = list(range(M))
    girls = list(range(M))
    rng.shuffle(boys)
    rng.shuffle(girls)
    pool = _two_row_pool(boys, girls, M)
    rng.shuffle(pool)
    kept = []
    for text, pred in pool:
        kept.append((text, pred))
        if _count_two_row(kept, M) == 1:
            return boys, girls, kept
    return None


def _build_two_row(p):
    M, seed = p
    result = _try_two_row(M, seed)
    if result is None:
        return None
    boys, girls, clues = result
    rng = random.Random(seed * 31 + 7)
    k = rng.randint(0, M - 1)
    answer = f"G{girls[k]+1}"
    lines = [
        f"{M} boys B1..B{M} sit in a row facing south.",
        f"{M} girls G1..G{M} sit in a row facing north, facing the boys.",
        "Clues:",
    ]
    for text, _ in clues:
        lines.append(f"  - {text}")
    lines.append(f"\nWho faces Boy B{boys[k]+1}? (e.g. G3)")
    return {
        "prompt": "\n".join(lines),
        "answer": answer.lower(),
        "hint": "Build both rows independently, then link via 'faces'.",
        "qtype": "two_row",
    }


def _circular_pool(people, N, facing):
    sign = 1 if facing == "in" else -1
    idx = {p: i for i, p in enumerate(people)}
    pool = []
    if N % 2 == 0:
        for p in range(N):
            i = idx[p]
            opp_p = people[(i + N // 2) % N]
            pool.append((f"P{p+1} sits opposite P{opp_p+1}",
                         lambda a, p=p, q=opp_p:
                             (a.index(p) + len(a) // 2) % len(a)
                             == a.index(q)))
    for p in range(N):
        for q in range(N):
            if p == q:
                continue
            i, j = idx[p], idx[q]
            for k in (1, 2):
                if i == (j + sign * k) % N:
                    pool.append((f"P{p+1} is {k} place(s) to the left of P{q+1}",
                                 lambda a, p=p, q=q, k=k, s=sign:
                                     a.index(p) == (a.index(q) + s * k) % len(a)))
                if i == (j - sign * k) % N:
                    pool.append((f"P{p+1} is {k} place(s) to the right of P{q+1}",
                                 lambda a, p=p, q=q, k=k, s=sign:
                                     a.index(p) == (a.index(q) - s * k) % len(a)))
    return pool


def _count_circular(pool, N):
    count = 0
    for perm in itertools.permutations(range(1, N)):
        arr = (0,) + perm
        if all(pred(arr) for _, pred in pool):
            count += 1
            if count > 1:
                return count
    return count


def _try_circular(N, facing, seed):
    rng = random.Random(seed)
    people = list(range(N))
    rng.shuffle(people)
    pool = _circular_pool(people, N, facing)
    rng.shuffle(pool)
    kept = []
    for text, pred in pool:
        kept.append((text, pred))
        if _count_circular(kept, N) == 1:
            return people, kept
    return None


def _build_circular(p):
    N, facing, seed = p
    result = _try_circular(N, facing, seed)
    if result is None:
        return None
    people, clues = result
    rng = random.Random(seed * 31 + 7)
    target = rng.randint(0, N - 1)
    sign = 1 if facing == "in" else -1
    idx = {p: i for i, p in enumerate(people)}
    left_i = (idx[target] + sign * 2) % N
    answer_p = people[left_i]
    face_word = "centre" if facing == "in" else "away from the centre"
    lines = [f"{N} people P1..P{N} sit around a circular table facing {face_word}.",
             "Clues:"]
    for text, _ in clues:
        lines.append(f"  - {text}")
    lines.append(f"\nWho is 2 places to the left of P{target+1}? (person number)")
    return {
        "prompt": "\n".join(lines),
        "answer": str(answer_p + 1),
        "hint": "Fix one person, place others by relative clues.",
        "qtype": "circular_inward" if facing == "in" else "circular_outward",
    }


def _enumerate_linear():
    out = []
    for N in (5, 6):
        for seed in range(60):
            if _try_linear(N, seed) is not None:
                out.append((N, seed))
    return out


def _enumerate_two_row():
    out = []
    for M in (3, 4):
        for seed in range(60):
            if _try_two_row(M, seed) is not None:
                out.append((M, seed))
    return out


def _enumerate_circular(facing):
    out = []
    for N in (5, 6):
        for seed in range(60):
            if _try_circular(N, facing, seed) is not None:
                out.append((N, facing, seed))
    return out


PARAMS = {
    "linear":           _enumerate_linear(),
    "two_row":          _enumerate_two_row(),
    "circular_inward":  _enumerate_circular("in"),
    "circular_outward": _enumerate_circular("out"),
}

BUILDERS = {
    "linear":           _build_linear,
    "two_row":          _build_two_row,
    "circular_inward":  _build_circular,
    "circular_outward": _build_circular,
}

LABELS = {
    "linear":           "Linear row (facing north)",
    "two_row":          "Two rows (boys + girls)",
    "circular_inward":  "Circular (facing centre)",
    "circular_outward": "Circular (facing away)",
}
