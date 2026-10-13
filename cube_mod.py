"""Cube / Cuboid question generators.

Families (cube of size X cut into 1cm small cubes):
    cube_total         — total small cubes
    cube_three_face    — small cubes with 3 faces coloured
    cube_two_face      — small cubes with 2 faces coloured
    cube_one_face      — small cubes with 1 face coloured
    cube_zero_face     — small cubes with 0 faces coloured
    cube_hollow        — small cubes in a hollow shell of thickness 1

Families (cuboid L×B×H cut into 1cm small cubes):
    cuboid_total, cuboid_two_face, cuboid_one_face,
    cuboid_zero_face, cuboid_hollow

Special:
    unpainted_faces    — hollow cube, one outer face painted; count
                         small-cube faces remaining unpainted
"""

import random


# ------------------------------------------------------------------
# Builders
# ------------------------------------------------------------------
def _build_cube_total(p):
    x = p[0]
    return {
        "prompt": f"A {x}cm cube is cut into 1cm small cubes. Total cubes?",
        "answer": str(x ** 3),
        "hint": "Total = X³",
        "qtype": "cube_total",
    }


def _build_cube_three_face(p):
    x = p[0]
    return {
        "prompt": (
            f"A {x}cm cube is cut into 1cm cubes. How many small cubes "
            f"have exactly 3 faces coloured?"
        ),
        "answer": "8",
        "hint": "3 faces meet only at the 8 corners of a cube.",
        "qtype": "cube_three_face",
    }


def _build_cube_two_face(p):
    x = p[0]
    ans = 12 * (x - 2)
    return {
        "prompt": (
            f"A {x}cm cube is cut into 1cm cubes. How many small cubes "
            f"have exactly 2 faces coloured?"
        ),
        "answer": str(ans),
        "hint": "2 faces meet on edges, minus corners: 12 × (X−2)",
        "qtype": "cube_two_face",
    }


def _build_cube_one_face(p):
    x = p[0]
    ans = 6 * (x - 2) ** 2
    return {
        "prompt": (
            f"A {x}cm cube is cut into 1cm cubes. How many small cubes "
            f"have exactly 1 face coloured?"
        ),
        "answer": str(ans),
        "hint": "1 face on face interior: 6 × (X−2)²",
        "qtype": "cube_one_face",
    }


def _build_cube_zero_face(p):
    x = p[0]
    ans = (x - 2) ** 3
    return {
        "prompt": (
            f"A {x}cm cube is cut into 1cm cubes. How many small cubes "
            f"have 0 faces coloured?"
        ),
        "answer": str(ans),
        "hint": "Interior cubes: (X−2)³",
        "qtype": "cube_zero_face",
    }


def _build_cube_hollow(p):
    x = p[0]
    ans = x ** 3 - (x - 2) ** 3
    return {
        "prompt": (
            f"A hollow {x}cm cube of thickness 1cm is made of 1cm cubes. "
            f"How many small cubes are used?"
        ),
        "answer": str(ans),
        "hint": "Hollow = X³ − (X−2)³",
        "qtype": "cube_hollow",
    }


def _build_cuboid_total(p):
    l, b, h = p
    return {
        "prompt": (
            f"A {l}×{b}×{h}cm cuboid is cut into 1cm cubes. "
            f"Total small cubes?"
        ),
        "answer": str(l * b * h),
        "hint": "Total = L × B × H",
        "qtype": "cuboid_total",
    }


def _build_cuboid_two_face(p):
    l, b, h = p
    ans = 4 * (l - 2) + 4 * (b - 2) + 4 * (h - 2)
    return {
        "prompt": (
            f"A {l}×{b}×{h}cm cuboid is cut into 1cm cubes. "
            f"How many small cubes have exactly 2 faces coloured?"
        ),
        "answer": str(ans),
        "hint": "2 faces on edges: 4(L−2) + 4(B−2) + 4(H−2)",
        "qtype": "cuboid_two_face",
    }


def _build_cuboid_one_face(p):
    l, b, h = p
    ans = 2 * (l - 2) * (b - 2) + 2 * (b - 2) * (h - 2) + 2 * (h - 2) * (l - 2)
    return {
        "prompt": (
            f"A {l}×{b}×{h}cm cuboid is cut into 1cm cubes. "
            f"How many small cubes have exactly 1 face coloured?"
        ),
        "answer": str(ans),
        "hint": "1 face on face interiors: 2(L−2)(B−2) + 2(B−2)(H−2) + 2(H−2)(L−2)",
        "qtype": "cuboid_one_face",
    }


