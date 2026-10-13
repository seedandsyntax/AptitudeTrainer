"""Entry point for the CLI aptitude trainer."""

import trainer_core as core
from alphabets_pos_trainer import CLIUserInterface, clr, C


def main():
    core.ensure_dirs()
    try:
        username = input("Username [default]: ").strip() or "default"
        CLIUserInterface(username).main_loop()
    except (KeyboardInterrupt, EOFError):
        print(clr("\n\nInterrupted. Bye!", C.CYAN))


if __name__ == "__main__":
    main()
