"""
Training core: generation, pickers, registry, profiles.
"""

import json
import random
from pathlib import Path
from datetime import datetime
from itertools import combinations

import code_decode_mod
import number_series_mod
import clock_mod
import cube_mod
import blood_relations_mod
import direction_mod
import hcf_lcm_mod
import calendar_mod
import percentage_mod
import average_mod
import number_system_mod
import venn_mod
import syllogism_mod
import sitting_arrangement_mod
import alphabet_series_mod


ALPHABETS = "abcdefghijklmnopqrstuvwxyz"
LHS_TABLE = {ch: i + 1 for i, ch in enumerate(ALPHABETS)}
RHS_TABLE = {ch: 26 - i for i, ch in enumerate(ALPHABETS)}

DATA_DIR = Path("data")
PROFILES_DIR = DATA_DIR / "profiles"
QUIZ_DATA_DIR = DATA_DIR / "quiz_data"


def ensure_dirs():
    PROFILES_DIR.mkdir(parents=True, exist_ok=True)
    QUIZ_DATA_DIR.mkdir(parents=True, exist_ok=True)


class Question:
    def __init__(self, prompt, answer, hint="", qtype="", tolerance=None):
        self.prompt = prompt
        self.answer = str(answer).strip().lower()
        self.hint = hint
        self.qtype = qtype
        self.tolerance = tolerance
        self.user_answer = None
        self.is_correct = False
        self.time_sec = 0.0

    def check(self, user_input):
        self.user_answer = str(user_input).strip().lower()
        if self.tolerance is not None:
            try:
                self.is_correct = (
                    abs(float(self.user_answer) - float(self.answer))
                    <= self.tolerance
                )
            except ValueError:
                self.is_correct = False
        else:
            self.is_correct = self.user_answer == self.answer
        return self.is_correct

    def to_dict(self):
        return {
            "prompt": self.prompt,
            "qtype": self.qtype,
            "user_answer": self.user_answer,
            "correct": self.is_correct,
            "time_sec": round(self.time_sec, 3),
        }


class CooldownPicker:
    def __init__(self, pool, cooldown=3):
        self.pool = list(pool)
        self.cooldown = cooldown
        self.queue = []

    def pick(self):
        ghost = [x for x in self.pool if x not in self.queue]
        choice = random.choice(ghost)
        self.queue.append(choice)
        if len(self.queue) > self.cooldown:
            self.queue.pop(0)
        return choice


class Bag:
    def __init__(self, items):
        self.items = list(items)
        self._deck = []

    def pick(self):
        if not self._deck:
            self._deck = self.items[:]
            random.shuffle(self._deck)
        return self._deck.pop()


def q_lhs_pos(letter):
    return Question(
        prompt=f"LHS position of '{letter.upper()}'?",
        answer=str(LHS_TABLE[letter]),
        hint="A=1, B=2, ... Z=26",
        qtype="lhs_pos",
    )


def q_rhs_pos(letter):
    return Question(
        prompt=f"RHS position of '{letter.upper()}'?",
        answer=str(RHS_TABLE[letter]),
        hint="RHS = 27 - LHS",
        qtype="rhs_pos",
    )


def q_pos_to_letter(letter):
    pos = LHS_TABLE[letter]
    return Question(
        prompt=f"Letter at LHS position {pos}?",
        answer=letter,
        hint="Count forward from A=1",
        qtype="pos_letter",
    )


ALPHABET_GENERATORS = {
    "lhs_pos":    q_lhs_pos,
    "rhs_pos":    q_rhs_pos,
    "pos_letter": q_pos_to_letter,
}

ALPHABET_ATOMS = {
    "lhs_pos":    "LHS",
    "rhs_pos":    "RHS",
    "pos_letter": "Positional",
}


def _all_subsets(atoms):
    keys = list(atoms)
    modes = []
    for r in range(1, len(keys) + 1):
        for combo in combinations(keys, r):
            label = " + ".join(atoms[k] for k in combo)
            modes.append((label, list(combo)))
    return modes


ALPHABET_MODES = _all_subsets(ALPHABET_ATOMS)


