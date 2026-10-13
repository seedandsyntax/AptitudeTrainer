"""Blood-relations question generators.

Subtypes:
    coded_short  — 3-person chain with symbol → relation mapping
    coded_long   — 4-person chain
    simple       — classic "Introducing X, Y said …" templates
    puzzle       — multi-statement family-tree constraints + query
"""

import random
from itertools import product


# ------------------------------------------------------------------
# Family graph primitives
# ------------------------------------------------------------------
class Person:
    __slots__ = ("name", "gender", "parents", "children", "spouse")
    _next_id = 0

    def __init__(self, name, gender="?"):
        self.name = name
        self.gender = gender
        self.parents = []
        self.children = []
        self.spouse = None

    @classmethod
    def next_placeholder(cls):
        cls._next_id += 1
        return cls(f"_{cls._next_id}")


def _add_parent(parent, child):
    if parent not in child.parents:
        child.parents.append(parent)
    if child not in parent.children:
        parent.children.append(child)


def _add_sibling(a, b):
    if not a.parents and not b.parents:
        p = Person.next_placeholder()
        _add_parent(p, a)
        _add_parent(p, b)
        return
    all_parents = set(a.parents) | set(b.parents)
    if not all_parents:
        all_parents = {Person.next_placeholder()}
    for p in all_parents:
        _add_parent(p, a)
        _add_parent(p, b)


def _link(a, b, relation):
    if relation == "mother":
        a.gender = "F"
        _add_parent(a, b)
    elif relation == "father":
        a.gender = "M"
        _add_parent(a, b)
    elif relation == "sister":
        a.gender = "F"
        _add_sibling(a, b)
    elif relation == "brother":
        a.gender = "M"
        _add_sibling(a, b)
    elif relation == "son":
        a.gender = "M"
        _add_parent(b, a)
    elif relation == "daughter":
        a.gender = "F"
        _add_parent(b, a)
    elif relation == "wife":
        a.gender = "F"
        a.spouse = b
        b.spouse = a
    elif relation == "husband":
        a.gender = "M"
        a.spouse = b
        b.spouse = a


# ------------------------------------------------------------------
# Relation inference (single-hop + multi-hop graph walk)
# ------------------------------------------------------------------
def _relation(x, y):
    """Return how x is related to y (single word) or 'unknown'."""
    if y in x.children:
        return "father" if x.gender == "M" else "mother"
    if y in x.parents:
        return "son" if x.gender == "M" else "daughter"
    if x.spouse is y:
        return "husband" if x.gender == "M" else "wife"

    xp = set(x.parents)
    yp = set(y.parents)

    if xp and yp and (xp & yp):
        return "brother" if x.gender == "M" else "sister"

    # Grandparent / grandchild
    for ypar in y.parents:
        if ypar in x.children:
            return "grandfather" if x.gender == "M" else "grandmother"
    for xpar in x.parents:
        if xpar in y.children:
            return "grandson" if x.gender == "M" else "granddaughter"

    # Parent-in-law: x's child is married to y
    for xc in x.children:
        if xc.spouse is y:
            return "father-in-law" if x.gender == "M" else "mother-in-law"

    # Child-in-law: y's child is married to x
    for yc in y.children:
        if yc.spouse is x:
            return "son-in-law" if x.gender == "M" else "daughter-in-law"

    # Aunt / Uncle
    for ypar in y.parents:
        if ypar.parents and (xp & set(ypar.parents)) and x is not ypar:
            return "uncle" if x.gender == "M" else "aunt"

    # Niece / Nephew
    y_siblings = set()
    for ypar in y.parents:
        for sib in ypar.children:
            if sib is y:
                continue
            if yp and (set(sib.parents) & yp):
                y_siblings.add(sib)
    for sib in y_siblings:
        if sib in x.parents:
            return "nephew" if x.gender == "M" else "niece"

    # Cousins
    for xpar in x.parents:
        for ypar in y.parents:
            if xpar is ypar:
                continue
            if xpar.parents and ypar.parents and (
                set(xpar.parents) & set(ypar.parents)
            ):
                return "cousin"

    return "unknown"


# ------------------------------------------------------------------
# Coded chains — pre-enumerate
# ------------------------------------------------------------------
SYMBOLS = ["+", "-", "*", "/", "@", "#", "$", "%"]
RELATIONS = [
    "mother", "father", "sister", "brother",
    "son", "daughter", "wife", "husband",
]
SYMBOL_TO_REL = dict(zip(SYMBOLS, RELATIONS))
NAMES = ["A", "B", "C", "D"]


def _eval_chain(symbols):
    people = {n: Person(n) for n in NAMES[:len(symbols) + 1]}
    for i, sym in enumerate(symbols):
        _link(people[NAMES[i]], people[NAMES[i + 1]], SYMBOL_TO_REL[sym])
    first = people[NAMES[0]]
    last = people[NAMES[len(symbols)]]
    ans = _relation(first, last)
    if ans == "unknown":
        return None
    chain = " ".join(
        NAMES[i] + " " + symbols[i] + " " for i in range(len(symbols))
    ) + NAMES[len(symbols)]
    return chain, ans


def _enumerate_chains(length):
    out = []
    for symbols in product(SYMBOLS, repeat=length):
        result = _eval_chain(list(symbols))
        if result is not None:
            out.append(result)
    return out


_CODED_SHORT = _enumerate_chains(2)
_CODED_LONG = _enumerate_chains(3)


def _mapping_line():
    return ", ".join(f"{s}={r}" for s, r in SYMBOL_TO_REL.items())


