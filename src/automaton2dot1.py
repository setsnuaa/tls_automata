# -*- coding：utf-8 -*-
import sys
from automata.automata import Automaton, load_automaton_from_file


def main():
    automaton: Automaton = load_automaton_from_file(sys.argv[2])
    with open(sys.argv[3], "w", encoding="utf-8") as dot_file:
        dot_file.write(automaton.dot())


if __name__ == "__main__":
    main()