def all_types_registry():
    reg = {}
    for k in ALPHABET_GENERATORS:
        reg[f"alphabet:{k}"] = ("alphabet", k, f"[A] {ALPHABET_ATOMS[k]}")
    for k in code_decode_mod.LABELS:
        reg[f"coding:{k}"] = ("coding", k, f"[C] {code_decode_mod.LABELS[k]}")
    for k in number_series_mod.BUILDERS:
        reg[f"series:{k}"] = ("series", k, f"[S] {number_series_mod.LABELS[k]}")
    for k in clock_mod.BUILDERS:
        reg[f"clock:{k}"] = ("clock", k, f"[K] {clock_mod.LABELS[k]}")
    for k in cube_mod.BUILDERS:
        reg[f"cube:{k}"] = ("cube", k, f"[U] {cube_mod.LABELS[k]}")
    for k in blood_relations_mod.BUILDERS:
        reg[f"blood:{k}"] = ("blood", k, f"[B] {blood_relations_mod.LABELS[k]}")
    for k in direction_mod.BUILDERS:
        reg[f"direction:{k}"] = ("direction", k, f"[D] {direction_mod.LABELS[k]}")
    for k in hcf_lcm_mod.BUILDERS:
        reg[f"hcf_lcm:{k}"] = ("hcf_lcm", k, f"[H] {hcf_lcm_mod.LABELS[k]}")
    for k in calendar_mod.BUILDERS:
        reg[f"calendar:{k}"] = ("calendar", k, f"[Y] {calendar_mod.LABELS[k]}")
    for k in percentage_mod.BUILDERS:
        reg[f"percentage:{k}"] = ("percentage", k, f"[%] {percentage_mod.LABELS[k]}")
    for k in average_mod.BUILDERS:
        reg[f"average:{k}"] = ("average", k, f"[V] {average_mod.LABELS[k]}")
    for k in number_system_mod.BUILDERS:
        reg[f"number_system:{k}"] = ("number_system", k, f"[N] {number_system_mod.LABELS[k]}")
    for k in venn_mod.BUILDERS:
        reg[f"venn:{k}"] = ("venn", k, f"[E] {venn_mod.LABELS[k]}")
    for k in syllogism_mod.BUILDERS:
        reg[f"syllogism:{k}"] = ("syllogism", k, f"[L] {syllogism_mod.LABELS[k]}")
    for k in sitting_arrangement_mod.BUILDERS:
        reg[f"sitting:{k}"] = ("sitting", k, f"[T] {sitting_arrangement_mod.LABELS[k]}")
    for k in alphabet_series_mod.BUILDERS:
        reg[f"alpha_series:{k}"] = ("alpha_series", k, f"[Z] {alphabet_series_mod.LABELS[k]}")
    return reg


def generate_alphabet_questions(types, count, cooldown=5):
    picker = CooldownPicker(ALPHABETS, cooldown=cooldown)
    return [
        ALPHABET_GENERATORS[random.choice(types)](picker.pick())
        for _ in range(count)
    ]


def generate_coding_questions(types, count, cooldown=5):
    word_types = [t for t in types if t in code_decode_mod.WORD_BASED]
    non_word_types = [t for t in types if t not in code_decode_mod.WORD_BASED]

    picker = None
    if word_types:
        picker = CooldownPicker(code_decode_mod.WORDS, cooldown=cooldown)

    out = []
    for _ in range(count):
        if word_types and non_word_types:
            t = random.choice(types)
        elif word_types:
            t = random.choice(word_types)
        else:
            t = random.choice(non_word_types)

        if t in code_decode_mod.WORD_BASED:
            word = picker.pick()
            data = code_decode_mod.GENERATORS[t](word)
        else:
            param = random.choice(code_decode_mod.PARAMS[t])
            data = code_decode_mod.BUILDERS[t](param)
        out.append(Question(**data))
    return out


def _generate_parametrized(mod, types, count, cooldown=2, strip_difficulty=True):
    type_picker = (
        CooldownPicker(types, cooldown=min(cooldown, len(types) - 1))
        if len(types) > 1 else None
    )
    bags = {t: Bag(mod.PARAMS[t]) for t in types}
    out = []
    for _ in range(count):
        qtype = types[0] if type_picker is None else type_picker.pick()
        param = bags[qtype].pick()
        data = mod.BUILDERS[qtype](param)
        if strip_difficulty:
            data.pop("difficulty", None)
        out.append(Question(**data))
    return out


def generate_number_series_questions(types, count):
    return _generate_parametrized(number_series_mod, types, count)


def generate_clock_questions(types, count):
    return _generate_parametrized(clock_mod, types, count, strip_difficulty=False)


def generate_cube_questions(types, count):
    return _generate_parametrized(cube_mod, types, count, strip_difficulty=False)


def generate_blood_questions(types, count):
    return _generate_parametrized(
        blood_relations_mod, types, count, strip_difficulty=False
    )


def generate_direction_questions(types, count):
    return _generate_parametrized(
        direction_mod, types, count, strip_difficulty=False
    )


def generate_hcf_lcm_questions(types, count):
    return _generate_parametrized(
        hcf_lcm_mod, types, count, strip_difficulty=False
    )


def generate_calendar_questions(types, count):
    return _generate_parametrized(
        calendar_mod, types, count, strip_difficulty=False
    )


def generate_percentage_questions(types, count):
    return _generate_parametrized(
        percentage_mod, types, count, strip_difficulty=False
    )


def generate_average_questions(types, count):
    return _generate_parametrized(
        average_mod, types, count, strip_difficulty=False
    )


