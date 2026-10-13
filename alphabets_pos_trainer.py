"""
CLI Coding-Decoding Trainer
- Meta drills: alphabet position training (7 modes)
- Quiz: JSON-loaded question banks
- Time-tracked, profile-persisted.
"""

import json
import random
import time
from pathlib import Path
from datetime import datetime


ALPHABETS = "abcdefghijklmnopqrstuvwxyz"
LHS_TABLE = {ch: i + 1 for i, ch in enumerate(ALPHABETS)}
RHS_TABLE = {ch: 26 - i for i, ch in enumerate(ALPHABETS)}


# ------------------------------------------------------------------
# Paths
# ------------------------------------------------------------------
DATA_DIR = Path("data")
PROFILES_DIR = DATA_DIR / "profiles"
QUIZ_DATA_DIR = DATA_DIR / "quiz_data"


def ensure_dirs():
    PROFILES_DIR.mkdir(parents=True, exist_ok=True)
    QUIZ_DATA_DIR.mkdir(parents=True, exist_ok=True)


# ------------------------------------------------------------------
# Colors
# ------------------------------------------------------------------
class C:
    RESET = "\033[0m"
    BOLD = "\033[1m"
    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    CYAN = "\033[96m"
    GREY = "\033[90m"


def clr(t, c):
    return f"{c}{t}{C.RESET}"


# ------------------------------------------------------------------
# Question
# ------------------------------------------------------------------
class Question:
    def __init__(self, prompt, answer, hint="", qtype=""):
        self.prompt = prompt
        self.answer = str(answer).strip().lower()
        self.hint = hint
        self.qtype = qtype
        self.user_answer = None
        self.is_correct = False
        self.time_sec = 0.0

    def check(self, user_input):
        self.user_answer = str(user_input).strip().lower()
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


# ------------------------------------------------------------------
# Cooldown picker
# ------------------------------------------------------------------
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


# ------------------------------------------------------------------
# Meta generators
# ------------------------------------------------------------------
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


GENERATORS = {
    "lhs_pos": q_lhs_pos,
    "rhs_pos": q_rhs_pos,
    "pos_letter": q_pos_to_letter,
}


META_MODES = {
    "1": ("LHS only",                 ["lhs_pos"]),
    "2": ("RHS only",                 ["rhs_pos"]),
    "3": ("Positional only",          ["pos_letter"]),
    "4": ("LHS + RHS",                ["lhs_pos", "rhs_pos"]),
    "5": ("LHS + Positional",         ["lhs_pos", "pos_letter"]),
    "6": ("RHS + Positional",         ["rhs_pos", "pos_letter"]),
    "7": ("LHS + RHS + Positional",   ["lhs_pos", "rhs_pos", "pos_letter"]),
}


def generate_meta_questions(types, count, cooldown=3):
    picker = CooldownPicker(ALPHABETS, cooldown=cooldown)
    return [
        GENERATORS[random.choice(types)](picker.pick())
        for _ in range(count)
    ]


# ------------------------------------------------------------------
# Profile
# ------------------------------------------------------------------
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

    def summary(self):
        print(clr(f"\nProfile: {self.username}", C.BOLD))

        for kind, bucket in (("Meta", self.meta), ("Quiz", self.quiz)):
            sessions = bucket["sessions"]
            print(f"  {kind} sessions: {len(sessions)}")
            if not sessions:
                continue
            q_total = sum(s["question_count"] for s in sessions)
            c_total = sum(s["correct"] for s in sessions)
            t_total = sum(s["total_time_sec"] for s in sessions)
            avg_t = t_total / q_total if q_total else 0
            pct = c_total / q_total * 100 if q_total else 0
            print(
                f"    Q={q_total}  correct={c_total} ({pct:.1f}%)  "
                f"total={t_total:.1f}s  avg={avg_t:.2f}s/q"
            )

    def last_session(self, kind):
        bucket = self.meta if kind == "meta" else self.quiz
        return bucket["sessions"][-1] if bucket["sessions"] else None


