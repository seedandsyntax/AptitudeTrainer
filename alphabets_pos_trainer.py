"""CLI UI for the aptitude trainer.

Entry point is AptitudeTrainer.py.
"""

import json
import random
import time

import trainer_core as core
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


class CLIUserInterface:
    def __init__(self, username="default"):
        self.profile = core.Profile(username)
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
            print(clr("  Perfect!", C.GREEN))
        elif pct >= 80:
            print(clr("  Strong. Keep going.", C.GREEN))
        elif pct >= 50:
            print(clr("  Decent — review mistakes.", C.YELLOW))
        else:
            print(clr("  Needs work. Re-read the cheat sheet.", C.RED))

    def _ask_common(self):
        try:
            n = int(input("Questions? [default 20]: ").strip() or "20")
        except ValueError:
            n = 20
        try:
            cd = int(input("Cooldown? [default 5]: ").strip() or "5")
        except ValueError:
            cd = 5
        return n, cd

    def _pick_subset(self, keys, labels):
        print("Enter type numbers, comma-separated (e.g. 1,3,5):")
        for i, k in enumerate(keys, 1):
            print(f"  {i}) {labels[k]}")
        raw = input("  > ").strip()
        try:
            idxs = [int(x.strip()) - 1 for x in raw.split(",") if x.strip()]
        except ValueError:
            print(clr("Invalid input.", C.RED))
            return []
        picked = [keys[i] for i in idxs if 0 <= i < len(keys)]
        if not picked:
            print(clr("No valid types selected.", C.RED))
        return picked

    def _pick_registry_subset(self, keys, registry):
        print("Enter type numbers, comma-separated (e.g. 1,5,20):")
        for i, k in enumerate(keys, 1):
            print(f"  {i}) {registry[k][2]}")
        raw = input("  > ").strip()
        try:
            idxs = [int(x.strip()) - 1 for x in raw.split(",") if x.strip()]
        except ValueError:
            print(clr("Invalid input.", C.RED))
            return []
        picked = [keys[i] for i in idxs if 0 <= i < len(keys)]
        if not picked:
            print(clr("No valid types selected.", C.RED))
        return picked

    def _family_menu(self, title, mod, generator, default_n=20):
        while True:
            print(clr(f"\n── {title} ──", C.BOLD))
            keys = list(mod.BUILDERS.keys()) if hasattr(mod, "BUILDERS") \
                else list(mod.GENERATORS.keys())
            labels = mod.LABELS

            for i, k in enumerate(keys, 1):
                print(f"  {i}) {labels[k]}")
            n_all = len(keys)
            print(f"  {n_all + 1}) All types mixed")
            print(f"  {n_all + 2}) Custom subset")
            print("  q) Back")
            choice = input(clr("Choose: ", C.YELLOW)).strip().lower()

            if choice == "q":
                return
            if not choice.isdigit():
                print(clr("Invalid choice.", C.RED))
                continue

            c = int(choice)
            if 1 <= c <= n_all:
                types = [keys[c - 1]]
            elif c == n_all + 1:
                types = keys
            elif c == n_all + 2:
                types = self._pick_subset(keys, labels)
                if not types:
                    continue
            else:
                print(clr("Invalid choice.", C.RED))
                continue

            try:
                n = int(
                    input(f"Questions? [default {default_n}]: ").strip()
                    or str(default_n)
                )
            except ValueError:
                n = default_n

            questions = generator(types, n)
            self._run_questions(
                questions, f"{title}:{','.join(types)}", "meta"
            )

    def meta_menu(self):
        while True:
            print(clr("\n── Meta Training ──", C.BOLD))
            print("   1) Alphabet position drills")
            print("   2) Coding-Decoding drills")
            print("   3) Number Series drills")
            print("   4) Clock drills")
            print("   5) Cube / Cuboid drills")
            print("   6) Blood Relations drills")
            print("   7) Direction Sense drills")
            print("   8) HCF / LCM drills")
            print("   9) Calendar drills")
            print("  10) Percentage drills")
            print("  11) Average drills")
            print("  12) Number System drills")
            print("  13) Venn / Set Theory drills")
            print("  14) Syllogism drills")
            print("  15) Sitting Arrangement drills")
            print("  16) Alphabet Series / Letter Pairs")
            print("  17) Unified mixed drills (any family)")
            print("   q) Back to main menu")
            choice = input(clr("Choose: ", C.YELLOW)).strip().lower()

            if choice == "q":
                return
            if choice == "1":
                self.alphabet_menu()
            elif choice == "2":
                self.coding_menu()
            elif choice == "3":
                self.number_series_menu()
            elif choice == "4":
                self.clock_menu()
            elif choice == "5":
                self.cube_menu()
            elif choice == "6":
                self.blood_menu()
            elif choice == "7":
                self.direction_menu()
            elif choice == "8":
                self.hcf_lcm_menu()
            elif choice == "9":
                self.calendar_menu()
            elif choice == "10":
                self.percentage_menu()
            elif choice == "11":
                self.average_menu()
            elif choice == "12":
                self.number_system_menu()
            elif choice == "13":
                self.venn_menu()
            elif choice == "14":
                self.syllogism_menu()
            elif choice == "15":
                self.sitting_menu()
            elif choice == "16":
                self.alphabet_series_menu()
            elif choice == "17":
                self.mixed_menu()
            else:
                print(clr("Invalid choice.", C.RED))

    def alphabet_menu(self):
        while True:
            print(clr("\n── Alphabet Drills ──", C.BOLD))
            for i, (label, _) in enumerate(core.ALPHABET_MODES, 1):
                print(f"  {i}) {label}")
            print("  q) Back")
            choice = input(clr("Choose: ", C.YELLOW)).strip().lower()

            if choice == "q":
                return
            try:
                idx = int(choice) - 1
                label, types = core.ALPHABET_MODES[idx]
            except (ValueError, IndexError):
                print(clr("Invalid choice.", C.RED))
                continue

            n, cd = self._ask_common()
            questions = core.generate_alphabet_questions(types, n, cooldown=cd)
            self._run_questions(questions, f"alphabet:{label}", "meta")

    def coding_menu(self):
        self._family_menu(
            "Coding-Decoding Drills",
            code_decode_mod,
            core.generate_coding_questions,
            default_n=20,
        )

    def number_series_menu(self):
        self._family_menu(
            "Number Series Drills",
            number_series_mod,
            core.generate_number_series_questions,
            default_n=20,
        )

    def clock_menu(self):
        self._family_menu(
            "Clock Drills",
            clock_mod,
            core.generate_clock_questions,
            default_n=10,
        )

    def cube_menu(self):
        self._family_menu(
            "Cube / Cuboid Drills",
            cube_mod,
            core.generate_cube_questions,
            default_n=20,
        )

    def blood_menu(self):
        self._family_menu(
            "Blood Relations Drills",
            blood_relations_mod,
            core.generate_blood_questions,
            default_n=10,
        )

    def direction_menu(self):
        self._family_menu(
            "Direction Sense Drills",
            direction_mod,
            core.generate_direction_questions,
            default_n=10,
        )

    def hcf_lcm_menu(self):
        self._family_menu(
            "HCF / LCM Drills",
            hcf_lcm_mod,
            core.generate_hcf_lcm_questions,
            default_n=15,
        )

    def calendar_menu(self):
        self._family_menu(
            "Calendar Drills",
            calendar_mod,
            core.generate_calendar_questions,
            default_n=15,
        )

    def percentage_menu(self):
        self._family_menu(
            "Percentage Drills",
            percentage_mod,
            core.generate_percentage_questions,
            default_n=15,
        )

    def average_menu(self):
        self._family_menu(
            "Average Drills",
            average_mod,
            core.generate_average_questions,
            default_n=15,
        )

    def number_system_menu(self):
        self._family_menu(
            "Number System Drills",
            number_system_mod,
            core.generate_number_system_questions,
            default_n=15,
        )

    def venn_menu(self):
        self._family_menu(
            "Venn / Set Theory Drills",
            venn_mod,
            core.generate_venn_questions,
            default_n=15,
        )

    def syllogism_menu(self):
        self._family_menu(
            "Syllogism Drills",
            syllogism_mod,
            core.generate_syllogism_questions,
            default_n=10,
        )

    def sitting_menu(self):
        self._family_menu(
            "Sitting Arrangement Drills",
            sitting_arrangement_mod,
            core.generate_sitting_questions,
            default_n=5,
        )

    def alphabet_series_menu(self):
        self._family_menu(
            "Alphabet Series / Letter Pairs",
            alphabet_series_mod,
            core.generate_alphabet_series_questions,
            default_n=10,
        )

    def mixed_menu(self):
        registry = core.all_types_registry()
        keys = list(registry.keys())

        while True:
            print(clr("\n── Unified Mixed Drills ──", C.BOLD))
            for i, k in enumerate(keys, 1):
                print(f"  {i}) {registry[k][2]}")
            n_all = len(keys)
            print(f"  {n_all + 1}) Everything mixed")
            print(f"  {n_all + 2}) Custom subset")
            print("  q) Back")
            choice = input(clr("Choose: ", C.YELLOW)).strip().lower()

            if choice == "q":
                return

            if not choice.isdigit():
                print(clr("Invalid choice.", C.RED))
                continue

            c = int(choice)
            if 1 <= c <= n_all:
                fq_keys = [keys[c - 1]]
            elif c == n_all + 1:
                fq_keys = keys
            elif c == n_all + 2:
                fq_keys = self._pick_registry_subset(keys, registry)
                if not fq_keys:
                    continue
            else:
                print(clr("Invalid choice.", C.RED))
                continue

            try:
                n = int(input("Questions? [default 20]: ").strip() or "20")
            except ValueError:
                n = 20

            questions = core.generate_mixed_questions(fq_keys, n)
            label = "mixed:" + ",".join(fq_keys)
            self._run_questions(questions, label, "meta")

    def list_quiz_databases(self):
        core.QUIZ_DATA_DIR.mkdir(parents=True, exist_ok=True)
        files = sorted(core.QUIZ_DATA_DIR.glob("*.json"))
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
                core.Question(
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
            print(clr("\n── Custom Quiz Bank ──", C.BOLD))
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
        print(clr("\n══ Aptitude Trainer ══", C.BOLD))
        print(f"  User: {clr(self.profile.username, C.CYAN)}")
        print("  1) Meta training")
        print("  2) Custom quiz bank")
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
        print(self.box("APTITUDE CLI TRAINER"))
        while True:
            choice = self.main_menu()
            if choice == "1":
                self.meta_menu()
            elif choice == "2":
                self.quiz_menu()
            elif choice == "3":
                for line in self.profile.summary_lines():
                    print(line)
            elif choice == "4":
                self.last_session_report()
            elif choice in ("q", "quit", "exit"):
                print(clr("\nBye! Keep practicing.", C.CYAN))
                return
            else:
                print(clr("Invalid choice.", C.RED))