def generate_number_system_questions(types, count):
    return _generate_parametrized(
        number_system_mod, types, count, strip_difficulty=False
    )


def generate_venn_questions(types, count):
    return _generate_parametrized(
        venn_mod, types, count, strip_difficulty=False
    )


def generate_syllogism_questions(types, count):
    return _generate_parametrized(
        syllogism_mod, types, count, strip_difficulty=False
    )


def generate_sitting_questions(types, count):
    return _generate_parametrized(
        sitting_arrangement_mod, types, count, strip_difficulty=False
    )


def generate_alphabet_series_questions(types, count):
    return _generate_parametrized(
        alphabet_series_mod, types, count, strip_difficulty=False
    )


def generate_mixed_questions(fq_keys, count):
    type_picker = CooldownPicker(fq_keys, cooldown=min(3, len(fq_keys) - 1))
    letter_picker = CooldownPicker(ALPHABETS, cooldown=5)
    word_picker = CooldownPicker(code_decode_mod.WORDS, cooldown=5)
    bags = {}
    mod_for = {
        "series":       number_series_mod,
        "clock":        clock_mod,
        "cube":         cube_mod,
        "blood":        blood_relations_mod,
        "direction":    direction_mod,
        "hcf_lcm":      hcf_lcm_mod,
        "calendar":     calendar_mod,
        "percentage":   percentage_mod,
        "average":      average_mod,
        "number_system": number_system_mod,
        "venn":         venn_mod,
        "syllogism":    syllogism_mod,
        "sitting":      sitting_arrangement_mod,
        "alpha_series": alphabet_series_mod,
    }

    out = []
    for _ in range(count):
        fq = type_picker.pick()
        family, key = fq.split(":", 1)

        if family == "alphabet":
            out.append(ALPHABET_GENERATORS[key](letter_picker.pick()))
        elif family == "coding":
            if key in code_decode_mod.WORD_BASED:
                word = word_picker.pick()
                data = code_decode_mod.GENERATORS[key](word)
            else:
                param = random.choice(code_decode_mod.PARAMS[key])
                data = code_decode_mod.BUILDERS[key](param)
            out.append(Question(**data))
        else:
            mod = mod_for[family]
            tag = f"{family}:{key}"
            if tag not in bags:
                bags[tag] = Bag(mod.PARAMS[key])
            param = bags[tag].pick()
            data = mod.BUILDERS[key](param)
            data.pop("difficulty", None)
            out.append(Question(**data))
    return out


class Profile:
    def __init__(self, username):
        self.username = username
        self.dir = PROFILES_DIR / username
        self.dir.mkdir(parents=True, exist_ok=True)
        self.meta_file = self.dir / "meta.json"
        self.quiz_file = self.dir / "quiz.json"
        self.meta = self._load(self.meta_file, {"sessions": []})
        self.quiz = self._load(self.quiz_file, {"sessions": []})

    @staticmethod
    def _load(path, default):
        if path.exists():
            try:
                with open(path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except (json.JSONDecodeError, OSError):
                return default
        return default

    def save(self):
        with open(self.meta_file, "w", encoding="utf-8") as f:
            json.dump(self.meta, f, indent=2)
        with open(self.quiz_file, "w", encoding="utf-8") as f:
            json.dump(self.quiz, f, indent=2)

    def record_session(self, kind, label, questions, total_time):
        n = len(questions) or 1
        session = {
            "timestamp": datetime.now().isoformat(timespec="seconds"),
            "label": label,
            "question_count": len(questions),
            "correct": sum(1 for q in questions if q.is_correct),
            "total_time_sec": round(total_time, 3),
            "avg_time_sec": round(total_time / n, 3),
            "per_question": [q.to_dict() for q in questions],
        }
        bucket = self.meta if kind == "meta" else self.quiz
        bucket["sessions"].append(session)
        self.save()
        return session

    def summary_lines(self):
        lines = [f"Profile: {self.username}"]
        for kind, bucket in (("Meta", self.meta), ("Quiz", self.quiz)):
            sessions = bucket["sessions"]
            lines.append(f"  {kind} sessions: {len(sessions)}")
            if not sessions:
                continue
            q_total = sum(s["question_count"] for s in sessions)
            c_total = sum(s["correct"] for s in sessions)
            t_total = sum(s["total_time_sec"] for s in sessions)
            avg_t = t_total / q_total if q_total else 0
            pct = c_total / q_total * 100 if q_total else 0
            lines.append(
                f"    Q={q_total}  correct={c_total} ({pct:.1f}%)  "
                f"total={t_total:.1f}s  avg={avg_t:.2f}s/q"
            )
        return lines

    def last_session(self, kind):
        bucket = self.meta if kind == "meta" else self.quiz
        return bucket["sessions"][-1] if bucket["sessions"] else None