# ------------------------------------------------------------------
# UI
# ------------------------------------------------------------------
class CLIUserInterface:
    def __init__(self, username="default"):
        self.profile = Profile(username)
        self.questions = []

    def box(self, text, width=60):
        top = "┌" + "─" * (width - 2) + "┐"
        bot = "└" + "─" * (width - 2) + "┘"
        mid = "│" + text.center(width - 2) + "│"
        return f"{top}\n{mid}\n{bot}"

    def _run_questions(self, questions, label, kind):
        if not questions:
            print(clr("No questions.", C.YELLOW))
            return

        if kind == "quiz":
            random.shuffle(questions)

        n = len(questions)
        print(
            f"\n{clr('Session:', C.CYAN)} {label}  "
            f"| {clr(f'{n} questions', C.GREY)}"
        )
        input(clr("Press Enter to start… ", C.YELLOW))

        session_start = time.perf_counter()
        correct = 0

        for i, q in enumerate(questions, 1):
            print(f"\n{clr(f'Q{i}/{n}', C.CYAN)}  {clr(q.prompt, C.BOLD)}")
            t0 = time.perf_counter()
            user_in = input("  > ")
            q.time_sec = time.perf_counter() - t0

            if q.check(user_in):
                correct += 1
                print(clr(f"  ✓  {q.time_sec:.2f}s", C.GREEN))
            else:
                print(
                    clr(f"  ✗ correct: {q.answer}  ({q.time_sec:.2f}s)", C.RED)
                )
                if q.hint:
                    print(clr(f"    hint: {q.hint}", C.GREY))

        total_time = time.perf_counter() - session_start
        self.profile.record_session(kind, label, questions, total_time)

        pct = correct / n * 100
        avg = total_time / n
        bar_len = 30
        filled = int(bar_len * correct / n)
        bar = "█" * filled + "░" * (bar_len - filled)

        print()
        print(self.box("RESULT"))
        print(f"  Score: {clr(f'{correct}/{n}', C.BOLD)}  ({pct:.1f}%)")
        print(f"  [{clr(bar, C.GREEN)}]")
        print(f"  Total time: {total_time:.2f}s   Avg/question: {avg:.2f}s")

        if pct == 100:
            print(clr("  Perfect! 🔥", C.GREEN))
        elif pct >= 80:
            print(clr("  Strong. Keep going.", C.GREEN))
        elif pct >= 50:
            print(clr("  Decent — review mistakes.", C.YELLOW))
        else:
            print(clr("  Needs work. Re-read the cheat sheet.", C.RED))

    def meta_menu(self):
        while True:
            print(clr("\n── Meta Alphabet Drill ──", C.BOLD))
            for key, (label, _) in META_MODES.items():
                print(f"  {key}) {label}")
            print("  q) Back to main menu")
            choice = input(clr("Choose: ", C.YELLOW)).strip().lower()

            if choice == "q":
                return
            if choice not in META_MODES:
                print(clr("Invalid choice.", C.RED))
                continue

            label, types = META_MODES[choice]
            try:
                n = int(input("Questions? [default 20]: ").strip() or "20")
            except ValueError:
                n = 20
            try:
                cd = int(input("Cooldown? [default 5]: ").strip() or "5")
            except ValueError:
                cd = 5

            questions = generate_meta_questions(types, n, cooldown=cd)
            self._run_questions(questions, f"meta:{label}", "meta")

    def list_quiz_databases(self):
        QUIZ_DATA_DIR.mkdir(parents=True, exist_ok=True)
        files = sorted(QUIZ_DATA_DIR.glob("*.json"))
        if not files:
            print(clr("No quiz databases in data/quiz_data/.", C.YELLOW))
            return []
        print(clr("\nAvailable quiz databases:", C.BOLD))
        for i, f in enumerate(files, 1):
            print(f"  {i}) {f.name}")
        return files

    def load_quiz_from_json(self, path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except (OSError, json.JSONDecodeError) as e:
            print(clr(f"Failed to load: {e}", C.RED))
            return

        qs = []
        for item in data.get("questions", []):
            qs.append(
                Question(
                    prompt=item["prompt"],
                    answer=str(item["answer"]),
                    hint=item.get("hint", ""),
                    qtype=item.get("type", ""),
                )
            )
        self.questions = qs
        print(clr(f"Loaded {len(qs)} questions from {path.name}", C.GREEN))

    def quiz_menu(self):
        while True:
            print(clr("\n── Quiz ──", C.BOLD))
            print(f"  Loaded: {len(self.questions)} questions")
            print("  1) List quiz databases")
            print("  2) Load a quiz database")
            print("  3) Run loaded quiz")
            print("  q) Back to main menu")
            choice = input(clr("Choose: ", C.YELLOW)).strip().lower()

            if choice == "q":
                return
            if choice == "1":
                self.list_quiz_databases()
            elif choice == "2":
                files = self.list_quiz_databases()
                if not files:
                    continue
                idx = input("Pick number: ").strip()
                try:
                    self.load_quiz_from_json(files[int(idx) - 1])
                except (ValueError, IndexError):
                    print(clr("Invalid selection.", C.RED))
            elif choice == "3":
                if not self.questions:
                    print(clr("No quiz loaded.", C.RED))
                    continue
                self._run_questions(
                    list(self.questions), "quiz:loaded", "quiz"
                )
            else:
                print(clr("Invalid choice.", C.RED))

    def main_menu(self):
        print(clr("\n══ Coding-Decoding Trainer ══", C.BOLD))
        print(f"  User: {clr(self.profile.username, C.CYAN)}")
        print("  1) Meta — alphabet drill")
        print("  2) Quiz")
        print("  3) Profile summary")
        print("  4) Last session")
        print("  q) Quit")
        return input(clr("\nChoose: ", C.YELLOW)).strip().lower()

    def last_session_report(self):
        print(clr("\nWhich profile?", C.BOLD))
        print("  1) Meta   2) Quiz")
        k = input("  > ").strip()
        kind = "meta" if k == "1" else "quiz" if k == "2" else None
        if kind is None:
            print(clr("Invalid.", C.RED))
            return
        s = self.profile.last_session(kind)
        if not s:
            print(clr("No sessions recorded yet.", C.YELLOW))
            return
        print(f"\n{clr('Last', C.BOLD)} {kind}: {s['label']}")
        print(f"  {s['timestamp']}")
        print(f"  Score: {s['correct']}/{s['question_count']}")
        print(
            f"  Total {s['total_time_sec']}s  avg {s['avg_time_sec']}s/question"
        )
        print(clr("  Per-question log (last 5):", C.GREY))
        for pq in s["per_question"][-5:]:
            mark = "✓" if pq["correct"] else "✗"
            print(
                f"    {mark} {pq['prompt']:<40} "
                f"{pq['time_sec']:>6.2f}s  [{pq['qtype']}]"
            )

    def main_loop(self):
        print(self.box("CODING-DECODING CLI TRAINER"))
        while True:
            choice = self.main_menu()
            if choice == "1":
                self.meta_menu()
            elif choice == "2":
                self.quiz_menu()
            elif choice == "3":
                self.profile.summary()
            elif choice == "4":
                self.last_session_report()
            elif choice in ("q", "quit", "exit"):
                print(clr("\nBye! Keep practicing.", C.CYAN))
                return
            else:
                print(clr("Invalid choice.", C.RED))


# ------------------------------------------------------------------
# Entry
# ------------------------------------------------------------------
def main():
    ensure_dirs()
    username = input("Username [default]: ").strip() or "default"
    try:
        CLIUserInterface(username).main_loop()
    except (KeyboardInterrupt, EOFError):
        print(clr("\n\nInterrupted. Bye!", C.CYAN))


if __name__ == "__main__":
    main()
