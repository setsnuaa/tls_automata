# -*- coding：utf-8 -*-
import os


def main():
    with open("D:\\code0\\tls_automata_results\\state_machine\\gnutls\\3.7.0\\TLS12\\automaton.dot", "w+") as f:
        lines = f.readlines()
        lines.insert(1, '__start0 [label="" shape="none"];\n')
        lines.insert(-1, '__start0 -> "0";\n')
        f.writelines(lines)
        # print(len(lines))


if __name__ == "__main__":
    main()