def _build_coded(p):
    chain, answer = p
    return {
        "prompt": (
            f"Given: {_mapping_line()}\n"
            f"Chain: {chain}\n"
            f"How is {chain[0]} related to {chain[-1]}?"
        ),
        "answer": answer,
        "hint": "Apply each symbol as a relation, then trace the graph.",
        "qtype": "coded",
    }


# ------------------------------------------------------------------
# Simple templates
# ------------------------------------------------------------------
_SIMPLE_TEMPLATES = [
    (
        "Introducing a man {m}, {w} said: Your brother's father is the only "
        "son of my grandfather. How is {w} related to {m}?",
        "sister",
    ),
    (
        "{m} introduces {w} as the daughter of the only son of my father's wife. "
        "How is {w} related to {m}?",
        "daughter",
    ),
    (
        "Pointing to a photograph, {m} said: I have no brother or sister, "
        "but that person's father is my father's son. How is the person in "
        "the photograph related to {m}?",
        "son",
    ),
    (
        "{m} said to {w}: Your mother is the only daughter of my mother. "
        "How is {w} related to {m}?",
        "daughter",
    ),
    (
        "Introducing {w}, {m} said: She is the daughter of my grandfather's "
        "only son. How is {w} related to {m}?",
        "sister",
    ),
]

_MALE_NAMES = ["Ramesh", "Suresh", "Mahesh", "Rajesh", "Amit", "Vijay", "Karan"]
_FEMALE_NAMES = ["Sudha", "Priya", "Anita", "Kavita", "Sunita", "Meena", "Rita"]


_SIMPLE_PARAMS = [
    (template, answer, m, w)
    for template, answer in _SIMPLE_TEMPLATES
    for m in _MALE_NAMES
    for w in _FEMALE_NAMES
]


def _build_simple(p):
    template, answer, m, w = p
    return {
        "prompt": template.format(m=m, w=w),
        "answer": answer,
        "hint": "Draw a small family tree from the statement.",
        "qtype": "simple",
    }


# ------------------------------------------------------------------
# Puzzle-based (generate a tree, narrate it, query it)
# ------------------------------------------------------------------
def _build_family_puzzle(p):
    """Build a fixed-shape 3-generation tree, narrate it, query it.

    Tree shape (7 members):
        H (M) ─ W (F)              grandparents
             │
        P (M/F) ─ SP (F/M)         parent + spouse
             │
        K1, K2, K3                 three children
    """
    seed = p[0]
    rng = random.Random(seed)

    names = ["A", "B", "C", "D", "E", "F", "G"]
    rng.shuffle(names)
    H, W, P, SP, K1, K2, K3 = names

    P_gender = rng.choice("MF")
    SP_gender = "F" if P_gender == "M" else "M"

    genders = {
        H: "M", W: "F",
        P: P_gender, SP: SP_gender,
        K1: rng.choice("MF"),
        K2: rng.choice("MF"),
        K3: rng.choice("MF"),
    }

    people = {n: Person(n, genders[n]) for n in names}

    people[H].spouse = people[W]
    people[W].spouse = people[H]
    _add_parent(people[H], people[P])
    _add_parent(people[W], people[P])
    people[P].spouse = people[SP]
    people[SP].spouse = people[P]
    for kid in (K1, K2, K3):
        _add_parent(people[P], people[kid])
        _add_parent(people[SP], people[kid])

    # ---- base facts -------------------------------------------------
    spouse_word_sp = "wife" if SP_gender == "F" else "husband"
    parent_word_p = "son" if P_gender == "M" else "daughter"

    facts = [
        f"{H} is the husband of {W}.",
        f"{SP} is the {spouse_word_sp} of {P}.",
        f"{P} is the {parent_word_p} of {H} and {W}.",
    ]
    for kid in (K1, K2, K3):
        kid_word = "son" if genders[kid] == "M" else "daughter"
        facts.append(f"{kid} is the {kid_word} of {P}.")

    # ---- query pool -------------------------------------------------
    queries = []
    for kid in (K1, K2, K3):
        queries.append((H, kid, "grandfather"))
        queries.append((W, kid, "grandmother"))
        queries.append(
            (SP, kid, "mother" if SP_gender == "F" else "father")
        )
        queries.append(
            (P, kid, "father" if P_gender == "M" else "mother")
        )
    for a, b in ((K1, K2), (K2, K3), (K1, K3)):
        queries.append((a, b, "brother" if genders[a] == "M" else "sister"))
    queries.append((H, SP, "father-in-law"))
    queries.append((W, SP, "mother-in-law"))
    queries.append(
        (SP, H, "daughter-in-law" if SP_gender == "F" else "son-in-law")
    )

    rng.shuffle(queries)
    for x, y, expected in queries:
        if _relation(people[x], people[y]) == expected:
            break
    else:
        # fallback — should never trigger
        x, y, expected = H, K1, "grandfather"

    prompt = "\n".join(facts) + f"\n\nHow is {x} related to {y}?"

    return {
        "prompt": prompt,
        "answer": expected,
        "hint": "Draw the tree from the statements, then infer the relation.",
        "qtype": "puzzle",
    }


_PUZZLE_SEEDS = [(i,) for i in range(100)]


# ------------------------------------------------------------------
# Public API
# ------------------------------------------------------------------
PARAMS = {
    "coded_short": _CODED_SHORT,
    "coded_long":  _CODED_LONG,
    "simple":      _SIMPLE_PARAMS,
    "puzzle":      _PUZZLE_SEEDS,
}

BUILDERS = {
    "coded_short": _build_coded,
    "coded_long":  _build_coded,
    "simple":      _build_simple,
    "puzzle":      _build_family_puzzle,
}

LABELS = {
    "coded_short": "Coded relations (3 people)",
    "coded_long":  "Coded relations (4 people)",
    "simple":      "Simple statements",
    "puzzle":      "Puzzle (multi-statement tree)",
}
