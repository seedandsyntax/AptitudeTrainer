"""Alphabet Analogy / Classification / Series generators.

Subtypes:
    letter_pairs  — count pairs in a word with matching gap in word and alphabet
    alpha_series  — find the missing term of a 3-letter series
"""


WORDS = [
    "EXPLOSION", "CREATIVE", "AEROPLANE", "GARDEN", "SILENT",
    "ROCKET", "PLANET", "CAMERA", "WINDOW", "ORANGE",
    "YELLOW", "PENCIL", "SYSTEM", "NUMBER", "LAPTOP",
    "FRIEND", "MOTHER", "FATHER", "SCHOOL", "STUDENT",
]


def _count_pairs(word):
    n = len(word)
    count = 0
    for i in range(n):
        for j in range(i + 1, n):
            if abs(ord(word[i]) - ord(word[j])) == j - i:
                count += 1
    return count


def _build_letter_pairs(p):
    word = p[0]
    return {
        "prompt": (
            f"How many pairs of letters in '{word}' have as many letters "
            f"between them (in the word) as in the English alphabet?"
        ),
        "answer": str(_count_pairs(word)),
        "hint": "For each pair (i, j) with i < j, check "
                "|alpha(word[i]) − alpha(word[j])| == j − i.",
        "qtype": "letter_pairs",
    }


def _series_term(a_list, d_list, i):
    letters = []
    for a, d in zip(a_list, d_list):
        x = (a + i * d - 1) % 26 + 1
        letters.append(chr(x + 64))
    return "".join(letters)


def _build_alpha_series(p):
    a_list, d_list, missing = p
    terms = [_series_term(a_list, d_list, i) for i in range(4)]
    answer = terms[missing]
    shown = list(terms)
    shown[missing] = "?"
    return {
        "prompt": f"Find the missing term: {', '.join(shown)}",
        "answer": answer.lower(),
        "hint": "Each letter position advances by a fixed step across terms.",
        "qtype": "alpha_series",
    }


_LETTER_PAIRS_PARAMS = [(w,) for w in WORDS if _count_pairs(w) >= 2]

_ALPHA_SERIES_PARAMS = []
for a1 in range(1, 27, 4):
    for a2 in range(1, 27, 7):
        for a3 in range(1, 27, 11):
            for d1 in (1, 2):
                for d2 in (2, 3):
                    for d3 in (3, 4):
                        for missing in (1, 2, 3):
                            _ALPHA_SERIES_PARAMS.append(
                                ((a1, a2, a3), (d1, d2, d3), missing)
                            )
_ALPHA_SERIES_PARAMS = _ALPHA_SERIES_PARAMS[:500]

PARAMS = {
    "letter_pairs": _LETTER_PAIRS_PARAMS,
    "alpha_series": _ALPHA_SERIES_PARAMS,
}

BUILDERS = {
    "letter_pairs": _build_letter_pairs,
    "alpha_series": _build_alpha_series,
}

LABELS = {
    "letter_pairs": "Letter pairs (same gap)",
    "alpha_series": "3-letter series missing term",
}
