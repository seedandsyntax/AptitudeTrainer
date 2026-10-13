import json
alphabet_set : str = "abcdefghijklmnopqrstuvwxyz"

# comparitive table creation

dispatch_table: dict[str, int] = {}
temp_pos: int = 0
for letter in alphabet_set:
    temp_pos += 1
    dispatch_table[letter] = temp_pos

class Loader:
    def __init__(self, json_file: str) -> None:
        self.contents: dict
        with open(json_file, 'r', encoding='utf-8') as rf:
            self.contents = json.load(rf)

class Question:
    def __init__(self) -> None:
        label: str
        option_list: list[str]
        correct_opt: list[bool]
        

class CLIUserInterface:
    def __init__(self) -> None:
        loader_obj: Loader
        all_questions: list[Question] = []

    def main_loop(self):
        pass

    def opt_deco(self):
        pass

    def question_deco(self):
        pass

    def box_deco(self):
        pass

    def overall_score(self):
        pass