def _build_cuboid_zero_face(p):
    l, b, h = p
    ans = (l - 2) * (b - 2) * (h - 2)
    return {
        "prompt": (
            f"A {l}×{b}×{h}cm cuboid is cut into 1cm cubes. "
            f"How many small cubes have 0 faces coloured?"
        ),
        "answer": str(ans),
        "hint": "Interior: (L−2)(B−2)(H−2)",
        "qtype": "cuboid_zero_face",
    }


def _build_cuboid_hollow(p):
    l, b, h = p
    ans = l * b * h - (l - 2) * (b - 2) * (h - 2)
    return {
        "prompt": (
            f"A hollow {l}×{b}×{h}cm cuboid of thickness 1cm is made of "
            f"1cm cubes. How many small cubes are used?"
        ),
        "answer": str(ans),
        "hint": "Hollow = LBH − (L−2)(B−2)(H−2)",
        "qtype": "cuboid_hollow",
    }


def _build_unpainted_faces(p):
    x = p[0]
    total = x ** 3 - (x - 2) ** 3
    painted = x ** 2
    ans = 5 * painted + 6 * (total - painted)
    return {
        "prompt": (
            f"A hollow {x}cm cube of thickness 1cm is made of 1cm cubes. "
            f"One outer face is fully painted. How many faces of the "
            f"small cubes remain unpainted?"
        ),
        "answer": str(ans),
        "hint": (
            f"Total cubes = X³ − (X−2)³. Painted face exposes X² cubes "
            f"(each with 1 painted face). Unpainted faces = 5·X² + 6·(rest)."
        ),
        "qtype": "unpainted_faces",
    }


# ------------------------------------------------------------------
# Parameter enumeration
# ------------------------------------------------------------------
_CUBE_SMALL = [(x,) for x in range(3, 11)]           # 3..10
_CUBE_LARGE = [(x,) for x in range(4, 11)]           # 4..10 (X-2 ≥ 2)

_CUBOID_ALL = [
    (l, b, h)
    for l in range(3, 9)
    for b in range(3, 9)
    for h in range(3, 9)
    if not (l == b == h)
]
_CUBOID_LARGE = [
    (l, b, h)
    for l in range(4, 9)
    for b in range(4, 9)
    for h in range(4, 9)
    if not (l == b == h)
]


PARAMS = {
    "cube_total":        _CUBE_SMALL,
    "cube_three_face":   _CUBE_SMALL,
    "cube_two_face":     _CUBE_LARGE,
    "cube_one_face":     _CUBE_LARGE,
    "cube_zero_face":    _CUBE_LARGE,
    "cube_hollow":       _CUBE_LARGE,
    "cuboid_total":      _CUBOID_ALL,
    "cuboid_two_face":   _CUBOID_LARGE,
    "cuboid_one_face":   _CUBOID_LARGE,
    "cuboid_zero_face":  _CUBOID_LARGE,
    "cuboid_hollow":     _CUBOID_LARGE,
    "unpainted_faces":   _CUBE_SMALL,
}

BUILDERS = {
    "cube_total":        _build_cube_total,
    "cube_three_face":   _build_cube_three_face,
    "cube_two_face":     _build_cube_two_face,
    "cube_one_face":     _build_cube_one_face,
    "cube_zero_face":    _build_cube_zero_face,
    "cube_hollow":       _build_cube_hollow,
    "cuboid_total":      _build_cuboid_total,
    "cuboid_two_face":   _build_cuboid_two_face,
    "cuboid_one_face":   _build_cuboid_one_face,
    "cuboid_zero_face":  _build_cuboid_zero_face,
    "cuboid_hollow":     _build_cuboid_hollow,
    "unpainted_faces":   _build_unpainted_faces,
}

LABELS = {
    "cube_total":        "Cube — total small cubes",
    "cube_three_face":   "Cube — 3 faces coloured",
    "cube_two_face":     "Cube — 2 faces coloured",
    "cube_one_face":     "Cube — 1 face coloured",
    "cube_zero_face":    "Cube — 0 faces coloured",
    "cube_hollow":       "Cube — hollow (thickness 1)",
    "cuboid_total":      "Cuboid — total small cubes",
    "cuboid_two_face":   "Cuboid — 2 faces coloured",
    "cuboid_one_face":   "Cuboid — 1 face coloured",
    "cuboid_zero_face":  "Cuboid — 0 faces coloured",
    "cuboid_hollow":     "Cuboid — hollow (thickness 1)",
    "unpainted_faces":   "Hollow cube — unpainted faces",
}
